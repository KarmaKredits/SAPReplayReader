"""Placeholder reader for SAP replay files.

This module now supports either reading from a local file path or fetching
JSON from an HTTP(S) endpoint. If `path` looks like a URL (starts with http),
the function will POST to the endpoint and return the parsed JSON.
"""
from typing import Dict, Optional
from urllib.parse import urlparse
import pandas as pd
from pathlib import Path
import os

import json
import time

from . import api_client  # import module so tests can monkeypatch api_client.fetch_replay


def read_replay(path: str, *, auth: Optional[Dict] = None) -> Dict:
    """Read a replay from a local path or fetch from an HTTP(S) API.

    If `path` is a URL (http/https) this will POST and return the parsed JSON
    via the API client. For local files it attempts to read the JSON and
    returns an empty dict on failure (keeps previous placeholder behavior).
    """
    parsed = urlparse(path)
    if parsed.scheme in ("http", "https"):
        return api_client.fetch_replay(path, auth=auth)

    # Local file fallback
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# from api_client import download_replay # needed if process_from_df calls it here
# from api_client import login # needed if process_from_df calls it here

# import os
# import requests
# from . import api_client

def get_replay(pid: str):
    output_directory = "Replays"
    output_filename = pid + ".json"

    # Construct the full path to the file
    full_path = os.path.join(output_directory, output_filename)
    try:
        with open(full_path, 'r') as file:
            data = json.load(file)
            print('Replay Loaded!')
    except FileNotFoundError:
        print(f"Error: The file '{output_filename}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{output_filename}' contains invalid JSON.")
    return data

def read_pid_df(filename: str):
    try:
        df = pd.read_csv(filename,)
    except FileNotFoundError:
        return {}
    return df

def read_replay_filenames():
    folder_path = "Replays"
    all_entries = os.listdir(folder_path)
    file_names = []
    for entry in all_entries:
        full_path = os.path.join(folder_path, entry)
        if os.path.isfile(full_path) and entry.endswith(".json"):
            file_names.append(entry[:-5])
    return file_names

# Read a file containing a list of discord messages with Pids, clean and return as a list
def read_pid_file(filename: str):

    # Determine file path: if only a name was provided, look in the same folder as this module.
    p = Path(filename)
    if p.name == filename:
        file_path = Path(__file__).parent / filename
    else:
        file_path = p

    try:
        data = file_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        # keep previous behavior for tests: return empty dict
        return {}

    # Keep the entire file text in `data` (already done). Now normalize and parse.
    s = data.strip()

    # Remove surrounding brackets if present
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1].strip()

    if not s:
        return []

    # Split on commas and strip whitespace and optional quotes from each item
    def _strip_quotes(x: str) -> str:
        x = x.strip()
        if (x.startswith('"') and x.endswith('"')) or (x.startswith("'") and x.endswith("'")):
            return x[1:-1]
        return x

    items = [_strip_quotes(part) for part in s.split(",")]
    return items

# updates the process db from existing downloads
def update_process_db(file_names: list):
    #pid,processed,version
    ver = 0
    # read df
    pid_df = read_pid_df('pid_df.csv')
    print(pid_df)

    # Only check unprocessed

    for file in file_names:
        print(file)
        replay = get_replay(file)
        ver = json.loads(replay['Actions'][0]['Request'])["Version"]
        gamedate = replay['CreatedOn']
        # only get files not processed
        index = pid_df.loc[(pid_df['processed'] == 0) & (pid_df['pid']==file)]
        print(True in index)
        if (True in index):
            pid_df.loc[pid_df['pid'] == file, 'processed'] = 1
            print(ver)
            pid_df.loc[pid_df['pid'] == file, 'version'] = ver
            pid_df.loc[pid_df['pid'] == file, 'processdate'] = int(time.time())
            pid_df.loc[pid_df['pid'] == file, 'gamedate'] = gamedate
            pid_df.loc[pid_df['pid'] == file, 'failure'] = 0
        # add new row if the file is not in the df
        elif(file not in pid_df['pid'].values):
            # pid,version,processed,failure,processdate,gamedate
            pid_df.loc[len(pid_df)] = [file,ver,1,0,int(time.time()),gamedate] 
            print("NEW ROW INSERTED")
    #save df
    pid_df.to_csv('pid_df.csv', index=False)
    return None

# get replay from opponent perspective; opponent Pids from all existing replay files
def extract_pids():
    new_pids = []
    old_pids = read_replay_filenames()
    total = len(old_pids)
    cnt=0
    for pid in old_pids:
        cnt+=1
        print("Extract:",cnt,"/",total)
        replay = get_replay(pid)
        if replay["GenesisModeModel"] != None:
            gmm = json.loads(replay["GenesisModeModel"])
            opponents = gmm["Opponents"]
            for opponent in opponents:
                opp_pid = opponent["ParticipationId"]
                if opp_pid in (new_pids + old_pids):
                    pass
                else:
                    new_pids.append(opponent["ParticipationId"])
    return new_pids

