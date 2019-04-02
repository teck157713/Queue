import requests
import json
import datetime
import time

my_token = '848142865:AAF-tFHYZz94LCjoWchZ_7gx7zYrmno5RH8' 
url_base = 'https://api.telegram.org/bot{}/'.format(my_token)
website = 'https://smuqueue.appspot.com'

url_getMe = '{}getme'.format(url_base)
url_getUpdates = '{}getupdates'.format(url_base)
url_sendMsg = '{}sendMessage'.format(url_base)
url_editMsgText = '{}editMessageText'.format(url_base)
url_delMsg = '{}deleteMessage'.format(url_base)
url_getFile = '{}getFile'.format(url_base)

url_sendPhoto = '{}sendPhoto'.format(url_base)





#################### Define Funcitons START ##############################
def print_pretty_json(json_object):
    print(json.dumps(json_object, indent=2, sort_keys=True))
    return

def send_msg(text,chat_id,reply_markup=None):
    if reply_markup:
        params_send = {'chat_id':chat_id,'text':text,'reply_markup':json.dumps(reply_markup)}
    else:
        params_send = {'chat_id':chat_id,'text':text}
    r = requests.post(url_sendMsg,params_send)
    return

def send_photo(chat_id, photo):
    params_send = {'chat_id':chat_id, 'photo':photo}
    r = requests.post(url_sendPhoto,params_send)
    return r.json()

def get_file_path(file_id):
    params = {'file_id' : file_id}
    r = requests.get(url_getFile, params)
    return r.json()['result']['file_path']

def download_file(file_path):
    url = 'https://api.telegram.org/file/bot{}/{}'.format(my_token,file_path)
    r = requests.get(url)
    return r

def post_new_vendor(vendor_name):
    params = {'Vendor' : vendor_name}
    r = requests.post(website + '{}'.format('/getvendor/'), params)
    return r.json()

def put_new_queue_image(vendor_name, image):
    params = {'updated_queue': image}
    r = requests.put(website + '/{}'.format(vendor_name), params)
    return r.json()

#################### Define Funcitons END ##############################



#################### Execution of Codes START ##############################

chat_id = 398491673

# get chat_id
updates = requests.get(url = url_getUpdates).json()

chat_id = updates["result"][-1]["message"]["chat"]["id"]


wel_text = 'Hi! Welcome to SMUderQs! What do you wanna do today?'
keyboard = [["New Vendor"], ["New Queue Image"]]
reply_markup = {"keyboard":keyboard, "one_time_keyboard":True}

# send welcoming message
send_msg(wel_text,chat_id,reply_markup)

############## define the loop ################

message_id = 0

while True:

    # run every 3 secs
    #time.sleep(3)
    
    updates = requests.get(url = url_getUpdates).json()
    last_message_id = updates['result'][-1]['message']['message_id']
    chat_id = updates["result"][-1]["message"]["chat"]["id"]

    if last_message_id > message_id:
        message_id = last_message_id
        text = updates["result"][-1]["message"]["text"]
        
        if text == 'New Vendor':
            msg_txt = 'Please type in the name of new vendor.'
            send_msg(msg_txt,chat_id)

            while True:

                # run every 2 secs
                #time.sleep(2)
                
                updates = requests.get(url = url_getUpdates).json()
                last_message_id = updates['result'][-1]['message']['message_id']
                text = updates["result"][-1]["message"]["text"]
                chat_id = updates["result"][-1]["message"]["chat"]["id"]
                
                if last_message_id > message_id:
                    message_id = last_message_id
                    
                    try:
                        new_vendor_name = updates['result'][-1]['message']['text']

                        
                        # execute posting
                        post_new_vendor(new_vendor_name)
                        
                        send_msg('New Vendor Successfully input',chat_id)
                        
                        # break loop
                        break
                    
                    except:
                        send_msg('Invalid input', chat_id)
                        break

            # send welcoming message
            send_msg(wel_text,chat_id,reply_markup)

        elif text == 'New Queue Image':
            msg_txt = 'Please send in the image with the name of vendor.'
            send_msg(msg_txt,chat_id)

            while True:
                
                # run every 2 secs
                #time.sleep(2)
                
                updates = requests.get(url = url_getUpdates).json()
                last_message_id = updates['result'][-1]['message']['message_id']
                chat_id = updates["result"][-1]["message"]["chat"]["id"]
                
                if last_message_id > message_id:
                    message_id = last_message_id
                    try:
                        vendor_name = updates['result'][-1]['message']['caption']
                        queue_image_file_id = updates['result'][-1]['message']['photo'][-1]['file_id']
                        queue_image_path = get_file_path(queue_image_file_id)

                        
                        
                        # it will download the file instead of converting to multipart form data
                        download_file(queue_image_path)

                        # pls change the image field after converting to form data
                        put_new_queue_image(vendor_name, image)
                        
                        send_msg('New Queue Image Successfully input',chat_id)
                        break

                    except:
                        send_msg('Invalid input', chat_id)
                        break
                    
            # send welcoming message
            send_msg(wel_text,chat_id,reply_markup)
            
            
        else:

            send_msg('Invalid input', chat_id)
            # send welcoming message
            send_msg(wel_text,chat_id,reply_markup)
                
#################### Execution of Codes END ##############################



#################### RANDOM CODES START ##############################################
'''
r = requests.get(url = url_getUpdates)
#print(print_pretty_json(r.json()))

params = {}
updates = []

text = 'Hi! Welcome to SMUderQs! What do you wanna do today?'
keyboard = [["New Vendor"], ["New Queue Image"]]
reply_markup = {"keyboard":keyboard, "one_time_keyboard":True}

#print(reply_markup)
#print(json.dumps(reply_markup))

send_msg(text,chat_id,reply_markup)

#send_msg('lala',chat_id)

updates = requests.get(url = url_getUpdates).json()
last_message_id = updates['result'][-1]['message']['message_id']
text = updates["result"][-1]["message"]["text"]
chat_id = updates["result"][-1]["message"]["chat"]["id"]

if text == 'New Vendor':
    msg_txt = 'Please type in the name of new vendor.'
    send_msg(msg_txt,chat_id)
    if updates['result'][-1]['message']['message_id'] > last_message_id:
        new_vendor_name = updates['result'][-1]['message']['text']
        post_new_vendor(new_vendor_name)

elif text == 'New Queue Image'：
    msg_txt = 'Please send in the image with the name of vendor.'
    send_msg(msg_txt,chat_id)
    if updates['result'][-1]['message']['message_id'] > last_message_id:
        vendor_name = updates['result'][-1]['message']['caption']
        queue_image_file_id = updates['result'][-1]['message']['photo'][-1]['file_id']
        queue_image_path = get_file_path(queue_image_file_id)

        # it will download the file instead of converting to multipart form data
        download_file(queue_image_path)

        # pls change the image field after converting to form data
        put_new_queue_image(vendor_name, image)

else:
    msg_txt = 'Invalid input.'
    send_msg(msg_txt,chat_id)
        
    


r = requests.get(url = url_getUpdates)
print(print_pretty_json(r.json()))

#send_photo(chat_id, "AgADBQADhagxG7ByAAFVgDBiOtk-a6isV9syAARAqYakfeGH4Z_GBAABAg")

get_file_path("AgADBQADhagxG7ByAAFVgDBiOtk-a6isV9syAARAqYakfeGH4Z_GBAABAg")

x = download_file(get_file_path("AgADBQADhagxG7ByAAFVgDBiOtk-a6isV9syAARAqYakfeGH4Z_GBAABAg"))
'''
#################### RANDOM CODES END ##############################################

