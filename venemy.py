import requests, argparse, json, time, os, configparser
from random import randint
from auth_api import AuthenticationApi
from api_client import ApiClient
from api_util import validate_access_token

requests.packages.urllib3.disable_warnings()

#Script Arguments
parser = argparse.ArgumentParser(description="Venemy: An Intel Tool For Venmo - Use at your own risk")
parser.add_argument('-u', '--user', required=False, help='Grabs basic info of user')
parser.add_argument('-f', '--friends',required=False,help='Get friends')
parser.add_argument('-t', '--trans',required=False,help="Get transactions of users")
parser.add_argument('-a', '--all',required=False,help="Grab basic info, transactions, and friends of target's profile and crawl one level of friends")
parser.add_argument('-c', '--crawl',required=False,help="Crawl one level of friends (foaf) - this is incredibly noisy!!! See README before running")
parser.add_argument('-p', '--pics',required=False,action='store_true',help="Download user's public photos")
parser.add_argument('-A', '--auth',required=False,action='store_true',help="Authenticate to the API for an oAuth token")
parser.add_argument('-n', '--noauth',required=False,help="Check if username exists via the web")
parser.add_argument('-b', '--brute-force',required=False,help="Brute Force variation's of person's name")
args = parser.parse_args()

#Grab our configurations from our .ini file
config = configparser.ConfigParser()
config.read('venmo.ini')

#This class was written by mmohades - https://github.com/mmohades/Venmo
class Client(object):

    def __init__(self, access_token: str):
        """
        VenmoAPI Client
        :param access_token: <str> Need access_token to work with the API.
        """
        super().__init__()
        self.__access_token = validate_access_token(access_token=access_token)
        self.__api_client = ApiClient(access_token=access_token)
        self.user = UserApi(self.__api_client)
        #self.__profile = self.user.get_my_profile()
        #self.payment = PaymentApi(profile=self.__profile,api_client=self.__api_client)

    def my_profile(self, force_update=False):
        """
        Get your profile info. It can be cached from the prev time.
        :return:
        """
        if force_update:
            self.__profile = self.user.get_my_profile(force_update=force_update)

        return self.__profile

    def get_access_token(username: str, password: str, device_id: str = None) -> str:
        """
        Log in using your credentials and get an access_token to use in the API
        :param username: <str> Can be username, phone number (without +1) or email address.
        :param password: <str> Account's password
        :param device_id: <str> [optional] A valid device-id.
        :return: <str> access_token
        """
        authn_api = AuthenticationApi(api_client=ApiClient(), device_id=device_id)
        return authn_api.login_with_credentials_cli(username=username, password=password)

    def log_out(access_token) -> bool:
        """
        Revoke your access_token. Log out, in other words.
        :param access_token:
        :return: <bool>
        """
        return AuthenticationApi.log_out(access_token=access_token)


def no_auth(username):
	url = 'https://venmo.com/{0}'.format(username)
	user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
	headers = {'User-Agent':user_agent}
	response = requests.get(url, headers=headers,verify=False)
	if response.status_code==200:
		print("[+] "+username+" Exists - " + url)
	else:
		print("[-] "+username+" Does Not Exists")

def authenticate():
	access_token = Client.get_access_token(username=config['venmo.com']['username'],password=config['venmo.com']['password'])
	venmo = Client(access_token=access_token)

# Setting up and Making the Web Call
def GetDataFromVenmo(url):
	try:
		api_key = config['venmo.com']['api_token']
		user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
		headers = {'User-Agent':user_agent, 'Authorization': 'Bearer '+ api_key}
		response = requests.get(url, headers=headers,verify=False)
		return response

	except Exception as e:
		print('[!]   ERROR - Venmo issue: {}'.format(str(e)))
		exit(1)

#Grab Basic Info for User
def GetBasicInfo(passed_user):
	try:
		url = 'https://api.venmo.com/v1/users/{0}'.format(passed_user)
		response = GetDataFromVenmo(url)
		print(response.json())
		if response.status_code==200:
			data = response.json()
			return data['data']
		elif response.status_code==400:
			print("That user profile doesn't exist - make sure you have it right. If you're trying to find the profile of someone, use the brute force option first")
	except:
		 print(str(e))

#Grab the list of friends
def GetFriendList(passed_user):	
	url = 'https://api.venmo.com/v1/users/{0}/friends?limit=1337'.format(passed_user)
	response = GetDataFromVenmo(url)
	data = response.json()
	if response.status_code==200:
		return data['data']
	else:
		print("Mistakes Were Made...")

#Grab a user's transactions
def GetUserTransactions(passed_user,url):
	if url is None:
		url = 'https://api.venmo.com/v1/stories/target-or-actor/{0}?limit=50'.format(passed_user)
	else:
		url = url
	response = GetDataFromVenmo(url)
	data = response.json()
	if response.status_code==200:
		if data['pagination'] is not None:
			nurl = data['pagination']['next']
		else:
			nurl = None
		return data,nurl
	else:
		print("Mistakes Were Made...")

