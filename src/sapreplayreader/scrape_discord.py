# -*- coding: utf-8 -*-
"""
@author: KarmaKredits
"""
import requests
import json
import re
import time
from dotenv import load_dotenv

load_dotenv()
import os 
# 
DISCORDAUTH = os.getenv("DISCORDAUTH")



def retrieve_messages():
    headers = {
        'authorization':DISCORDAUTH
        }
    offsetnum=0
    #min_id=1431492467097600000&content=pid&author_type=user&sort_by=timestamp&sort_order=desc&offset=0
    min_id = 1433666794291200000
    r = requests.get(f'https://discord.com/api/v9/guilds/920457253541273670/messages/search?min_id={min_id}&content=pid&author_type=user&sort_by=timestamp&sort_order=desc&offset={offsetnum}', headers=headers)
    data=[]

    jsonn = json.loads(r.text)
    regex = '{"Pid":"(.+)","T":\d+}'
    #data.append(jsonn)
    # max_messages = jsonn['total_results'] if 'total_results' in jsonn else 0
    max_messages = 250
    while ('errors' not in jsonn and len(jsonn)>0):
        if ('messages' not in jsonn):
            print(jsonn)
            break
        print("len [messages]:",len(jsonn['messages']))
        if (len(jsonn['messages'])==0):
               break
        offsetnum = offsetnum + len(jsonn['messages']) #increment the offset of messages
        for mes in jsonn['messages']:
            pids = re.findall(regex, mes[0]['content'])
            print(pids)
            for pid in pids: # incase more than one pid in a message
                data.append(pid)
        print("Pid len:",len(data))
        print("offset:",offsetnum)        

        if offsetnum>max_messages:
            break # break to prevent too many requests in one go
        time.sleep(2)
        r = requests.get(f'https://discord.com/api/v9/guilds/920457253541273670/messages/search?content=pid&sort_by=timestamp&sort_order=desc&offset={offsetnum}', headers=headers)
        jsonn = json.loads(r.text)
        
    return data

# 

# with open(increment_file, 'w') as file:
#     file.write('')

if __name__ == "__main__":
    increment_file = 'pids_increment.txt'
    full_file = 'pids_full.txt'
    dataAll = retrieve_messages()
    print('pull Done')
    with open(full_file, 'w') as file:
        file.write(json.dumps(dataAll))
    print(f'Wrote full pid list to {full_file}')