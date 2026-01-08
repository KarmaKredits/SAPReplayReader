"""Simple API client to fetch replay JSON with optional auth.

This module provides a small helper to log in to the Teamwood API and
helpers used elsewhere in the package.

Functions provided:
- login(email=None, password=None, api_version=API_VERSION) -> dict
- get_oauth2_token(token_url, client_id, client_secret) -> str
- fetch_replay(url, auth=None) -> dict
"""

from typing import Dict, Optional
from urllib.parse import urljoin
import requests
import os
from dotenv import load_dotenv
import json
import pandas as pd
import time


load_dotenv()

API_VERSION = 44


def login(email: Optional[str] = None, password: Optional[str] = None, api_version: int = API_VERSION, timeout: int = 20) -> Dict:
    """Log in to the Teamwood API and return the parsed JSON response.

    Credentials are read from environment variables if not supplied:
      SAP_EMAIL or SAPEMAIL
      SAP_PASS or SAPPASS

    Returns the parsed JSON response (commonly includes a token).
    """
    email = email or os.getenv("SAPEMAIL")
    password = password or os.getenv("SAPPASS")
    if not email or not password:
        raise ValueError("Email and password must be provided via arguments or environment variables")

    url = f"https://api.teamwood.games/0.{api_version}/api/user/login"
    payload = {"Email": email, "Password": password, "Version": api_version}
    headers = {"Content-Type": "application/json; utf-8", "Accept": "application/json"}

    resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    
    resp.raise_for_status()
    return resp.json()


def download_replay(pid: str, auth: Optional[str] = None, api_version: int = API_VERSION, timeout: int = 20) -> Dict:
    auth = auth or os.getenv("SAPAUTH")
    #print(auth)
    if not auth:
        raise ValueError("Auth must be provided via arguments or environment variables")
    # {"Pid":"17a5fc19-0ae7-461c-97d1-c3eb623513d8","T":15}
    #replay_code = f'\{\"Pid\":\"{pid}\",\"T\":1\}'
    url = f"https://api.teamwood.games/0.{api_version}/api/playback/participation"
    payload = {
        "ParticipationId": pid,
        "ParticipationName": None,
        "ChangeMin": None,
        "ChangeMax": None,
        "TurnMin": None,
        "TurnMax": None,
        "DateMin": None,
        "DateMax": None,
        "Version": API_VERSION
        }
    headers = {"Authorization": f"Bearer {auth}", 
               "Content-Type": "application/json; utf-8", 
               "Authority": "api.teamwood.games"}
    # body =  json.dumps({
    #             "ParticipationId": pid,
    #             "Turn": 1,
    #             "Version": API_VERSION
    #         })
    print("Sending request for: ",pid)
    try:
        resp = requests.post(url, json=payload, headers=headers,timeout=timeout)
        #resp.raise_for_status()
        print("Status Code:",resp.status_code)
        if(resp.status_code != 200 and resp.status_code != 400):
            print("JSON:",resp.json())
    except requests.exceptions.ConnectionError as err:
        # eg, no internet
        #raise SystemExit(err)
        print (SystemExit(err))
    except requests.exceptions.HTTPError as err:
        # eg, url, server and other errors
        #raise SystemExit(err)
        print(SystemExit(err))
    # the rest of my code is going here

    # Define the target directory and filename
    output_directory = "Replays"
    output_filename = pid + ".json"

    # Create the directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Construct the full path to the file
    full_path = os.path.join(output_directory, output_filename)
    if ("Message" in resp.json()):
        print(resp.json()["Message"])
        return None
    
    with open(full_path, "w") as f:
        json.dump(resp.json(), f, indent=4) # indent=4 for pretty-printing with 4 spaces

    print(f"JSON data successfully written to: {full_path}")
    return resp.json()  

def process_from_df(api_version: int = API_VERSION,reprocess: int = 0):
    print("---process_from_df()---")
    TOKEN = login(api_version=api_version)["Token"]
    pid_df = read_pid_df('pid_df.csv')    
    for i in range(len(pid_df)):
        # print("=========================================")
        # print(pid_df.iloc[i])
        #print(pid_df.at[i,"pid"])
        
        # for non processed and non failures
        condition = (pid_df.at[i,"processed"]==0) and (pid_df.at[i,"failure"]==reprocess)
        #print("condition:", condition)
        if (condition):
            print("processing:",pid_df.at[i,"pid"])
            #set failure to true before attempt
            pid_df.at[i,["failure","processdate"]] = [1,int(time.time())]
            #pid_df.at[i,"processdate"] = int(time.time())
            #save df here
            pid_df.to_csv('pid_df.csv', index=0)
            # get replay from url # save replay occures in download

            replay = download_replay(pid=pid_df.at[i,"pid"],auth=TOKEN,api_version=api_version)
            if replay != None:
                # set version
                if replay['Actions'][0]['Request'] not in [None,""]:
                    if "Version" in json.loads(replay['Actions'][0]['Request']):
                        ver = json.loads(replay['Actions'][0]['Request'])["Version"]
                    else:
                        ver = API_VERSION
                else:
                    ver = API_VERSION

                pid_df.at[i,["version","gamedate","processed","failure"]] = [ver,replay["CreatedOn"],1,0]

                #print(pid_df.iloc[i])
                # save df
                pid_df.to_csv('pid_df.csv', index=0)
                print("Saving Entry:",pid_df.at[i,"pid"])
            else:
                print("Replay failure")
                
            time.sleep(1)
        #break
    #pid_df.to_csv('pid_df.csv', index=False)
    print("----process_from_df() COMPLETE----")
    return None

# DUPLICATE from api_client.py but needed here to avoid circular import
def read_pid_df(filename: str):
    try:
        df = pd.read_csv(filename,)
    except FileNotFoundError:
        return {}
    return df


if __name__== "__main__":
    pass
    # resp_login = login()
    # login
    # print(resp_login)
    #process_from_df()
    # ## read all file names in Replays
    # pid_list = read_replay_filenames()
    # ## update the process df with all replay files as processed and version number.
    # update_process_db(pid_list)
    # ## save process file
    #pid_df = read_pid_df('pid_df.csv')   
    # print(pid_df.iloc[0])
    # print(pid_df.iloc[0]["pid"])
    # condition = pid_df["pid"] == pid_df.iloc[0]["pid"]
    # print(condition)
    # pid_df.at[0,"failure"] = 0
    # print(pid_df.iloc[0])
    # test_pid = "17a5fc19-0ae7-461c-97d1-c3eb623513d8"
    # #print(login())
    # #replayData = download_replay(pid="17a5fc19-0ae7-461c-97d1-c3eb623513d8")
    # replay = get_replay(test_pid)
    # for i in replay:
    #     if len(i)<100:
    #         print(i)

    #newpidlist = extract_pids()

    # print("add_to_pid_df")
    # time.sleep(5)
    # add_to_pid_df(newpidlist)
    # print("process_from_df")
    # # time.sleep(5)
    # process_from_df()