def Paginate(nurl):
	url = nurl
	response = GetDataFromVenmo(url)
	data = response.json()
	if response.status_code==200:
		if data['pagination'] is not None:
			nurl = data['pagination']['next']
		else:
			nurl = None
		return data,nurl
	else:
		print("Mistakes Were Made...")

#Grab Internal ID for User
def GetInternalId(passed_user):
	url = 'https://api.venmo.com/v1/users/{0}'.format(passed_user)
	response = GetDataFromVenmo(url)
	if response.status_code==200:
		data = response.json()
		user_id = data['data']['id']
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

#Function for making a request to download the profile picture
def get_profile_pic(pic,file_name):
	request = requests.get(pic,verify=False)
	with open(file_name,'wb') as f:
		f.write(request.content)
		#file_check(file_name+'.jpg')

def dir_check(user):
	if os.path.isdir('./'+user):
		os.chdir(user)
	else:
		os.mkdir(user)
		os.chdir(user)

def brute_force(username):
	barray = []
	barray.append(username.replace(' ','')) #UserName
	barray.append(username.replace(' ','-')) #User-Name
	barray.append(username.replace(' ','_')) #User_Name
	barray.append(username[0:1]+username.split(" ")[1]) #UName
	barray.append(username.split(" ")[0]+username.split(" ")[1][0:1]) #UserN
	barray.append(username.split(" ")[1]+username.split(" ")[0]) #NameUser
	barray.append(username.replace(' ','-')+'-1') #User-Name-1
	barray.append(username.replace(' ','-')+'-2') #User-Name-2
	barray.append(username.replace(' ','-')+'-3') #User-Name-3
	barray.append(username.replace(' ','')+'1') #UserName
	barray.append(username.replace(' ','')+'2') #UserName
	barray.append(username.replace(' ','')+'3') #UserName
	for uname in barray:
		no_auth(uname)
		time.sleep(1.5)

######Main#######

if args.auth:
	authenticate()

if args.noauth:
	no_auth(args.noauth)

if args.brute_force:
	brute_force(args.brute_force)

#Get basic info on target profile
if args.user:
	user=args.user
	dir_check(user)
	info = GetBasicInfo(user) #Go find basic info of the target profile
	if info:
		with open(args.user+'.csv','w') as f:
			id = info['id']
			username = info['username']
			display_name = info['display_name']
			friends_count = info['friends_count']
			phone = info['phone']
			date_joined = info['date_joined']
			email = info['email']
			f.write("venmo_id,username,display_name,friends_count,phone,date_joined,email\n")
			f.write("{0},{1},{2},{3},{4},{5},{6}".format(id,username,display_name,friends_count,phone,date_joined,email))
			if "venmopics" in info['profile_picture_url'] or "facebook" in info['profile_picture_url']:
					pic = info['profile_picture_url']
					get_profile_pic(pic,info['username'])

#Get friends of target profile
if args.friends:
	user = args.friends
	dir_check(user)
	#if user.isdigit() is not True: #If the user variable is username and not an internal ID code, go find the internal_id code
	#	user = GetInternalId(user)#Call function to get internal_Id and assign to user variable
	info = GetFriendList(user)
	if args.pics:
		pic_flag=True
	else:
		pic_flag=False
	if info:
		with open(args.friends + '_friends.csv','w') as f:
			f.write("fvalue,venmo_id,username,display_name,friends_count,phone,date_joined,email\n")
			for friend in info:
				fvalue = user
				id = friend['id']
				username = friend['username']
				display_name = friend['display_name']
				friends_count = friend['friends_count']
				phone = friend['phone']
				date_joined = friend['date_joined']
				email = friend['email']
				f.write("{0},{1},{2},{3},{4},{5},{6},{7}\n".format(fvalue,id,username,display_name,friends_count,phone,date_joined,email))
				if pic_flag:
					if "venmopics" in friend['profile_picture_url'] or "facebook" in friend['profile_picture_url']:
						pic = friend['profile_picture_url']
						get_profile_pic(pic,friend['username'])


#Get transactions of target profile
if args.trans:
	user = args.trans #Take the CLI argument
	dir_check(user)
	if user.isdigit() is not True: #If the user variable is username and not an internal ID code, go find the internal_id code
		user = GetInternalId(user)#Call function to get internal_Id and assign to user variable
	nurl = None
	trans,nurl = GetUserTransactions(user,nurl) #Go find transactions of the target profile
	if trans:
		with open(args.trans+'_trans.csv','w') as f:
			#f.write(str(trans))
			f.write("id,date_updated,app_used,payee,payor,item\n")
			for i in trans['data']:
				try:
					id = str(i['id'])
					dt = str(i['date_updated'])
					app = i['app']['description']
					payee = i['payment']['target']['user']['username']
					payor = i['payment']['actor']['username']
					note = i['payment']['note']
					f.write("{0},{1},{2},{3},{4},{5}\n".format(id,dt,app,payee,payor,note))
				except:
					pass
	while nurl is not None:
		data,nurl = Paginate(nurl)
		if nurl is None:
			break
		else:
			with open(args.trans+'_trans.csv','a') as f:
				for i in data['data']:
					try:
						id = str(i['id'])
						dt = str(i['date_updated'])
						app = i['app']['description']
						payee = i['payment']['target']['user']['username']
						payor = i['payment']['actor']['username']
						note = i['payment']['note']
						f.write("{0},{1},{2},{3},{4},{5}\n".format(id,dt,app,payee,payor,note))
					except:
						pass
		time.sleep(randint(1,5))

