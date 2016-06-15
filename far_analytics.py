import praw
import re
import sqlite3
import time
import calendar
import datetime


def get_row_exists(table, column, value):
	c.execute("SELECT count(*) FROM "+table+" WHERE "+column+"=? COLLATE NOCASE", (value,))
	data = c.fetchone()[0]
	if data==0:
		return False
	else:
		return True


def gen_log(data):
	f = open(LOGFILE, 'a')
	datetime =  str(time.strftime("%Y/%m/%d")) + " " + str(time.strftime("%H:%M:%S"))
	f.write(datetime + ": " + data + "\n")
	f.close()
	print datetime + ": " + data


# MAIN ###########################################################################
PATH='/home/pandemic/Documents/scripts/findareddit/'
LOGFILE=PATH+'far_analytics.log'
DB=PATH+"far_analytics.db"
r = praw.Reddit("findareddit analytics by /u/Pandemic21")
query = "r\/\w*" #matches "r/subreddit"
sub = r.get_subreddit('findareddit')
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS mentions (subreddit text, count integer)")
conn.commit()
gen_log("Starting...")

#start time magic
year = time.gmtime().tm_year
mon = time.gmtime().tm_mon
if mon == 1: 
	mon = 13
	year = year-1
days_last_month = calendar.monthrange(year, mon-1)[1]
seconds_last_month = 60*60*24*days_last_month

last_month_epoch = calendar.timegm((year,mon-1,days_last_month+1,0,0,0))
#end time magic

lowest = last_month_epoch-seconds_last_month
results = praw.helpers.submissions_between(r, sub, lowest_timestamp=lowest, highest_timestamp=last_month_epoch)

gen_log("Getting submissions from " + time.strftime('%m-%d-%Y', time.gmtime(lowest)) + " to " + time.strftime('%m-%d-%Y', time.gmtime(last_month_epoch)))
for result in results:
	try:
		gen_log(result.permalink)
	except Exception as e:
		gen_log("Can't permalink, id = " + result.id)
	comments = praw.helpers.flatten_tree(result.comments)
	
	#if any exist, get rid of morecomments object and replace with comment object
	for comment in comments:
		if type(comment) is praw.objects.MoreComments:
			result.replace_more_comments(limit=None, threshold=0)
			comments = praw.helpers.flatten_tree(result.comments)
			break
	
	for comment in comments:
		#if the comment has no subreddit mentions, continue
		results = re.search(query, comment.body)
		if results is None: 
			gen_log(comment.id + " has no subreddit mentions")
			continue
		
		gen_log(comment.id + " has mentions, parsing...")
		mentions = re.findall(query, comment.body)

		#record all subreddit mentions
		for mention in mentions:
			#if subreddit has already been mentioned 
			if get_row_exists('mentions', 'subreddit', mention):
				#increase count
				gen_log(mention + " exists, increasing count...")
				c.execute("SELECT count FROM mentions WHERE subreddit=? COLLATE NOCASE", (mention,))
				count = c.fetchone()[0]
				count = int(count) + 1
				c.execute("UPDATE mentions SET count=? WHERE subreddit=? COLLATE NOCASE", (str(count),mention))
				conn.commit()
				gen_log(mention + " increased to " + str(count))
			else:	
				#if it hasn't been mentioned, add it
				c.execute("INSERT INTO mentions VALUES (?,?)", (mention, '1',))
				conn.commit()
				gen_log(mention + " did not exist, created")

gen_log("Starting report, getting mentions...")
c.execute("SELECT * FROM mentions ORDER BY count DESC")

results = c.fetchall()
k = 0
i = 0
report = ''

gen_log("Generating report...")
while k < len(results):
	while i < len(results):
		if results[i][1] != results[k][1]:
			break;
		i = i + 1
	
	count = results[k][1]
	if count == 1:
		report = report + str(count) + " time:\n\n"
	else:
		report = report + str(count) + " times:\n\n"

	while k < i:
		if k + 1 < i:
			report = report + results[k][0] + " - "
		else:
			report = report + results[k][0] + "\n\n"
		k = k + 1
	if k + 1 < len(results):
		report = report + "--------------------------\n\n"
	
gen_log(report)
filename = "report_" + str(time.strftime("%Y-%m-%d")) + "_" + str(time.strftime("%H-%M-%S") + ".txt")
f = open(PATH+filename, "a")
f.write(report)
f.close()

droptable = raw_input("Delete gathered data (y/n)? ")
if droptable.upper() == "Y":
	gen_log("Dropping table...")
	c.execute("DROP TABLE mentions")
	conn.commit()
	c.execute("CREATE TABLE mentions (subreddit text, count text)")
	conn.commit()
else:
	gen_log("Keeping table")
