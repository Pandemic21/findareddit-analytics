import praw
import time


def gen_log(data):
	f = open(LOGFILE, 'a')
	datetime =  str(time.strftime("%Y/%m/%d")) + " " + str(time.strftime("%H:%M:%S"))
	f.write(datetime + ": " + data + "\n")
	f.close()
	print datetime + ": " + data


### MAIN ##################################################################
LOGFILE="/home/pandemic/Documents/scripts/findareddit/far_comments.log"
REPORTFILE="/home/pandemic/Documents/scripts/findareddit/comments_report_" + str(time.strftime("%Y-%m-%d")) + "_" + str(time.strftime("%H-%M-%S")) + ".txt"
SUBMISSION_TITLE="Commentless submissions for the week of " + time.strftime('%m-%d-%Y', time.gmtime(time.time()-60*60*24*7))
USERNAME=""
PASSWORD=""
r = praw.Reddit('findareddit comment checker /u/Pandemic21')
r.login(USERNAME,PASSWORD,disable_warning=True)

commentless = []
sub = r.get_subreddit('findareddit')
t = time.time()
lowest = t-(60*60*24*7) #7 days in seconds
results = praw.helpers.submissions_between(r, sub, lowest_timestamp=lowest, highest_timestamp=t)

gen_log("Getting submissions from previous week...")
for result in results:
	comments = result.comments
	if len(comments) > 0: continue
	commentless.append(result)

commentless.reverse()

gen_log("Total commentless submissions = " + str(len(commentless)))
report = open(REPORTFILE, 'a')
report.write("|Thread|Date|\n|---|---|\n")

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
