#!/usr/bin/env python
"""
Final comprehensive test for Buy Pet Y-axis improvements.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sapreplayreader.gui_replay_viewer import ReplayTimelineVisualization

def test_buy_pet_comprehensive():
    """Comprehensive test: Buy Pet Y-axis with actual replay data."""
    print("=" * 70)
    print("FINAL COMPREHENSIVE TEST: Buy Pet Y-axis Requirements")
    print("=" * 70)
    print()
    
    # Requirements:
    # 1. Buy Pet Y-axis values should always be whole numbers with no decimals
    # 2. Y-axis should always show 0 as the minimum value
    
    viz = ReplayTimelineVisualization()
    pid = "0a3a16f1-43e3-4fb7-ba74-e9806a5d9f6b"
    
    if not viz.load_actions(pid):
        print("✗ Failed to load actions")
        return False
    
    print(f"Loaded {len(viz.actions)} actions from replay\n")
    
    # Test 1: Get Buy Pet Y-axis data
    print("-" * 70)
    print("Test 1: Buy Pet Y-axis returns only whole numbers")
    print("-" * 70)
    
    x_values, y_values = viz.get_timeline_data(x_axis_mode="turns", y_axis_mode="buy pet")
    
    # Check all values
    all_integers = True
    decimal_count = 0
    
    for y in y_values:
        if not (isinstance(y, int) or (isinstance(y, float) and y.is_integer())):
            all_integers = False
            decimal_count += 1
    
    if all_integers:
        print("✓ All Y-values are whole numbers (no decimals)")
    else:
        print(f"✗ Found {decimal_count} Y-values with decimal portions")
        return False
    
    # Test 2: Check minimum value
    print()
    print("-" * 70)
    print("Test 2: Y-axis minimum is 0")
    print("-" * 70)
    
    min_y = min(y_values)
    if min_y == 0:
        print(f"✓ Minimum Y-value is 0 (starts at 0)")
    else:
        print(f"✗ Minimum Y-value is {min_y}, should be 0")
        return False
    
    # Test 3: Display sample values
    print()
    print("-" * 70)
    print("Test 3: Sample Buy Pet progression")
    print("-" * 70)
    
    buy_pet_indices = [i for i, action in enumerate(viz.actions) if action.get("Action Type") == "BUY PET"]
    print(f"Found {len(buy_pet_indices)} Buy Pet actions\n")
    
    sample_count = min(10, len(buy_pet_indices))
    print(f"First {sample_count} Buy Pet actions:")
    for idx_pos, idx in enumerate(buy_pet_indices[:sample_count]):
        y_val = y_values[idx]
        is_whole = y_val == int(y_val)
        print(f"  Buy Pet #{idx_pos + 1}: Y = {int(y_val):3d} (whole: {is_whole})")
    
    # Test 4: Verify Buy Pet actions increment from 1
    print()
    print("-" * 70)
    print("Test 4: Buy Pet cumulative count increments correctly")
    print("-" * 70)
    
    buy_pet_y_values = [y_values[idx] for idx in buy_pet_indices]
    
    # Check if Buy Pet values form a sequence 1, 2, 3, 4, ...
    expected_sequence = list(range(1, len(buy_pet_y_values) + 1))
    
    if buy_pet_y_values == expected_sequence:
        print(f"✓ Buy Pet cumulative sequence is correct: {buy_pet_y_values[:10]}...")
    else:
        print(f"✗ Sequence mismatch")
        print(f"  Expected: {expected_sequence[:10]}...")
        print(f"  Got:      {buy_pet_y_values[:10]}...")
        return False
    
    # Test 5: Verify plot Y-axis limits
    print()
    print("-" * 70)
    print("Test 5: Plot Y-axis configuration")
    print("-" * 70)
    
    from sapreplayreader.gui_replay_viewer import TimelineChartView
    
    chart_view = TimelineChartView()
    chart_view.plot_timeline(x_values, y_values, x_label="Turns", y_label="BUY PET Count", title="Buy Pet Count Over Time")
    
    y_min, y_max = chart_view.ax.get_ylim()
    print(f"Y-axis limits: ({y_min}, {y_max})")
    
    if y_min == 0:
        print(f"✓ Y-axis minimum is 0")
    else:
        print(f"✗ Y-axis minimum is {y_min}, should be 0")
        return False
    
    if y_max > max(y_values):
        print(f"✓ Y-axis maximum has padding ({y_max} > {max(y_values)})")
    else:
        print(f"⚠ Y-axis maximum may need padding")
    
    return True

if __name__ == "__main__":
    print()
    success = test_buy_pet_comprehensive()
    
    print()
    print("=" * 70)
    if success:
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("=" * 70)
        print()
        print("Buy Pet Y-axis requirements satisfied:")
        print("  1. ✓ All values are whole numbers with no decimals")
        print("  2. ✓ Y-axis minimum is always 0")
        sys.exit(0)
    else:
        print("✗✗✗ SOME TESTS FAILED ✗✗✗")
        print("=" * 70)
        sys.exit(1)
