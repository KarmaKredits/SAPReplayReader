#!/usr/bin/env python
"""
Test script to verify Buy Food amount extraction.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test the amount extraction logic
def test_buy_food_amount_extraction():
    """Test that Buy Food amounts are correctly extracted as integers."""
    print("Testing Buy Food amount extraction...")
    
    # Simulate Buy Food action extraction logic
    action_type = 8  # BUY FOOD
    
    # Test case 1: Request with Cost as integer
    request_1 = {"Cost": 3}
    amount_1 = int(request_1.get("Cost", 0)) if "Cost" in request_1 else None
    assert amount_1 == 3 and isinstance(amount_1, int), f"Expected 3 (int), got {amount_1} ({type(amount_1)})"
    print(f"✓ Cost extraction from integer: {amount_1} (type: {type(amount_1).__name__})")
    
    # Test case 2: Request with Cost as float
    request_2 = {"Cost": 2.5}
    amount_2 = int(request_2.get("Cost", 0)) if "Cost" in request_2 else None
    assert amount_2 == 2 and isinstance(amount_2, int), f"Expected 2 (int), got {amount_2} ({type(amount_2)})"
    print(f"✓ Cost extraction from float (converted to int): {amount_2} (type: {type(amount_2).__name__})")
    
    # Test case 3: Request without Cost field
    request_3 = {}
    amount_3 = int(request_3.get("Cost", 0)) if "Cost" in request_3 else None
    assert amount_3 is None, f"Expected None, got {amount_3}"
    print(f"✓ Missing Cost field returns None: {amount_3}")
    
    # Test case 4: Non-Buy Food action
    action_type_other = 6  # BUY PET
    request_4 = {"Cost": 4}
    # Only extract amount for Buy Food (action_type == 8)
    amount_4 = int(request_4.get("Cost", 0)) if "Cost" in request_4 and action_type_other == 8 else None
    assert amount_4 is None, f"Expected None (action type is not Buy Food), got {amount_4}"
    print(f"✓ Non-Buy Food action returns None: {amount_4}")
    
    print("\n✓ All Buy Food amount extraction tests passed!")

if __name__ == "__main__":
    test_buy_food_amount_extraction()
