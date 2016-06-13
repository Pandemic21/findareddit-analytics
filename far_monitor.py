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

LOGFILE='c:\\users\\caldw\\desktop\\far_analytics.log'
r = praw.Reddit("findareddit analytics by /u/Pandemic21")
query = "r\/\w*" #matches "r/subreddit"
sub = r.get_subreddit('findareddit')
conn = sqlite3.connect('c:\\users\\caldw\\desktop\\far_analytics.db')
c = conn.cursor()
#TODO delete this
c.execute("CREATE TABLE IF NOT EXISTS mentions (subreddit text, count integer)")
conn.commit()
gen_log("Starting ......................")

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
print lowest
print last_month_epoch


results = praw.helpers.submissions_between(r, sub, lowest_timestamp=lowest, highest_timestamp=last_month_epoch)

gen_log("Getting submissions from previous month...")
for result in results:
	try:
		gen_log(str(result.permalink))
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
		
		#get all subreddit mentions in comment
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
