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
try:
    from . import api_calls
except ImportError:
    import api_calls
#from . import api_calls  # import module so tests can monkeypatch api_client.fetch_replay

#from api_calls import download_replay # needed if process_from_df calls it here
#from api_calls import login # needed if process_from_df calls it here
# from api_calls import download_replay, login, process_from_df

# import os
# import requests


def get_replay(pid: str):
    output_directory = "Replays"
    output_filename = pid + ".json"

    # Construct the full path to the file
    full_path = os.path.join(output_directory, output_filename)
    try:
        with open(full_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: The file '{output_filename}' was not found in '{output_directory}' directory.")
        raise
    except json.JSONDecodeError:
        print(f"Error: The file '{output_filename}' contains invalid JSON.")
        raise

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
    pid_df = read_pid_df('data/pid_df.csv')
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
    pid_df.to_csv('data/pid_df.csv', index=False)
    return None

# get replay from opponent perspective; opponent Pids from all existing replay files
def extract_pids(list_of_pids: list = [] ):
    new_pids_list = []
    if list_of_pids == []:
        list_of_pids = read_replay_filenames()
    old_pids = read_replay_filenames()
    total = len(list_of_pids)
    cnt=0
    for pid in list_of_pids:
        cnt+=1
        print("Extract:",cnt,"/",total)
        replay = get_replay(pid)
        if replay["GenesisModeModel"] != None:
            gmm = json.loads(replay["GenesisModeModel"])
            opponents = gmm["Opponents"]
            for opponent in opponents:
                opp_pid = opponent["ParticipationId"]
                if opp_pid in (new_pids_list + old_pids + list_of_pids):
                    pass
                else:
                    new_pids_list.append(opponent["ParticipationId"])
    return new_pids_list

# adds new pids to the process db from pid list; doesnt download replays
def add_to_pid_df(pids: list):

    print("Adding new pids",len(pids))
    pid_df = read_pid_df('data/pid_df.csv')
    for pid in pids:
        if pid in pid_df["pid"].values:
            print("pid exists:",pid)
            pass
        else:
            print("new pid:",pid)
            pid_df.loc[len(pid_df)] = [pid,0,0,0,None,None] 
    pid_df.to_csv('data/pid_df.csv', index=False)
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
    opp_uid_list = []
    opp_name_list = []
    opp_pack_list = []
    opp_deck_list = []
    opp_rank_list = []
    opp_pid_list = []
    # will be null for customs, mode 1
    GMMexists = False
    if replay["GenesisModeModel"] != None:
        GMMexists=True
        GenesisModeModel = json.loads(replay["GenesisModeModel"])

        #print(len(GenesisModeModel["Opponents"]))
        for opponent in GenesisModeModel["Opponents"]:
            opp_uid_list.append(opponent["UserId"])
            opp_name_list.append(opponent["DisplayName"])
            opp_rank_list.append(opponent["Rank"]) 
            #need to check pack value for customs
            
            opp_pack_list.append(opponent["Pack"] if ("Pack" in opponent) else None)
            opp_pid_list.append(opponent["ParticipationId"]) 
            #opp_deck_list[i] = []

    lastactionresponse = json.loads(replay["Actions"][-1]["Response"]) if replay["Actions"][-1]["Response"] not in [None,""] else {}
    # in actions type 11
    # 
    version = None
    
    try:
        version = [json.loads(replay['Actions'][0]['Request'])["Version"]] if replay['Actions'][0]['Request'] not in [None,""] else None
    except (KeyError, json.JSONDecodeError):
        version = None
        pass

    d = {
        "matchid": [replay["MatchId"]],
        "datestart": [replay["CreatedOn"]],
        "dateend": [replay["Actions"][-1]["CreatedOn"]],
        "version":  version,
        "turns": [replay["LastTurn"]],
        "outcome": [replay["Outcome"]], #0=draw, 1=win, 2=loss, 3=abandoned
        "gamemode": [replay["Mode"]], #0=vs, 1=arena
        "versus": 1 if GMMexists else 0, #0=arena 
        "rankedgame": [0 if ("Name" in GenesisModeModel) else 1] if GMMexists else None, #find alternate ranked info
        "playercount": [GenesisModeModel["ActivePlayerCount"]] if GMMexists else None, #find alternative
        "userid": [replay["UserId"]],
        "username": [replay["UserName"]],
        "userpack": [replay["GenesisBuildModel"]["Bor"]["Pack"]], #["Deck"]
        "userrank": [lastactionresponse["NewRank"]["OldValue"] if ("NewRank" in lastactionresponse) else None], #only shows in ranked
        "pid": pid,
        "opp_uidlist": [str(opp_uid_list)],
        "opp_namelist": [str(opp_name_list)],
        "opp_ranklist": [str(opp_rank_list)],
        "opp_packlist": [str(opp_pack_list)],
        "opp_pid_list": [str(opp_pid_list)]
        
    }
    return pd.DataFrame(data=d)

    """
    Actions:
    Action Type: str
    BuildCount: #
    Time: timestamp str
    Freeze; 
    Order (pre action from request)
    Turn: #
    """
def extract_actions(pid: str):
    replay = get_replay(pid)
    actions = replay["Actions"]
    action_type_names = {
        0: "GAME READY",
        1: "GAME MODE",
        2: "GAME WATCH",
        3: "UNKNOWN TYPE 3",
        4: "START TURN",
        5: "ROLL",
        6: "BUY PET", # PLAY MINION
        7: "COMBINE PET", # STACK MINION
        8: "BUY FOOD", # PLAY SPELL
        9: "SELL PET", # SELL MINION
        10: "CHOOSE",
        11: "END TURN",
        12: "NAME BOARD"
    }
    outcome_names = {
        1: "Win",
        2: "Loss",
        3: "Draw"
    }
    maxlives = json.loads(replay.get("GenesisModeModel", None)).get("MaxLives", None) if replay.get("GenesisModeModel", None) else None
    lives = maxlives
    previous_turn_outcome = None
    action_list = []
    for action in actions:
        request = None
        response = None
        mode = None
        battle = None
        freeze = None
        order = None
        action_type = action["Type"]
        if action_type == 0: # GAME READY (battle info)
            build = json.loads(action["Build"])
            battle = json.loads(action["Battle"])
            previous_turn_outcome = battle.get("Outcome", None)
            lives -= 1 if previous_turn_outcome == 2 else 0
            if turn == 2 and lives < maxlives:
                lives += 1
        elif action_type == 1: # GAME MODE (Opp board)
            mode = json.loads(action["Mode"])
            
        elif action_type == 2: # # GAME WATCH (result if end)
            # could be empty dict
            if len(action["Response"]) > 3:
                response = json.loads(action["Response"])
            else:
                response = action["Response"] # could be empty dict
        elif action_type in [4,5,6,7,8,9,10,11]:
            request = json.loads(action["Request"])
            response = json.loads(action["Response"])
        elif action_type == 12: # NAME BOARD (first turn only)
            request = json.loads(action["Request"])
        else:
            print("Unknown Action Type:",action_type)
            print(json.dumps(action))

        if request and "BoardFreezes" in request:
            freeze = request["BoardFreezes"]
        if request and "BoardOrders" in request:
            order = request["BoardOrders"]

        build_count = action["BuildChangeCount"]
        time_stamp = action["CreatedOn"]
        turn = action["Turn"]
        
        # Extract amount for Buy Food actions
        amount = None
        if action_type == 8 and request:  # BUY FOOD
            amount = int(request.get("Cost", 0)) if "Cost" in request else None
        
        action_entry = {
            "Action Type": action_type_names[action_type],
            "BuildCount": build_count,
            "Time": time_stamp,
            "Freeze": freeze,
            "Order": order,
            "Turn": turn,
            "PreviousResult": outcome_names[previous_turn_outcome] if previous_turn_outcome is not None else None,
            #"PreviousResult": previous_turn_outcome,
            "Lives": lives
        }
        
        if amount is not None:
            action_entry["Amount"] = amount
        
        action_list.append(action_entry)
    return action_list

# Use when a new pid list has been scraped from discord
# may need to move list location before execution
def etl_newlist_download(filelist: list):
    print("==========================")
    print("etl_newlist_download")
    print("read pid file")
    pid_list = read_pid_file(filelist)
    pid_set = list(set(pid_list))
    #print(pid_set)
    print("add_to_pid_df")
    time.sleep(2)
    add_to_pid_df(pid_set)
    print("process_from_df")
    time.sleep(2)
    api_calls.process_from_df()
    print("Done")

    print("extract opponent pids")
    time.sleep(2)   
    new_opp_pid_set = extract_pids()

    print("add_to_pid_df for opp pids")
    time.sleep(2)   
    add_to_pid_df(new_opp_pid_set)
    print("process_from_df for opp pids")
    time.sleep(2)
    api_calls.process_from_df()
    print("Done")

    return None


# check summary for unprocecssed opp pids
def check_summary_for_opp_pids():
    print("==========================")
    print("check_summary_for_opp_pids")
    # read summary df
    try:
        summary_df = pd.read_csv('data/summary.csv',)
    except FileNotFoundError:
        print("No summary.csv file found.")
        return None

    opppidlist_list = []
    opppidlist_str = ''
    opp_pids = []
    existing_pids = summary_df['pid'].tolist()
    for index, row in summary_df.iterrows():
        opppidlist_str = row['opp_pid_list']
        if pd.isna(opppidlist_str) or opppidlist_str == '[]':
            continue
        # Convert string representation of list back to actual list
        opppidlist_list = eval(opppidlist_str)
        for opp_pid in opppidlist_list:
            if opp_pid not in opp_pids and opp_pid not in existing_pids:
                opp_pids.append(opp_pid)

    print(f"Extracted {len(opp_pids)} unique opponent PIDs from summary.")
    print("add_to_pid_df")
    time.sleep(2)
    add_to_pid_df(opp_pids)
    print("process_from_df")
    time.sleep(2)
    api_calls.process_from_df()
    print("Done")
    return None


def generate_summarydb_from_files(progress_callback=None):
    """Generate summary DB from replay files.

    If `progress_callback` is provided, it will be called as
    `progress_callback(processed_count, total_count)` after each file is processed.
    """
    print("---- GENERATING SUMMARY DB FROM FILES ----")
    files = read_replay_filenames()
    total = len(files)

    if total == 0:
        # write empty dataframe
        pd.DataFrame().to_csv('data/summary.csv', index=False)
        if progress_callback:
            progress_callback(0, 0)
        print("---- SUMMARY DB GENERATED AND SAVED (no files) ----")
        return

    # Initialize with first file
    summary_df = get_summary(files[0])
    cnt = 1
    if progress_callback:
        progress_callback(cnt, total)

    for file in files[1:]:
        cnt += 1
        print(file, ' | ', cnt, '/', total)
        try:
            summary_df = pd.concat([summary_df, get_summary(file)], ignore_index=True)
        except Exception as e:
            print(f"Warning: failed to process {file}: {e}")
        if progress_callback:
            try:
                progress_callback(cnt, total)
            except Exception:
                pass

    summary_df.to_csv('data/summary.csv', index=False)
    print("---- SUMMARY DB GENERATED AND SAVED ----")


if __name__ == "__main__":
    """
    ==== Proceedures ====
    1. etl_newlist_download("pids_full.txt")
    2. check_summary_for_opp_pids()

    """

    # RUN AFTER SCRAPING NEW PID LIST FROM DISCORD
    #etl_newlist_download("pids_full.txt")

    # RUN AFTER ETL_NEWLIST_DOWNLOAD to capture opponent pids
    #check_summary_for_opp_pids()

    # RUN to download all unprocessed replays from pid_df
    #api_calls.process_from_df()

 
    # GENERATE SUMMARY DB FROM ALL REPLAY FILES
    generate_summarydb_from_files()


    """ other """
    # test_actions = extract_actions("17a5fc19-0ae7-461c-97d1-c3eb623513d8")
    # for action in test_actions:
    #     print(action)
    # actions_df = pd.DataFrame(test_actions) 
    # print(actions_df)
    # actions_df.to_csv('data/action_test.csv',index=False)


    """
    Unit index
    Build table of all Uni and fill with known and unknown BoIDs
    """
    # hard mode: 9eb139a4-baf4-4586-a83c-e50a2a4ea5f0
    pass