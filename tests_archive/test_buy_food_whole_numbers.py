#!/usr/bin/env python
"""
Final verification that Buy Food Y-axis shows only whole numbers like 1, 2, 3 (not 1.5, 2.3, etc).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sapreplayreader.gui_replay_viewer import ReplayTimelineVisualization

def test_buy_food_whole_numbers():
    """Verify Buy Food Y-axis values are whole numbers with no decimal portions."""
    print("Final Verification: Buy Food Y-axis shows only whole numbers\n")
    
    viz = ReplayTimelineVisualization()
    pid = "0a3a16f1-43e3-4fb7-ba74-e9806a5d9f6b"
    
    if not viz.load_actions(pid):
        print("Failed to load actions")
        return False
    
    x_values, y_values = viz.get_timeline_data(x_axis_mode="turns", y_axis_mode="buy food")
    
    # Filter to Buy Food Y-values only
    buy_food_y_values = [y_values[i] for i, action in enumerate(viz.actions) if action.get("Action Type") == "BUY FOOD"]
    
    print(f"Buy Food Y-axis values: {buy_food_y_values}\n")
    
    # Check each value
    print("Checking each value:")
    print("-" * 70)
    all_whole = True
    
    for i, y_val in enumerate(buy_food_y_values):
        is_whole = y_val == int(y_val)
        remainder = y_val - int(y_val)
        
        status = "✓" if is_whole else "✗"
        print(f"{status} Y[{i:2d}] = {y_val:6.2f} | Whole: {is_whole} | Decimal portion: {remainder:.6f}")
        
        if remainder != 0:
            all_whole = False
    
    print()
    if all_whole:
        print(f"✓ SUCCESS: All {len(buy_food_y_values)} Buy Food Y-values are whole numbers")
        print("  No decimal portions (like 1.5, 2.3, etc.) found")
        return True
    else:
        print(f"✗ FAILURE: Some Buy Food Y-values have decimal portions")
        return False

if __name__ == "__main__":
    success = test_buy_food_whole_numbers()
    sys.exit(0 if success else 1)
