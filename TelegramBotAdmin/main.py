########################################################################
# ay18t2-smt203-asm-01
# team members:
#               1. Fabian Toh
#               2. Khu Giem Teck
########################################################################

import requests
import json
import datetime, time 
import math

########################################################################
# global variables 
########################################################################

my_token = '734178160:AAHcWCOKZJ-ReBJ6lift2KsU--vB9-x2uvs' # put your secret Telegram token here 
# bot name is @FT_KGT_A1_bot
url_base = 'https://api.telegram.org/bot{}/'.format(my_token)

url_busArrival = 'http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2'
# if you read page 6 of the LTA data mall, notice that ALL requests to the data 
# mall must include headers, for example: 
headers = {
                'AccountKey': 'TkCjPqovTzyUk9Al1Z1l7g==', # enter your account key here (check your email when you sign up in LTA data mall) 
                'accept': 'application/json'
}

def print_pretty_json(json_object):
                print(json.dumps(json_object, indent=2, sort_keys=True))
                return 

chat_id = '' # please type in your Telegram user chat id here  

########################################################################
# Telegram method URLs
########################################################################

url_getUpdates = '{}getupdates'.format(url_base)
url_sendMsg = '{}sendMessage'.format(url_base)

# write your code below
# you may wish to break your code into different functions,
# for readability and modularity (which allows for code reuse)
# some suggested functions are below as a guide; 
# however, you are free to change any of the functions below 

def send_welcome(chat_id):
        parameters = {'chat_id':chat_id, 'text':'Welcome!!\n\nTo begin, please enter a bus stop code!\ne.g.  04222 \n\nIf you want a specific bus service please enter bustop code,bus service number \n e.g.  04222,NR5'}
        send_welcome_msg = requests.post(url_sendMsg,parameters)
        return send_welcome_msg.json()
                
def compute_busarrival(estimated_arrival):
        timenow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timenow = datetime.datetime.strptime(timenow, "%Y-%m-%d %H:%M:%S")
        time_diff = datetime.datetime.strptime(estimated_arrival.replace('T', ' ').split('+')[0],'%Y-%m-%d %H:%M:%S') - timenow
        time_diff = math.floor(time_diff.total_seconds()/60)
        return time_diff

def get_busarrival_api(bus_stop_code):
        try:
                msg_split =bus_stop_code.split(',')
                r = requests.get(url=url_busArrival, headers=headers,params={'BusStopCode':msg_split[0]})
                bus_data = r.json()
                msg = 'Bus Arrival: '
                # print(bus_data)
                if len(msg_split)==2:
                        if msg_split[1] != '':
                                waiting_time = []
                                for bus in bus_data['Services']:
                                        i = [bus['NextBus']['EstimatedArrival'],bus['NextBus2']['EstimatedArrival'],bus['NextBus3']['EstimatedArrival']]
                                        if str(bus['ServiceNo']) == str(msg_split[1]):
                                                for k in i:
                                                        if k != '':
                                                                if compute_busarrival(k) < 1 :
                                                                        waiting_time.append('Arr')
                                                                else:
                                                                        waiting_time.append(compute_busarrival(k))
                                                        else:
                                                                waiting_time.append('NA')
                                                # print(waiting_time)
                                                bus_service = msg_split[1]
                                                msg += '\n' + str(bus_service) + " > " + str(waiting_time[0]) + " , " + str(waiting_time[1])  + " , " + str(waiting_time[2])
                                if msg == 'Bus Arrival: ':
                                        msg = "There is no such bus in this bus stop \n*This program is case sensitive. \ne.g.  'nr5' is not the same as 'NR5'"
                        else:
                                msg = 'Please enter a valid bus stop code and bus service!'
                        return msg
                if bus_data['Services'] == []:
                        msg = "Invalid Bus stop or there are currently no buses in service for this bus stop"
                        return msg
                for bus in bus_data['Services']:
                        bus_service = bus['ServiceNo']
                        waiting_time = []
                        i = [bus['NextBus']['EstimatedArrival'],bus['NextBus2']['EstimatedArrival'],bus['NextBus3']['EstimatedArrival']]
                        # print(i)
                        for k in i:
                                if k != '':
                                        if compute_busarrival(k) < 1 :
                                                waiting_time.append('Arr')
                                        else:
                                                waiting_time.append(compute_busarrival(k))
                                else:
                                        waiting_time.append('NA')
                        # print(waiting_time)
                        msg += '\n' + str(bus_service) + " > " + str(waiting_time[0]) + " , " + str(waiting_time[1])  + " , " + str(waiting_time[2])
                return msg
        except Exception as e:
                # There shouldn't be any exception
                msg = "Bus stop is invalid!"
                print(e)
                return msg
           
def listen():
        # write code here 
        get_ID = requests.get(url_getUpdates)
        trigger_json = get_ID.json()
        latest = len(trigger_json['result'])-1
        msg = ''
        if latest >=0:
                msg = trigger_json['result'][latest]['message']['text']
        return latest,msg

def reply(chat_id,rid):
        get_ID = requests.get(url_getUpdates)
        trigger_json = get_ID.json()
        msg = trigger_json['result'][rid]['message']['text']
        parameters = {'chat_id':chat_id, 'text':get_busarrival_api(msg)}
        return parameters

def check_id(checknum):
        get_ID = requests.get(url_getUpdates)
        trigger_json = get_ID.json()
        chat_id = trigger_json['result'][checknum]['message']['from']['id']
        return(chat_id)

# when you type in /start welcome message will be sent
#however if you want it to be done mannually pls uncomment the 2 lines below
# chat_id = 133282891 # Please change the chat ID to your own chat id
# send_welcome(chat_id)
def main():
        get_ID = requests.get(url_getUpdates)
        trigger_json = get_ID.json()
        checknum = len(trigger_json['result'])-1
        while True:
                latest_num = listen()[0]
                latest_msg = listen()[1]
                if  latest_num > checknum:
                        checknum += 1
                        chat_id = check_id(checknum)
                        if latest_msg == '/start':
                                send_welcome(chat_id)
                        else:
                                requests.post(url_sendMsg,params=reply(chat_id,checknum))
main()