#Do all the things for a target profile
if args.all:
	user=args.all
	dir_check(user)
	print("[+] Gathering User info...")
	info = GetBasicInfo(user) #Go find basic info of the target profile
	if info:
		with open(user+'.csv','w') as f:
			f.write("venmo_id,username,display_name,friends_count,phone,date_joined,email\n")
			id = info['id']
			username = info['username']
			display_name = info['display_name']
			friends_count = info['friends_count']
			phone = info['phone']
			date_joined = info['date_joined']
			email = info['email']
			f.write("{0},{1},{2},{3},{4},{5},{6}".format(id,username,display_name,friends_count,phone,date_joined,email))
			if "venmopics" in info['profile_picture_url'] or "facebook" in info['profile_picture_url']:
					pic = info['profile_picture_url']
					get_profile_pic(pic,info['username'])
	#Go find friends of the target profile
	print("[+] Gathering friend info...")
	info = GetFriendList(user)
	if args.pics:
		pic_flag=True
	else:
		pic_flag=False
	if info:
		with open(user + '_friends.csv','w') as f:
			f.write("fvalue,venmo_id,username,display_name,friends_count,phone,date_joined,email\n")
			for friend in info:
				fvalue = user
				id = friend['id']
				username = friend['username']
				display_name = friend['display_name']
				friends_count = friend['friends_count']
				phone = friend['phone']
				date_joined = friend['date_joined']
				email = friend['email']
				f.write("{0},{1},{2},{3},{4},{5},{6},{7}\n".format(fvalue,id,username,display_name,friends_count,phone,date_joined,email))
				if pic_flag:
					if "venmopics" in friend['profile_picture_url'] or "facebook" in friend['profile_picture_url']:
						pic = friend['profile_picture_url']
						get_profile_pic(pic,friend['username'])
	#Go find transactions of target profile
	print("[+] Gathering transaction info...")
	time.sleep(randint(1,5))
	if user.isdigit() is not True: #If the user variable is username and not an internal ID code, go find the internal_id code
		duser = GetInternalId(user)#Call function to get internal_Id and assign to user variable
	nurl = None
	trans,nurl = GetUserTransactions(duser,nurl) #Go find transactions of the target profile
	if trans:
		with open(args.all+'_trans.csv','w') as f:
			#f.write(str(trans))
			f.write("id,date_updated,app_used,payee,payor,item\n")
			for i in trans['data']:
				try:
					id = str(i['id'])
					dt = str(i['date_updated'])
					app = i['app']['description']
					payee = i['payment']['target']['user']['username']
					payor = i['payment']['actor']['username']
					note = i['payment']['note']
					f.write("{0},{1},{2},{3},{4},{5}\n".format(id,dt,app,payee,payor,note))
				except:
					pass
	while nurl is not None:
		data,nurl = Paginate(nurl)
		if nurl is None:
			break
		else:
			with open(args.all+'_trans.csv','a') as f:
				for i in data['data']:
					try:
						id = str(i['id'])
						dt = str(i['date_updated'])
						app = i['app']['description']
						payee = i['payment']['target']['user']['username']
						payor = i['payment']['actor']['username']
						note = i['payment']['note']
						f.write("{0},{1},{2},{3},{4},{5}\n".format(id,dt,app,payee,payor,note))
					except:
						pass
		time.sleep(randint(1,5))
	print("[+] Done! Info located at " + os.getcwd())

if args.crawl:
	user = args.crawl
	dir_check(user)
	if user.isdigit() is not True:#If the user variable is username and not an internal ID code, go find the internal_id code
		user = GetInternalId(user) #Call function to get internal_Id and assign to user variable
	friends = GetFriendList(user)
	if friends:
		with open(args.crawl+'_foaf.csv','w') as f:
			f.write("fvalue,venmo_id,username,display_name,friends_count,phone,date_joined,email\n")
			for i in friends:
				print("Fetching list for "+i['id'])
				foaf = GetFriendList(i['id'])
				#print (foaf)
				if foaf:
					for friend in foaf:
						fvalue = user
						id = friend['id']
						username = friend['username']
						display_name = friend['display_name']
						friends_count = friend['friends_count']
						phone = friend['phone']
						date_joined = friend['date_joined']
						email = friend['email']
						f.write("{0},{1},{2},{3},{4},{5},{6},{7}\n".format(fvalue,id,username,display_name,friends_count,phone,date_joined,email))
				time.sleep(randint(1,5))
