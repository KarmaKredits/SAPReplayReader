#!/usr/bin/env python
"""
Debug script to check Buy Food request structure.
"""

import json

replay_file = 'Replays/0a3a16f1-43e3-4fb7-ba74-e9806a5d9f6b.json'

try:
    with open(replay_file, 'r') as f:
        replay = json.load(f)
    
    actions = replay['Actions']
    
    # Find Buy Food actions (type 8)
    buy_food_actions = [a for a in actions if a['Type'] == 8]
    
    print(f"Found {len(buy_food_actions)} Buy Food actions\n")
    
    # Show first 5 Buy Food actions and their request structure
    for i, action in enumerate(buy_food_actions[:5]):
        print(f"Buy Food Action {i + 1}:")
        print(f"  Type: {action['Type']}")
        print(f"  Turn: {action['Turn']}")
        print(f"  CreatedOn: {action['CreatedOn']}")
        
        if action.get('Request'):
            try:
                request = json.loads(action['Request'])
                print(f"  Request keys: {list(request.keys())}")
                print(f"  Request data: {json.dumps(request, indent=4)}")
            except:
                print(f"  Request: {action['Request']}")
        else:
            print(f"  Request: Empty or None")
        
        print()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
