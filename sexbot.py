#!/usr/bin/env python
#Changelog
# 0.1 Initial Version
# 0.1.1 Correct number of reviews
# 0.1.2 Fixed SSL
# 0.2 Removed [buy] posts
# 0.2.1 Fixed selfposts being ignored in listings
# 0.2.2 Fixed more than 25 listings
# 0.2.3 Fixed listings for usernames starting with a hyphen
# 0.2.4 Bot ignores [rvw] listings
# 0.2.5 Fixed Unicode characters not being matched by regex
# 0.3 message overhaul

version='0.3'

import os
import praw
import feedparser
import MySQLdb
import re
from datetime import datetime
import time

#Definitions
user_agent=version + " /r/SexSells Notification by /u/b0wmz"
from settings import *

#Create connection and auth as bot
r = praw.Reddit(user_agent=user_agent)
r.login(botusername, botpassword)
db = MySQLdb.connect(mysqlhost, mysqluser, mysqlpass, mysqldb)
cur = db.cursor()

def getReviews(username):
	username = str(username)
	s = r.search('flair:"review" ' + username, subreddit)
	counter = 0
	for i in s:
		counter+=1
	return counter

def getListings(username):
	username = str(username)
	if username[0] == '-':
		s = r.search(username[1:] + ' NOT title:[rvw] AND NOT title:[meta]', subreddit=subreddit, sort='new', limit=None)
	else:
		s = r.search('author:' + username + ' ' + 'AND NOT title:[rvw] AND NOT title:[meta]', subreddit=subreddit, sort='new', limit=None)
	counter = 0
	for i in s:
		counter+=1
	return counter

def getFlair(username):
	username = str(username)
	f = r.get_flair(subreddit, username)
	returnstring = 'Undefined'
	print(f['flair_css_class'])
	if f['flair_css_class'] == None:
		return 'Unverified'
	elif f['flair_css_class'] == 'verified':
		return 'Verified Seller'
	elif f['flair_css_class'] == 'trustedseller':
		return 'Trusted Seller'
	elif f['flair_css_class'] == 'trustedbuyer':
		return 'Trusted Buyer'
	else:
		return "None"
def addComment(sub):
	flair = getFlair(sub.author)
	user = r.get_redditor(sub.author)
	days = str(getRegisteredTime(sub.author))
	if flair == "None":
		addmsg = "**Alert!** *This user is unverified, [click here](/r/sexsells/w/tips) for tips on protecting yourself from scammers!*\r\n\r\n"
	else:
		addmsg = ""
	gentime = str(time.strftime("%H:%M:%S EDT %D"))
	msg = ("""###SexSells Stats for /u/""" + str(sub.author) + """\n\r""" + addmsg + """\r\n* Verification: **""" + flair + """** [learn more](/r/sexsells/w/verification)\n\r* Account Age: **""" + days + """** Days | Karma: **""" + str((user.link_karma+user.comment_karma)) + """**\n\r* No. of Listings: **""" + str(getListings(sub.author)) + """** [view](http://www.reddit.com/r/Sexsells/search?q=author%3A""" + str(sub.author) + """ &sort=new&restrict_sr=on) | No. of Reviews: **""" + str(getReviews(sub.author)) + """** [view](http://www.reddit.com/r/Sexsells/search?q=flair%3A%27review%27+""" + str(sub.author) + """&restrict_sr=on&sort=new&t=all)\r\n\r\n---\r\n\r\n[Wiki](/r/sexsells/w/) | [FAQ](/r/sexsells/w/faq) | [Bot Info](/r/sexsells/w/bot) | [Report a Bug](http://reddit.com/message/compose/?to=b0wmz&subject=SexSellsStats Bug&message=The post with a bug is: """ + sub.short_link + """) | [Modmail](http://www.reddit.com/message/compose?to=%2Fr%2FSexsells)\r\n---\n\r^(Version """ + version + """. Generated at: """ + gentime + """)""")
	sub.add_comment(msg)

def getRegisteredTime(user):
	user = r.get_redditor(str(user))
	t = datetime.utcfromtimestamp(user.created_utc)
	days = (datetime.utcnow() - t).days
	return days

feed = feedparser.parse('http://reddit.com/r/' + subreddit + '/.rss')

for i in feed.entries:
	s = i.link.split("/")
	cur.execute("SELECT * FROM seenposts WHERE postID = '" + s[6] + "';")
	print(cur.rowcount)
	if cur.rowcount < 1:
		sub = r.get_submission(i.link)
		reg = re.compile("^\[[METAmetaBUYbuyrvwRVW]+\]") # http://stackoverflow.com/questions/9942594/unicodeencodeerror-ascii-codec-cant-encode-character-u-xa0-in-position-20
		if not reg.match(sub.title.encode('utf-8')):
			print 'does not contain meta'
			addComment(sub)
			cur.execute("INSERT INTO seenposts (postid) VALUES ('" + s[6] + "');")
db.commit()
