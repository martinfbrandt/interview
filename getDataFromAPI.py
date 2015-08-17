import base64
import requests
import json
from alchemyapi import AlchemyAPI
# get bearer token for application only requests
import pymongo
from pymongo import MongoClient


class GetData:
	def __init__(self):
		alchemyapi = AlchemyAPI()
		db=self.ConnectToMongo()


		#self.GetTwitterData(alchemyapi,db)
		self.GetStackOverflowData(alchemyapi,db)
		

	def GetTwitterAuthorization(self):
		bearer_token_credentials = base64.urlsafe_b64encode(
		    '{}:{}'.format("HsIUELpN1MMYVVRBlf0LZZb7M", "VcNQ0ICdveyWwETJ8lNdSLeLnOFALef59bU02Vuxu74UfA2Ej1").encode('ascii')).decode('ascii')
		url = 'https://api.twitter.com/oauth2/token'
		headers = {
		    'Authorization': 'Basic {}'.format(bearer_token_credentials),
		    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
		}
		data = 'grant_type=client_credentials'
		response = requests.post(url, headers=headers, data=data)
		response_data = response.json()
		if response_data['token_type'] == 'bearer':
		    bearer_token = response_data['access_token']
		    return bearer_token
		else:
		    raise RuntimeError('unexpected token type: {}'.format(response_data['token_type']))
		    return False
	
	def GetTwitterData(self,alchemyapi,db):
		listofIDs=[]
		tweetStore=db.tweets
		result=tweetStore.remove()
		bearer_tok=self.GetTwitterAuthorization()
		if bearer_tok != False:
			
			searchurl="https://api.twitter.com/1.1/search/tweets.json"
			next_url=''
			headerSearch= {
			'Authorization':'Bearer {}'.format(bearer_tok),
			'Accept-Encoding':'gzip'

			}
			
			payload={'count':'100','q':'alchemyapi'}
			l=1
			while(True):
				l=l+1
				
				if next_url:
					response2=requests.get(searchurl+next_url,headers=headerSearch)
				else:
					
					response2=requests.get(searchurl,headers=headerSearch,params=payload)
				responses=response2.json()
				if 'next_results' in responses['search_metadata']:

					next_url=responses['search_metadata']['next_results']
				else: 
					break
				tweets=[]
				for status in  responses['statuses']:
					if status['id'] not in listofIDs:
						#craete tweet object
						stat=status['text'].encode('utf-8')
						if stat[:3]!= 'RT ':
							comboresponse=alchemyapi.combined('text', stat)
							relationResponse=alchemyapi.relations('text',stat)
							tweet=comboresponse
							tweet['id']=status['id']
							tweet['text']=stat
							tweet['relations']=relationResponse['relations']
							tweets.append(tweet)
				result=tweetStore.insert_many(tweets)
			# tweetStore.distinct('keywords.text')
				
	def ConnectToMongo(self):
		client = MongoClient('mongodb://martin:mfbmfb@ds033123.mongolab.com:33123/twitstackdata')
		db=client['twitstackdata']
		return db

	def GetStackOverflowData(self,alchemyapi,db):
		allQuestions=[]
		
		stackStore=db.stackOs
		result=stackStore.remove()
		page=1
		alchemyapi = AlchemyAPI()
		while(True):
			stackURL='https://api.stackexchange.com/2.2/search?page='+str(page)+'&order=desc&sort=activity&tagged=alchemyapi&site=stackoverflow&filter=withbody'
			responseStackO = requests.get(stackURL)
			response=responseStackO.json()

			if response['has_more']==True:
				page=page+1
			else: break
			text=''
			posts=[]
			for item in response['items']:
				try:
					postText=alchemyapi.text('html',item['body'])
					postText=postText['text'].encode('utf-8')
				except: postText=''
				
				
				post = alchemyapi.combined('text',item['title']+'\n'+postText)
				postRelation=alchemyapi.relations('text',item['title'])	
				
				post['text']=postText
				post['relations']=postRelation['relations']
				post['id']=item['question_id']	
				posts.append(post)
			stackStore.insert_many(posts)
	def printResponse(self,res2):
		for relation in self.res2['relations']:
			if relation['subject']['text']=='I':
				try: print relation['action']['text'],' ',relation['object']['text']
				except:continue
				

	

data=GetData()


