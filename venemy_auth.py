import requests
import argparse
import json
import time
from random import randint
import imghdr #used for checking image file types
import os #used for interacting with filesystem

requests.packages.urllib3.disable_warnings()

#Script Arguments
parser = argparse.ArgumentParser(description="Venemy: An Intel Tool For Venmo - Use at your own risk")
parser.add_argument('-u', '--user', required=False, help='Grabs basic info of user')
parser.add_argument('-f', '--friends',required=False,help='Get friends')
parser.add_argument('-t', '--trans',required=False,help="Get transactions of users")
parser.add_argument('-a', '--all',required=False,help="Grab basic info, transactions, and friends of target profile")
parser.add_argument('-c', '--crawl',required=False,help="Crawl one level of friends (foaf) - this is incredibly noisy!!! See README before running")
parser.add_argument('-p', '--pics',required=False,action='store_true',help="Download user's public photos")
args = parser.parse_args()

# Setting up and Making the Web Call
def GetDataFromVenmo(url):
	try:
		user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/66.0'
		api_key = "8466193b179ae7cbfedc94ec38985f946e0905dd4bccb9b0c8912d2df41ff763" #This expires every 30 minutes
		cookies = dict(api_access_token=api_key)
		headers = {'User-Agent': user_agent}
		response = requests.get(url, headers=headers, cookies=cookies,verify=False)# Make web request for that URL and don't verify SSL/TLS certs
		return response

	except Exception as e:
		print('[!]   ERROR - Venmo issue: {}'.format(str(e)))
		exit(1)

#Grab Basic Info for User
def GetBasicInfo(passed_user):
	url = 'https://venmo.com/api/v5/users/{0}'.format(passed_user)
	response = GetDataFromVenmo(url)
	if response.status_code==200:
		data = response.json()
		return data
		
		return user_id
	else:
		print("Mistakes Were Made...")

#Grab the list of friends
def GetFriendList(passed_user):	
	url = 'https://venmo.com/api/v5/users/{0}/friends'.format(passed_user)
	response = GetDataFromVenmo(url)
	data = response.json()
	if response.status_code==200:
		return data
	else:
		print("Mistakes Were Made...")

#Grab a user's transactions
def GetUserTransactions(passed_user):
	url = 'https://venmo.com/api/v5/users/{0}/feed?limit=50'.format(passed_user)
	response = GetDataFromVenmo(url)
	data = response.json()
	if response.status_code==200:
		return data
	else:
		print("Mistakes Were Made...")

#Grab Internal ID for User
def GetInternalId(passed_user):
	url = 'https://venmo.com/api/v5/search?q={0}'.format(passed_user)
	response = GetDataFromVenmo(url)
	if response.status_code==200:
		data = response.json()
		#print(data)
		user_id = data['data'][0]['id']
		return user_id
	else:
		print("Mistakes Were Made...")

#Parse the Facebook ID
def GetFbId(passed_user):
	if "facebook" in passed_user:
		fb_id = passed_user.split("/")[4]
	else:
		fb_id = "N/A"
	return fb_id


#The HTTP headers always have content type of jpeg but some are png and I've even found gif. This checks to make sure our file type is right and saves it accordingly
def file_check(f):
	if imghdr.what(f) == "png":
		os.rename(f,str(f.split('.')[0])+'.png')
	elif imghdr.what(f) == "gif":
		os.rename(f,str(f.split('.')[0])+'.gif')

#Function for making a request to download the profile picture
def get_profile_pic(pic,file_name):
	request = requests.get(pic,verify=False)
	with open(file_name+'.jpg','wb') as f:
		f.write(request.content)
		#file_check(file_name+'.jpg')

def dir_check(user):
	if os.path.isdir('./'+user):
		os.chdir(user)
	else:
		os.mkdir(user)
		os.chdir(user)


######Main#######

#Get basic info on target profile
if args.user:
	user=args.user
	dir_check(user)
	if user.isdigit() is not True: #If the user variable is username and not an internal ID code, go find the internal_id code
		user = GetInternalId(user) #Call function to get internal_Id and assign to user variable
	info = GetBasicInfo(user) #Go find basic info of the target profile
	if info:
		with open(args.user+'.csv','w') as f:
			f.write("user_id,external_id,username,name,date_created,is_business,num_friends,picture_url\n")
			f.write("{0},{1},{2},{3},{4},{5},{6},{7}".format(str(info['id']),str(info['external_id']),info['username'],info['name'],str(info['date_created']),info['is_business'],info['num_friends'],info['picture']))
			if "venmopics" in info['picture'] or "facebook" in info['picture']:
					pic = info['picture']
					get_profile_pic(pic,info['username'])

#Get friends of target profile
if args.friends:
	user = args.friends #We don't have to check for digits here. For whatever reason,
	dir_check(user)
	if user.isdigit() is not True: #If the user variable is username and not an internal ID code, go find the internal_id code
		user = GetInternalId(user)#Call function to get internal_Id and assign to user variable
	friends = GetFriendList(user)
	if args.pics:
		pic_flag=True
	else:
		pic_flag=False
	if friends:
		with open(user+'_friends.csv','w') as f:
			f.write("user,user_id,external_id,username,name,date_created,is_business,picture_url\n") #Write headers for csv file
			for i in friends['data']:
				f.write("{0},{1},{2},{3},{4},{5},{6},{7}\n".format(user,str(i['id']),str(i['external_id']),i['username'],i['name'],str(i['date_created']),i['is_business'],i['picture']))
				if pic_flag:
					if "venmopics" in i['picture'] or "facebook" in i['picture']:
						pic = i['picture']
						get_profile_pic(pic,i['username'])
		for files in os.listdir():
			if files.endswith(".jpg"):
				file_check(files)



