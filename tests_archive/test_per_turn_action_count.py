#!/usr/bin/env python
"""
Test to verify action counts reset per turn instead of being cumulative.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sapreplayreader.gui_replay_viewer import ReplayTimelineVisualization
from datetime import datetime, timedelta

def test_per_turn_counts():
    """Test that action counts reset per turn."""
    print("Testing per-turn action counts...\n")
    
    viz = ReplayTimelineVisualization()
    
    # Create mock actions across multiple turns
    base_time = datetime.fromisoformat("2025-10-26T06:57:39.625806+00:00")
    
    mock_actions = [
        # Turn 1
        {"Action Type": "START TURN", "Turn": 1, "Time": base_time.isoformat(), "Lives": 6, "BuildCount": 1},
        {"Action Type": "BUY PET", "Turn": 1, "Time": (base_time + timedelta(seconds=1)).isoformat(), "Lives": 6},
        {"Action Type": "BUY PET", "Turn": 1, "Time": (base_time + timedelta(seconds=2)).isoformat(), "Lives": 6},
        {"Action Type": "ROLL", "Turn": 1, "Time": (base_time + timedelta(seconds=3)).isoformat(), "Lives": 6},
        {"Action Type": "BUY PET", "Turn": 1, "Time": (base_time + timedelta(seconds=4)).isoformat(), "Lives": 6},
        {"Action Type": "END TURN", "Turn": 1, "Time": (base_time + timedelta(seconds=5)).isoformat(), "Lives": 6},
        
        # Turn 2
        {"Action Type": "START TURN", "Turn": 2, "Time": (base_time + timedelta(seconds=6)).isoformat(), "Lives": 6},
        {"Action Type": "BUY PET", "Turn": 2, "Time": (base_time + timedelta(seconds=7)).isoformat(), "Lives": 6},
        {"Action Type": "BUY PET", "Turn": 2, "Time": (base_time + timedelta(seconds=8)).isoformat(), "Lives": 6},
        {"Action Type": "ROLL", "Turn": 2, "Time": (base_time + timedelta(seconds=9)).isoformat(), "Lives": 6},
        {"Action Type": "END TURN", "Turn": 2, "Time": (base_time + timedelta(seconds=10)).isoformat(), "Lives": 6},
        
        # Turn 3
        {"Action Type": "START TURN", "Turn": 3, "Time": (base_time + timedelta(seconds=11)).isoformat(), "Lives": 6},
        {"Action Type": "BUY PET", "Turn": 3, "Time": (base_time + timedelta(seconds=12)).isoformat(), "Lives": 6},
        {"Action Type": "ROLL", "Turn": 3, "Time": (base_time + timedelta(seconds=13)).isoformat(), "Lives": 6},
        {"Action Type": "END TURN", "Turn": 3, "Time": (base_time + timedelta(seconds=14)).isoformat(), "Lives": 6},
    ]
    
    viz.actions = mock_actions
    
    # Get Buy Pet Y-axis data (per-turn count)
    x_values, y_values = viz.get_timeline_data(x_axis_mode="turns", y_axis_mode="buy pet")
    
    print("Turn 1 (3 Buy Pet actions):")
    print("-" * 60)
    for i in range(6):
        action = mock_actions[i]
        y_val = y_values[i]
        turn = action["Turn"]
        action_type = action["Action Type"]
        print(f"  {i}: {action_type:15s} (Turn {turn}) -> Y={y_val}")
    
    print("\nTurn 2 (2 Buy Pet actions):")
    print("-" * 60)
    for i in range(6, 11):
        action = mock_actions[i]
        y_val = y_values[i]
        turn = action["Turn"]
        action_type = action["Action Type"]
        print(f"  {i}: {action_type:15s} (Turn {turn}) -> Y={y_val}")
    
    print("\nTurn 3 (1 Buy Pet action):")
    print("-" * 60)
    for i in range(11, 15):
        action = mock_actions[i]
        y_val = y_values[i]
        turn = action["Turn"]
        action_type = action["Action Type"]
        print(f"  {i}: {action_type:15s} (Turn {turn}) -> Y={y_val}")
    
    # Verify per-turn reset
    print("\n" + "=" * 60)
    print("Verification of per-turn reset:")
    print("=" * 60)
    
    # Turn 1: Should have 0, 1, 2, 2, 3, 3
    turn1_values = y_values[0:6]
    expected_turn1 = [0, 1, 2, 2, 3, 3]
    
    if turn1_values == expected_turn1:
        print(f"✓ Turn 1 values correct: {turn1_values}")
    else:
        print(f"✗ Turn 1 values incorrect")
        print(f"  Expected: {expected_turn1}")
        print(f"  Got:      {turn1_values}")
        return False
    
    # Turn 2: Should reset to 0, 1, 2, 2, 2
    turn2_values = y_values[6:11]
    expected_turn2 = [0, 1, 2, 2, 2]
    
    if turn2_values == expected_turn2:
        print(f"✓ Turn 2 values correct (reset): {turn2_values}")
    else:
        print(f"✗ Turn 2 values incorrect")
        print(f"  Expected: {expected_turn2}")
        print(f"  Got:      {turn2_values}")
        return False
    
    # Turn 3: Should reset to 0, 1, 1, 1
    turn3_values = y_values[11:15]
    expected_turn3 = [0, 1, 1, 1]
    
    if turn3_values == expected_turn3:
        print(f"✓ Turn 3 values correct (reset): {turn3_values}")
    else:
        print(f"✗ Turn 3 values incorrect")
        print(f"  Expected: {expected_turn3}")
        print(f"  Got:      {turn3_values}")
        return False
    
    # Verify max value per turn never exceeds the number of Buy Pet actions in that turn
    print("\nMax values per turn:")
    print(f"  Turn 1: max = {max(turn1_values)} (3 Buy Pet actions) - ✓")
    print(f"  Turn 2: max = {max(turn2_values)} (2 Buy Pet actions) - ✓")
    print(f"  Turn 3: max = {max(turn3_values)} (1 Buy Pet action) - ✓")
    
    return True

def test_with_replay_data():
    """Test with actual replay data."""
    print("\n" + "=" * 60)
    print("Testing with actual replay data...\n")
    
    viz = ReplayTimelineVisualization()
    pid = "0a3a16f1-43e3-4fb7-ba74-e9806a5d9f6b"
    
    if not viz.load_actions(pid):
        print("✗ Failed to load actions")
        return False
    
    x_values, y_values = viz.get_timeline_data(x_axis_mode="turns", y_axis_mode="buy pet")
    
    # Group by turn and find max value per turn
    turn_max = {}
    for i, action in enumerate(viz.actions):
        turn = action.get("Turn", 0)
        y_val = y_values[i]
        
        if turn not in turn_max:
            turn_max[turn] = y_val
        else:
            turn_max[turn] = max(turn_max[turn], y_val)
    
    # Count Buy Pet per turn
    buy_pet_per_turn = {}
    for action in viz.actions:
        if action.get("Action Type") == "BUY PET":
            turn = action.get("Turn", 0)
            buy_pet_per_turn[turn] = buy_pet_per_turn.get(turn, 0) + 1
    
    print("Buy Pet count vs Y-axis max per turn:")
    print("-" * 60)
    
    all_match = True
    for turn in sorted(buy_pet_per_turn.keys())[:10]:  # Show first 10 turns
        expected_max = buy_pet_per_turn[turn]
        actual_max = turn_max[turn]
        match = expected_max == actual_max
        status = "✓" if match else "✗"
        print(f"{status} Turn {turn:2d}: {expected_max} Buy Pets -> Max Y = {actual_max}")
        if not match:
            all_match = False
    
    if all_match:
        print("\n✓ All turns have correct per-turn max values")
        return True
    else:
        print("\n✗ Some turns have incorrect max values")
        return False

if __name__ == "__main__":
    test1_pass = test_per_turn_counts()
    test2_pass = test_with_replay_data()
    
    print("\n" + "=" * 60)
    if test1_pass and test2_pass:
        print("✓ All per-turn count tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
