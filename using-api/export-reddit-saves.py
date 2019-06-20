#!/usr/bin/env python

"""
This Python script uses the Reddit API to store your saved items on Reddit in a .csv file within the same directory.

Obtain your Reddit API App ID and App Secret from https://www.reddit.com/prefs/apps/ 

Select application type as script

Note: Ensure that this script has sufficient permissions to write to its directory for CSV export to work
"""

import requests
import csv
import os.path
import html.parser

# Configure user credentials
USERNAME = 'username_here'
PASSWORD = 'password_here'
APPID = 'appid_here'
APPSECRET = 'appsecret_here'

# Write line to file
def write_to_file(valueArray):
	filename = 'redditsaves_' + USERNAME + '.csv'
	with open(filename, 'a+') as fileExport:
		redditCSVWriter = csv.writer(fileExport, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		redditCSVWriter.writerow(valueArray)

# Function checks if the save file exists then deletes it first
def delete_existing_file():
	filename = 'redditsaves_' + USERNAME + '.csv'
	if os.path.exists(filename) == True:
		os.remove(filename)

# Requesting OAuth Reddit token
base_url = 'https://www.reddit.com/'
data = {'grant_type': 'password', 'username': USERNAME, 'password': PASSWORD}
auth = requests.auth.HTTPBasicAuth(APPID, APPSECRET)

r = requests.post(base_url + 'api/v1/access_token',
									data=data,
									headers={'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'},
									auth=auth)
d = r.json()
token = 'bearer ' + d['access_token']

# Start obtaining authenticated users Reddit saves if authorised
base_url = 'https://oauth.reddit.com'

headers = {'Authorization' : token, 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
initialResponse = requests.get(base_url + '/api/v1/me', headers=headers)

# If the Oauth response works, start looking at saved posts
if initialResponse.status_code == 200:
	# Check if file exists
	delete_existing_file()

	# Initialise csv file with headers
	csvHeader = ['Title','Comment body','Subreddit','URL','Permalink','Fullname','Type']
	write_to_file(csvHeader)

	# Get first batch of saved posts
	savedPosts = requests.get(base_url + '/user/' + USERNAME + '/saved', headers=headers).json()

	postCounter = 0 # Total counter quoted by Reddit
	counter = 0 # Total counter of CSV lines saved
	
	# While the next page feature is being returned by Reddit, keep going until it is not returned
	while (savedPosts['data']['after'] != None):
		for i in range(len(savedPosts['data']['children'])):

			# If save data is a reddit post
			if (savedPosts['data']['children'][i]['kind'] == "t3"):
				# Write data into an array to write in as CSV later
				# CSV Structure for type post = title, *bodyempty*, subreddit, url, permalink, link_id, type(post)
				postDataArray = [
					html.unescape(savedPosts['data']['children'][i]['data']['title']), # Unescape certain symbols such as < & >
					"",
					savedPosts['data']['children'][i]['data']['subreddit'],
					savedPosts['data']['children'][i]['data']['url'],
					"https://www.reddit.com" + savedPosts['data']['children'][i]['data']['permalink'],
					savedPosts['data']['children'][i]['data']['name'],
					"Post"
				]

				# Write array to CSV
				write_to_file(postDataArray)

				counter += 1

				# Update situation on console
				print('Posts saved: %d\r'%(counter), end="")

			# If save data is a reddit comment
			elif (savedPosts['data']['children'][i]['kind'] == "t1"):
				# Write data into an array to write in as CSV later
				# CSV Structure for type comment = link_title, body, subreddit, *urlempty*, permalink, *linkidempty*, type(comment)
				postDataArray = [
					html.unescape(savedPosts['data']['children'][i]['data']['link_title']),
					html.unescape(savedPosts['data']['children'][i]['data']['body']),
					savedPosts['data']['children'][i]['data']['subreddit'],
					"",
					"https://www.reddit.com" + savedPosts['data']['children'][i]['data']['permalink'],
					savedPosts['data']['children'][i]['data']['name'],
					"Comment"
				]

				# Write array to CSV
				write_to_file(postDataArray)

				counter += 1

				# Update situation on console
				print('Posts saved: %d\r'%(counter), end="")

		postCounter += savedPosts['data']['dist']
		
		# Retrieve more saved posts
		savedPosts = requests.get(base_url + '/user/' + USERNAME + '/saved/?after=' + savedPosts['data']['after'] , headers=headers).json()
	
	print('\nExport completed, ' + str(postCounter) + ' posts saved.')
	

