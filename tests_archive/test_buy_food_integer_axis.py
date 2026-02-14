#!/usr/bin/env python
"""
Test script to verify Buy Food Y-axis shows integers with no decimals.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sapreplayreader.gui_replay_viewer import ReplayTimelineVisualization
from datetime import datetime, timedelta

def test_buy_food_integer_axis():
    """Test that Buy Food Y-axis increments by cost amount and shows only integers."""
    print("Testing Buy Food Y-axis with integer values...\n")
    
    viz = ReplayTimelineVisualization()
    
    # Create mock actions with Buy Food amounts
    base_time = datetime.fromisoformat("2025-10-26T06:57:39.625806+00:00")
    
    mock_actions = [
        {
            "Action Type": "START TURN",
            "Turn": 1,
            "Time": base_time.isoformat(),
            "Lives": 6,
            "BuildCount": 1
        },
        {
            "Action Type": "BUY FOOD",
            "Turn": 1,
            "Time": (base_time + timedelta(seconds=2)).isoformat(),
            "Lives": 6,
            "BuildCount": 2,
            "Amount": 3  # Cost 3
        },
        {
            "Action Type": "BUY PET",
            "Turn": 1,
            "Time": (base_time + timedelta(seconds=4)).isoformat(),
            "Lives": 6,
            "BuildCount": 3
        },
        {
            "Action Type": "BUY FOOD",
            "Turn": 1,
            "Time": (base_time + timedelta(seconds=6)).isoformat(),
            "Lives": 6,
            "BuildCount": 4,
            "Amount": 2  # Cost 2
        },
        {
            "Action Type": "BUY PET",
            "Turn": 1,
            "Time": (base_time + timedelta(seconds=8)).isoformat(),
            "Lives": 6,
            "BuildCount": 5
        },
        {
            "Action Type": "BUY FOOD",
            "Turn": 1,
            "Time": (base_time + timedelta(seconds=10)).isoformat(),
            "Lives": 6,
            "BuildCount": 6,
            "Amount": 1  # Cost 1
        },
        {
            "Action Type": "END TURN",
            "Turn": 1,
            "Time": (base_time + timedelta(seconds=12)).isoformat(),
            "Lives": 6,
            "BuildCount": 7
        }
    ]
    
    viz.actions = mock_actions
    
    # Test Buy Food Y-axis
    x_values, y_values = viz.get_timeline_data(x_axis_mode="turns", y_axis_mode="buy food")
    
    print("Buy Food Y-axis values (cumulative by cost):")
    print("-" * 60)
    for i, (x, y) in enumerate(zip(x_values, y_values)):
        action_type = mock_actions[i]["Action Type"]
        amount = mock_actions[i].get("Amount", "N/A")
        print(f"Action {i}: {action_type:15s} (Amount: {str(amount):3s}) -> Y={y:3.0f} (type: {type(y).__name__})")
    
    print()
    
    # Verify all Buy Food values are integers with no decimals
    buy_food_values = [y for i, y in enumerate(y_values) if mock_actions[i]["Action Type"] == "BUY FOOD"]
    
    all_integers = all(isinstance(y, int) or (isinstance(y, float) and y.is_integer()) for y in buy_food_values)
    if all_integers:
        print("✓ All Buy Food Y-values are integers")
    else:
        print("✗ Some Buy Food Y-values contain decimals:")
        for i, y in enumerate(buy_food_values):
            if not (isinstance(y, int) or (isinstance(y, float) and y.is_integer())):
                print(f"  {y} (type: {type(y).__name__})")
        return False
    
    # Verify cumulative amount: BUY FOOD actions should increment by Amount field
    # Expected sequence: 0, 3, 3, 5, 5, 6, 6
    expected_sequence = [0, 3, 3, 5, 5, 6, 6]
    if y_values == expected_sequence:
        print(f"✓ Buy Food cumulative values are correct: {y_values}")
    else:
        print(f"✗ Buy Food cumulative values incorrect")
        print(f"  Expected: {expected_sequence}")
        print(f"  Got:      {y_values}")
        return False
    
    # Test Buy Pet Y-axis (should increment by 1 each time)
    x_values_pet, y_values_pet = viz.get_timeline_data(x_axis_mode="turns", y_axis_mode="buy pet")
    
    print("\nBuy Pet Y-axis values (cumulative, increment by 1):")
    print("-" * 60)
    for i, (x, y) in enumerate(zip(x_values_pet, y_values_pet)):
        action_type = mock_actions[i]["Action Type"]
        print(f"Action {i}: {action_type:15s} -> Y={y:3.0f} (type: {type(y).__name__})")
    
    # For BUY PET, there are 2 occurrences
    # Expected sequence: 0, 0, 1, 1, 2, 2, 2
    expected_pet_sequence = [0, 0, 1, 1, 2, 2, 2]
    if y_values_pet == expected_pet_sequence:
        print(f"✓ Buy Pet cumulative values are correct: {y_values_pet}")
    else:
        print(f"✗ Buy Pet cumulative values incorrect")
        print(f"  Expected: {expected_pet_sequence}")
        print(f"  Got:      {y_values_pet}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_buy_food_integer_axis()
    sys.exit(0 if success else 1)
