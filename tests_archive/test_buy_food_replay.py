#!/usr/bin/env python
"""
Test Buy Food Y-axis with actual replay data.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sapreplayreader.gui_replay_viewer import ReplayTimelineVisualization

def test_buy_food_with_replay():
    """Test Buy Food Y-axis with actual replay data."""
    print("Testing Buy Food Y-axis with actual replay data...\n")
    
    viz = ReplayTimelineVisualization()
    pid = "0a3a16f1-43e3-4fb7-ba74-e9806a5d9f6b"
    
    # Load actions from the replay
    if not viz.load_actions(pid):
        print("Failed to load actions")
        return False
    
    print(f"Loaded {len(viz.actions)} actions\n")
    
    # Get Buy Food Y-axis data
    x_values, y_values = viz.get_timeline_data(x_axis_mode="turns", y_axis_mode="buy food")
    
    # Find Buy Food actions
    buy_food_indices = [i for i, action in enumerate(viz.actions) if action.get("Action Type") == "BUY FOOD"]
    
    print(f"Buy Food actions found: {len(buy_food_indices)}\n")
    print("Buy Food actions with amounts and cumulative Y-values:")
    print("-" * 70)
    
    total_cost = 0
    has_decimals = False
    
    for idx in buy_food_indices[:20]:  # Show first 20
        action = viz.actions[idx]
        amount = action.get("Amount", "N/A")
        y_value = y_values[idx]
        
        # Check if it's an integer or a whole number
        is_integer = isinstance(y_value, int) or (isinstance(y_value, float) and y_value.is_integer())
        
        print(f"Action {idx:3d}: Amount={str(amount):3s} -> Y={y_value:6.1f} (int: {y_value == int(y_value)})")
        
        if not is_integer:
            has_decimals = True
            print(f"  ⚠ WARNING: Non-integer value detected!")
    
    print()
    
    # Check if any Buy Food Y-value has decimals
    buy_food_y_values = [y_values[idx] for idx in buy_food_indices]
    
    all_integers = all(isinstance(y, int) or (isinstance(y, float) and y.is_integer()) for y in buy_food_y_values)
    
    if all_integers:
        print(f"✓ All {len(buy_food_y_values)} Buy Food Y-values are integers (no decimals)")
        return True
    else:
        print(f"✗ Some Buy Food Y-values have decimals")
        decimal_values = [y for y in buy_food_y_values if not (isinstance(y, int) or (isinstance(y, float) and y.is_integer()))]
        print(f"  Found {len(decimal_values)} non-integer values")
        return False

if __name__ == "__main__":
    success = test_buy_food_with_replay()
    sys.exit(0 if success else 1)