#Get transactions of target profile
if args.trans:
	user = args.trans #Take the CLI argument
	dir_check(user)
	if user.isdigit() is not True: #If the user variable is username and not an internal ID code, go find the internal_id code
		user = GetInternalId(user)#Call function to get internal_Id and assign to user variable
	trans = GetUserTransactions(user) #Go find transactions of the target profile
	if trans:
		with open(args.trans+'_trans.csv','w') as f:
			f.write("story_id,updated_time,actor_id,actor_external_id,actor_username,actor_name,actor_date_created,actor_is_business,actor_picture_url,msg_type,target_id,target_extid,target_username\n")
			for i in trans['data']:
				#print (i)
				f.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13}\n".format(str(i['story_id']),i['updated_time'],str(i['actor']['id']),str(i['actor']['external_id']),i['actor']['username'],i['actor']['name'],str(i['actor']['date_created']),i['actor']['is_business'],i['actor']['picture'],i['type'],i['message'],i['transactions'][0]['target']['id'],i['transactions'][0]['target']['external_id'],i['transactions'][0]['target']['username']))

#Do all the things for a target profile
if args.all:
	user = args.all #Take the CLI argument
	dir_check(user)
	print("[+] Data will be output to ./"+args.all+"/")
	if user.isdigit() is not True: #If the user variable is username and not an internal ID code, go find the internal_id code
		user = GetInternalId(user)#Call function to get internal_Id and assign to user variable
	#Go find basic info of the target profile
	print("[+] Gathering user info...") 
	info = GetBasicInfo(user)
	if info:
		with open(args.all+'.csv','w') as f:
			f.write("user,external_id,username,name,date_created,is_business,num_friends,picture_url\n")
			f.write("{0},{1},{2},{3},{4},{5},{6},{7}".format(str(info['id']),str(info['external_id']),info['username'],info['name'],str(info['date_created']),info['is_business'],info['num_friends'],info['picture']))
			if "venmopics" in info['picture'] or "facebook" in info['picture']:
					pic = info['picture']
					get_profile_pic(pic,info['username'])
	#Go find friends of the target profile
	print("[+] Gathering friend info...")
	friends = GetFriendList(user)
	if args.pics:
		pic_flag=True
	else:
		pic_flag=False
	if friends:
		with open(user+'_friends.csv','w') as f:
			f.write("user,user_id,external_id,username,name,date_created,is_business,picture_url\n") #Write headers for csv file
			for i in friends['data']:
				f.write("{0},{1},{2},{3},{4},{5},{6},{7}\n".format(user,str(i['id']),str(i['external_id']),i['username'],i['name'],str(i['date_created']),i['is_business'],i['picture']))
				if pic_flag:
					if "venmopics" in i['picture'] or "facebook" in i['picture']:
						pic = i['picture']
						get_profile_pic(pic,i['username'])
		for files in os.listdir():
			if files.endswith(".jpg"):
				file_check(files)
	#Go find transactions of target profile
	print("[+] Gathering transaction info...")
	trans = GetUserTransactions(user) #Go find transactions of the target profile
	if trans:
		with open(args.all+'_trans.csv','w') as f:
			f.write("story_id,updated_time,actor_id,actor_external_id,actor_username,actor_name,actor_date_created,actor_is_business,actor_picture_url,msg_type,msg,target_id,target_extid,target_username\n")
			for i in trans['data']:
				#print (i)
				f.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13}\n".format(str(i['story_id']),i['updated_time'],str(i['actor']['id']),str(i['actor']['external_id']),i['actor']['username'],i['actor']['name'],str(i['actor']['date_created']),i['actor']['is_business'],i['actor']['picture'],i['type'],i['message'],i['transactions'][0]['target']['id'],i['transactions'][0]['target']['external_id'],i['transactions'][0]['target']['username']))

if args.crawl:
	user = args.crawl
	dir_check(user)
	if user.isdigit() is not True:#If the user variable is username and not an internal ID code, go find the internal_id code
		user = GetInternalId(user) #Call function to get internal_Id and assign to user variable
	friends = GetFriendList(user)
	if friends:
		with open(args.crawl+'_foaf.csv','w') as f:
			f.write("user,user_id,external_id,username,name,date_created,is_business,picture_url\n") #Write headers for csv file
			for i in friends['data']:
				print("Fetching list for "+i['id'])
				foaf = GetFriendList(i['id'])
				#print (foaf)
				if foaf:
					for j in foaf['data']:
						f.write("{0},{1},{2},{3},{4},{5},{6},{7}\n".format(i['id'],str(j['id']),str(j['external_id']),j['username'],j['name'],str(j['date_created']),j['is_business'],j['picture']))
				time.sleep(randint(1,5))
	 
