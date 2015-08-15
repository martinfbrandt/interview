import base64
import requests
import json
from alchemyapi import AlchemyAPI
# get bearer token for application only requests

class GetData:
	def __init__(self):
		#self.GetTwitterData()
		self.GetStackOverflowData()
	

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
	
	def GetTwitterData(self):
		bearer_tok=self.GetTwitterAuthorization()
		if bearer_tok != False:
			searchurl="https://api.twitter.com/1.1/search/tweets.json?q=alchemyapi"
			headerSearch= {
			'Authorization':'Bearer {}'.format(bearer_tok),
			'Accept-Encoding':'gzip'

			}
			totalResponses=[]
			payload={'count':'100'}
			l=1
			while(True):
				l=l+1
				response2=requests.get(searchurl,headers=headerSearch,params=payload)
				responses=response2.json()
				for status in  responses['statuses']:
					if status['retweeted']!=True:

						 totalResponses.append((status['text'].encode('utf-8'),status['retweet_count']))
				if len(responses['statuses'])<100 or l==7:
					break

			i=1
			for tweet in totalResponses:
				i=i+1
				print i,tweet[0],'\n'


	def GetStackOverflowData(self):
		allQuestions=[]
		stackURL='https://api.stackexchange.com/2.2/search?order=desc&sort=activity&intitle=alchemyapi&site=stackoverflow'
		k=0
		while(True):
			responseStackO = requests.get(stackURL)
			k=k+1
			for item in responseStackO.json()['items']:
				allQuestions.append( [item['tags'],item['title'],item['link']])
			if k>4: 
				break
		questionIDs=[]

		alchemyapi = AlchemyAPI()

		text=''
		for question in allQuestions:
			res=alchemyapi.text('url',question[2])
			text= text+'\n'+ res['text'].encode('utf-8')
	

		res2=alchemyapi.relations('text',text)

		for relation in res2['relations']:
			if relation['subject']['text']=='I':
				try: print relation['action']['text'],' ',relation['object']['text']
				except:continue


data=GetData()


