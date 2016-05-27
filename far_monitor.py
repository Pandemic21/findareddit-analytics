import praw
import re
import sqlite3
import time


# get_new_comments
# get_row_exists(table, column, value)
# gen_log(data)


def get_new_comments():
	comments = subreddit.get_comments(sort='new')
	
	for comment in comments:
		#if comment has been parsed already, break
		if get_row_exists('comments', 'id', comment.id):
			gen_log(comment.id + " already parsed, breaking")
			break

		c.execute("INSERT INTO comments VALUES (?)", (comment.id,))
		conn.commit()
		gen_log("Parsing new comment: " + comment.id)

		#if the comment has no subreddit mentions, continue
		results = re.search(query, comment.body)
		if results is None: 
			gen_log(comment.id + " has no subreddit mentions")
			continue
		
		#get all subreddit mentions in comment
		results = re.findall(query, comment.body)
		#record all subreddit mentions
		for result in results:
			#if subreddit has already been mentioned 
			if get_row_exists('mentions', 'subreddit', result):
				#increase count
				gen_log(result + " exists, increasing count...")
				c.execute("SELECT count FROM mentions WHERE subreddit=? COLLATE NOCASE", (result,))
				count = c.fetchone()[0]
				count = int(count) + 1
				c.execute("UPDATE mentions SET count=? WHERE subreddit=? COLLATE NOCASE", (str(count),result))
				conn.commit()
				gen_log(result + " increased to " + str(count))
				return
			#if it hasn't been mentioned, add it
			gen_log(result + " does not exist, creating...")
			c.execute("INSERT INTO mentions VALUES (?,?)", (result, '1',))
			conn.commit()
			gen_log(result + " created")


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

r = praw.Reddit("findareddit analytics by /u/Pandemic21")
subreddit = r.get_subreddit('findareddit')
query = "r\/\w*" #matches "r/subreddit"
LOGFILE='/home/pandemic/Documents/scripts/findareddit/far_analytics.log'
conn = sqlite3.connect('/home/pandemic/Documents/scripts/findareddit/far_analytics.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS mentions (subreddit text, count text)")
c.execute("CREATE TABLE IF NOT EXISTS comments (id text)")
conn.commit()
gen_log("Starting ......................")


while 1:
	get_new_comments()
	time.sleep(60)
