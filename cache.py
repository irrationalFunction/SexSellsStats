#!/usr/bin/env python
import praw
import json
import pickle

#Definitions
user_agent="/r/SexSells Caching by /u/b0wmz"
from settings import *

#Create connection and auth as bot
r = praw.Reddit(user_agent=user_agent)
with open("token", "rb") as handle: # http://stackoverflow.com/a/11027016
	access_information = pickle.loads(handle.read())
r.set_oauth_app_info(oauth_client_id, oauth_client_secret, oauth_redirect_uri)
r.refresh_access_information(access_information['refresh_token'])
cache = {}
cposts = {}

def createCache():
	posts = r.get_subreddit(subreddit).get_new(limit=1000)
	
	try:
		inputfile = open("cache.json", "r")
		cache = json.load(inputfile)
	except IOError:
		print "cache.json doesn't exist, creating"

	try:
		cachedposts = open("cachedposts.json", "r+")
		cposts = json.load(cachedposts)
	except IOError:
		print "cachedposts.json doesn't exist, creating"


	for i in posts:
		if str(i.url) in cposts:
			continue
		else:
			print str(i.url)
		author = str(i.author)
		if author in cache:
			cache[author]+=1
		else:
			cache[author] = 1
		cposts[str(i.url)] = True

	json.dump(cache, open("cache.json", "w+"))
	json.dump(cposts, open("cachedposts.json", "w+"))

createCache()
