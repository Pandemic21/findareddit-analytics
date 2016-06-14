import praw
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-s', dest="lowest", help="Start date (YYYY-MM-DD)")
parser.add_argument('-e', dest="highest", help="End date (YYYY-MM-DD)")

def convert_date_to_time(a):
	try: 
		return int(time.mktime(time.strptime(a, '%Y-%m-%d')))
	except Exception as e:
		gen_log("Invalid date format for argument, valid format is YYYY-MM-DD")
		gen_log(str(e))
		exit()	

def check_args():
	args = parser.parse_args()
	#if -e was passed, convert it to epoch. Else, use current time
	if args.highest is not None:
		highest = convert_date_to_time(args.highest)
	else:
		highest = int(time.time())
	#if -s was passed, convert it to epoch. Else, use 7 days previous to end date
	if args.lowest is not None: 	
		lowest = convert_date_to_time(args.lowest)
	else: 
		lowest = int(highest-(60*60*24*7))
	if args.highest < args.lowest:
		gen_log("ERROR: Start date is after end date. The arguments are likely flipped.")
		exit()
	return lowest, highest

def gen_log(data):
	f = open(LOGFILE, 'a')
	datetime =  str(time.strftime("%Y/%m/%d")) + " " + str(time.strftime("%H:%M:%S"))
	f.write(datetime + ": " + data + "\n")
	f.close()
	print datetime + ": " + data


### MAIN ##################################################################
LOGFILE="/home/pandemic/Documents/scripts/far_comments.log"
times = check_args()
REPORTFILE="/home/pandemic/Documents/scripts/comments_report_" + str(time.strftime("%Y-%m-%d")) + "_" + str(time.strftime("%H-%M-%S")) + ".txt"
SUBMISSION_TITLE="Commentless submissions between " + time.strftime('%m-%d-%Y', time.gmtime(times[0])) + " and " + time.strftime('%m-%d-%Y', time.gmtime(times[1]))
USERNAME=""
PASSWORD=""
r = praw.Reddit('findareddit comment checker /u/Pandemic21')
r.login(USERNAME,PASSWORD,disable_warning=True)

commentless = []
sub = r.get_subreddit('findareddit')

results = praw.helpers.submissions_between(r, sub, lowest_timestamp=times[0], highest_timestamp=times[1])

gen_log("Getting submissions between " + time.strftime('%m-%d-%Y', time.gmtime(times[0])) + " and " + time.strftime('%m-%d-%Y', time.gmtime(times[1])))
total = 0
unanswered = 0
for result in results:
	total = total + 1
	comments = result.comments
	if len(comments) > 0: continue
	commentless.append(result)
	unanswered = unanswered + 1

commentless.reverse()

gen_log("Total commentless submissions = " + str(len(commentless)))
report = open(REPORTFILE, 'a')
preamble = "Welcome to our new weekly thread where we list all the submissions this week that haven't received any comments! Please **help us out** by going through some of these submissions and trying to answer their requests. The more that get removed from this list, the better we help the whole community!\n\n#Total number of commentless submissions: " + str(unanswered) + " (" + str(int(float(unanswered)/total*100)) + "% of all submissions this week)\n\n"
report.write(preamble + "|Thread|Date|\n|---|---|\n")

gen_log("Generating report...")
for result in commentless:
	data = "|[" + result.title + "](" + result.permalink + ")|" + time.strftime('%m-%d-%Y', time.gmtime(result.created_utc)) + "|"
	report.write(data + "\n")

report.close()
report = open(REPORTFILE, 'r')
data = report.read()
gen_log("Report generated: " + REPORTFILE)

post = r.submit(sub, SUBMISSION_TITLE, text=data)
post.sticky()

gen_log("Submission = " + post.permalink)
