import requests
import json
import datetime, time
import base64 
from PIL import Image
from io import BytesIO, StringIO
from flask import send_file

my_token = '673014859:AAHA64iWDcXp2-ksYRVsrjZHtSO-9CYmsSM' 
url_base = 'https://api.telegram.org/bot{}/'.format(my_token)

url_smuQueue = 'http://smuqueue.herokuapp.com/getvendor/'

chat_id = 66681185 

########################################################################

url_getUpdates = '{}getupdates'.format(url_base)
url_sendMsg = '{}sendMessage'.format(url_base)
url_sendPhoto = '{}sendPhoto'.format(url_base)


def main():
	last_update_id = None
	while True:
		updates = get_updates(last_update_id)
		if len(updates['result']) > 0:
			last_update_id = get_last_update_id(updates) + 1
			listen_and_reply(updates)
			time.sleep(0.5)

def get_updates(offset = None):
	url_getUpdates = '{}getupdates?timeout=100'.format(url_base)
	if offset:
		url_getUpdates += "&offset={}".format(offset)
	r = requests.get(url = url_getUpdates)
	print(r.json())
	return r.json()

def send_welcome(chat_id):
	params1 = {'chat_id':chat_id,'text':'Which establishment would you like to enquire? \n 1. Teaparty \n 2. Kenboru \n 3. Subway \n 4. B3'}
	r1 = requests.post(url_sendMsg,params1)
	return r1.json()

def non_existent(chat_id):
	params_no={'chat_id':chat_id,'text':'No such establishment in system'}
	r_no = requests.post(url_sendMsg, params_no)
	return r_no.json()

def get_QueueImage(userinput):

	params={'Vendor': userinput}
	r = requests.get(url=url_smuQueue, data=params)
	d_get = r.json()
	
	if d_get[0]['Vendor'] != '':
		try:
			print(d_get)
			
		except Exception as e:
			print('No information as of yet. Please check back soon for any updates!')

		output = queue_img_information # decode the image from value to png file

	return output

def get_Menu(userinput):

	params={'Vendor': userinput}
	r = requests.post(url=url_smuQueue, data=params)
	d_get = r.json()

	if d_get[0]['Vendor'] != '':
		try:
			menu_img_information = d_get[0]['Menu']
			queue_img_information = d_get[0]['Queue_Image']
		except Exception as e:
			print('No information as of yet. Please check back soon for any updates!')
		
		output = [menu_img_information, queue_img_information]
	return output

# def get_Analysis(userinput):

#     params={'Vendor_ID': userinput}
#     r = requests.get(url=url_smuQueue, params=params)
#     d_get = r.json()
	
#     if d_get['response']['Vendor'] != '':
#         try:
#             analysis_img_information = r.json()['response']['Analysis']
#         except Exception as e:
#             print('No information as of yet. Please check back soon for any updates!')

#         output = base64.decodestring(analysis_img_information) # decode the image from value to png file

#     return output

def get_last_update_id(updates):
	update_ids = []
	for update in updates['result']:
		update_ids.append(int(update["update_id"]))
	return max(update_ids)
	
def listen_and_reply(updates):
	for update in updates['result']:
		try:
			userinput = update['message']['text']
			chat_id = update['message']['chat']['id']
			output = get_Menu(userinput)
			img= BytesIO(base64.b64decode(output[0][2:-1]))
			img2= BytesIO(base64.b64decode(output[1][2:-1]))
			sendphoto(img,chat_id)
			sendphoto(img2,chat_id)
		except Exception as e:
			print(e)

def send_msg(output,chat_id):
	params_send = {'chat_id':chat_id,'text':output}
	r = requests.post(url_sendMsg,params_send)
	return r.json()

def sendphoto(output,chat_id):
	files = {'photo' : output}
	data = {"chat_id": chat_id}
	r = requests.post(url_sendPhoto,files=files,data=data)
	return r.json()

send_welcome(chat_id)	
if __name__ == '__main__':
	main()



send_welcome(chat_id)	
listen_and_reply(chat_id)

