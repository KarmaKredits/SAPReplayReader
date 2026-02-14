#!/usr/bin/env python
"""
Debug script to check turn time computation from actual replay data.
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Map action types
action_type_names = {
    0: "GAME READY",
    1: "GAME MODE",
    2: "GAME WATCH",
    3: "UNKNOWN TYPE 3",
    4: "START TURN",
    5: "ROLL",
    6: "BUY PET",
    7: "COMBINE PET",
    8: "BUY FOOD",
    9: "SELL PET",
    10: "CHOOSE",
    11: "END TURN",
    12: "NAME BOARD"
}

replay_file = 'Replays/0a3a16f1-43e3-4fb7-ba74-e9806a5d9f6b.json'

try:
    with open(replay_file, 'r') as f:
        replay = json.load(f)
    
    actions = replay['Actions']
    print(f"Total actions: {len(actions)}\n")
    
    # Show first 30 actions to see the pattern
    print("First 30 actions (Turn | Type | CreatedOn):")
    print("-" * 80)
    for i, action in enumerate(actions[:30]):
        turn = action['Turn']
        action_type = action_type_names.get(action['Type'], f"UNKNOWN ({action['Type']})")
        timestamp = action['CreatedOn']
        print(f"{i:2d}. Turn {turn:2d} | {action_type:15s} | {timestamp}")
    
    # Now let's identify Start Turn and End Turn pairs for each turn
    print("\n" + "="*80)
    print("Analyzing Start Turn and End Turn timestamps:\n")
    
    turn_pairs = {}
    for action in actions:
        turn_num = action['Turn']
        action_type = action['Type']
        timestamp = action['CreatedOn']
        
        if turn_num not in turn_pairs:
            turn_pairs[turn_num] = {}
        
        if action_type == 4:  # START TURN
            turn_pairs[turn_num]['start'] = timestamp
        elif action_type == 11:  # END TURN
            turn_pairs[turn_num]['end'] = timestamp
    
    # Compute turn times
    print(f"{'Turn':<5} {'Start Turn':<30} {'End Turn':<30} {'Duration (sec)':<15}")
    print("-" * 85)
    
    from datetime import datetime
    
    for turn_num in sorted(turn_pairs.keys()):
        pair = turn_pairs[turn_num]
        if 'start' in pair and 'end' in pair:
            try:
                # Handle timestamps with variable decimal precision
                start_str = pair['start'].replace("Z", "+00:00")
                end_str = pair['end'].replace("Z", "+00:00")
                
                # Try to parse, handling different microsecond precisions
                try:
                    start_time = datetime.fromisoformat(start_str)
                except ValueError:
                    # Try truncating microseconds if needed
                    import re
                    start_str = re.sub(r'(\.\d{6})\d+(\+|Z)', r'\1\2', start_str)
                    start_time = datetime.fromisoformat(start_str)
                
                try:
                    end_time = datetime.fromisoformat(end_str)
                except ValueError:
                    # Try truncating microseconds if needed
                    import re
                    end_str = re.sub(r'(\.\d{6})\d+(\+|Z)', r'\1\2', end_str)
                    end_time = datetime.fromisoformat(end_str)
                
                duration = (end_time - start_time).total_seconds()
                
                print(f"{turn_num:<5} {pair['start']:<30} {pair['end']:<30} {duration:<15.1f}")
            except Exception as e:
                print(f"{turn_num:<5} Error parsing timestamps: {e}")
        else:
            missing = []
            if 'start' not in pair:
                missing.append("START")
            if 'end' not in pair:
                missing.append("END")
            print(f"{turn_num:<5} {'MISSING: ' + ','.join(missing):<60}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