# adds new pids to the process db from pid list; doesnt download replays
def add_to_pid_df(pids: list):

    print("Adding new pids",len(pids))
    pid_df = read_pid_df('pid_df.csv')
    for pid in pids:
        if pid in pid_df["pid"].values:
            print("pid exists:",pid)
            pass
        else:
            print("new pid:",pid)
            pid_df.loc[len(pid_df)] = [pid,0,0,0,None,None] 
    pid_df.to_csv('pid_df.csv', index=False)
    return None

# summary df
"""
    Get all processed pids, can just read straight from Replay folder.
    Summary items:
    - pid participation id
    - user id
    - opp user id
    - match id
    - own pack: #
    - version: num
    - num of turns
    - outcome: 1=win;2=loss
    - date
    - opp pack
    - game mode: 0=standard; 1=weekly; 2=custom; lobby?
    - player count: # (1v1 or lobby)
    - turn duration: secs
    - match length: time
    - match type: ranked/private
"""

# extracts summary info from a replay (str) and returns as a dataframe row
# [] need to add opponent pids to summary db and update this.
def get_summary(pid: str):
    replay = get_replay(pid)
    oppidlist = []
    oppnamelist = []
    opppacklist = []
    oppdecklist = []
    oppranklist = []
    opppidlist = []
    # will be null for customs, mode 1
    GMMexists = False
    if replay["GenesisModeModel"] != None:
        GMMexists=True
        GenesisModeModel = json.loads(replay["GenesisModeModel"])

        print(len(GenesisModeModel["Opponents"]))
        for opponent in GenesisModeModel["Opponents"]:
            oppidlist.append(opponent["UserId"])
            oppnamelist.append(opponent["DisplayName"])
            oppranklist.append(opponent["Rank"]) 
            #need to check pack value for customs
            
            opppacklist.append(opponent["Pack"] if ("Pack" in opponent) else None)
            #oppranklist.append(opponent["ParticipationId"]) 
            #oppdecklist[i] = []
    lastactionresponse = json.loads(replay["Actions"][-1]["Response"])

    d = {
        "matchid": [replay["MatchId"]],
        "datestart": [replay["CreatedOn"]],
        "dateend": [replay["Actions"][-1]["CreatedOn"]],
        "version": [json.loads(replay['Actions'][0]['Request'])["Version"]],
        "turns": [replay["LastTurn"]],
        "outcome": [replay["Outcome"]], #0=draw, 1=win, 2=loss
        "gamemode": [replay["Mode"]], #0=vs, 1=arena
        "versus": 1 if GMMexists else 0, #0=arena 
        "rankedgame": [0 if ("Name" in GenesisModeModel) else 1] if GMMexists else None, #find alternate ranked info
        "playercount": [GenesisModeModel["ActivePlayerCount"]] if GMMexists else None, #find alternative
        "userid": [replay["UserId"]],
        "username": [replay["UserName"]],
        "userpack": [replay["GenesisBuildModel"]["Bor"]["Pack"]], #["Deck"]
        "userrank": [lastactionresponse["NewRank"]["OldValue"] if ("NewRank" in lastactionresponse) else None], #only shows in ranked
        "oppidlist": [str(oppidlist)],
        "oppnamelist": [str(oppnamelist)],
        "oppranklist": [str(oppranklist)],
        "opppacklist": [str(opppacklist)]
        #,"opppidlist": [str(opppidlist)]
    }
    return pd.DataFrame(data=d)



if __name__ == "__main__":
    #test_pid = "1877d5c7-bd77-4a0b-92d2-cacae2c459ca"
    # pid_list = read_pid_file("pids-copy.txt")
    # pid_set = list(set(pid_list))


    # pid_df.to_csv('pid_df.csv', index=False)
    #pid_df = read_pid_df('pid_df.csv')


    pid_list = read_pid_file("pids_full.txt")
    pid_set = list(set(pid_list))
    print(pid_set)
    print("add_to_pid_df")
    time.sleep(5)
    add_to_pid_df(pid_set)
    print("process_from_df")
    time.sleep(5)
    api_client.process_from_df()




    # # summary df
    # files = read_replay_filenames()
    # print(files[0])
    # summary_df = get_summary(files[0])
    # total = len(files)
    # cnt = 0
    # for file in files:
    #     cnt += 1
    #     if (file == files[0]):
    #         pass
    #     else:
    #         print(file,' | ',cnt,'/',total)
    #         summary_df = pd.concat([summary_df, get_summary(file)], ignore_index=True)
    # summary_df.to_csv('summary.csv',index=False)
    # print("Done")


    """
    Actions:
    Action Type: str
    BuildCount: #
    Time: timestamp str
    SubAction: Freeze; Order (pre action from request)
    Turn: #
    """

    """
    Unit index
    Build table of all Uni and fill with known and unknown BoIDs
    """
    # hard mode: 9eb139a4-baf4-4586-a83c-e50a2a4ea5f0
    pass