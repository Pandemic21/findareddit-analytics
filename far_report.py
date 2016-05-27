import sqlite3
import time

path = '/home/pandemic/Documents/scripts/findareddit/'
conn = sqlite3.connect(path+'far_analytics.db')
c = conn.cursor()

print "Getting mentions..."
c.execute("SELECT * FROM mentions ORDER BY count DESC")

results = c.fetchall()
k = 0
i = 0
report = ''

print "Generating report..."
while k < len(results):
	while i < len(results):
		if results[i][1] != results[k][1]:
			break;
		i = i + 1
	
	count = results[k][1]
	if count == "1":
		report = report + count + " time:\n\n"
	else:
		report = report + count + " times:\n\n"

	while k < i:
		if k + 1 < i:
			report = report + results[k][0] + " - "
		else:
			report = report + results[k][0] + "\n\n"
		k = k + 1
	if k + 1 < len(results):
		report = report + "--------------------------\n\n"
	
print report
filename = "report_" + str(time.strftime("%Y-%m-%d")) + "_" + str(time.strftime("%H-%M-%S") + ".txt")
f = open(path+filename, "a")
f.write(report)
f.close()

droptable = raw_input("Delete old data (y/n)? ")
if droptable.upper() == "Y":
	print "Dropping table..."
	c.execute("DROP TABLE mentions")
	conn.commit()
	print "Creating table..."
	c.execute("CREATE TABLE mentions (subreddit text, count text)")
	conn.commit()
