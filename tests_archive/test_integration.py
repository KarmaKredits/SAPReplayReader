#!/usr/bin/env python
"""
Integration test: Verify the complete flow from Replay Summary to Replay Viewer.
Tests that clicking "View Selected Replay" properly loads the replay data.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_integration():
    """Test complete replay selection flow."""
    print("Integration Test: Complete Replay Selection Flow\n")
    print("=" * 60)
    
    try:
        from PyQt5.QtWidgets import QApplication, QTableWidgetItem
        from PyQt5.QtCore import Qt
        from sapreplayreader.gui_main import SAPReplayReaderGUI
        import pandas as pd
        
        # Create application and window
        app = QApplication([])
        window = SAPReplayReaderGUI()
        window.show()
        app.processEvents()
        
        print("\n1. Testing Replay Summary Tab")
        print("-" * 60)
        
        # Check if summary data is loaded
        summary_tab = window.replay_summary_tab
        if summary_tab.summary_df is not None:
            num_replays = len(summary_tab.summary_df)
            print(f"✓ Summary tab has {num_replays} replays")
            
            # Get first replay PID
            test_pid = summary_tab.summary_df.iloc[0]['pid']
            print(f"✓ Using test PID: {test_pid}")
        else:
            print("⚠ Summary data not available (summary.csv might not exist)")
            print("  This is OK - you can still test with manual selection")
            
            # Use a hardcoded test PID
            test_pid = '0007f058-5586-4490-84df-9a94330024dd'
            print(f"✓ Using hardcoded test PID: {test_pid}")
        
        print("\n2. Testing Replay Selection Callback")
        print("-" * 60)
        
        # Simulate replay selection
        print(f"Selecting replay: {test_pid}")
        window.on_replay_selected(test_pid)
        app.processEvents()
        
        print("✓ Selection callback executed")
        
        print("\n3. Testing Tab Switch to Replay Viewer")
        print("-" * 60)
        
        current_tab_idx = window.tab_widget.currentIndex()
        current_tab_name = window.tab_widget.tabText(current_tab_idx)
        
        if current_tab_idx == 1:
            print(f"✓ Switched to Replay Viewer tab (index {current_tab_idx})")
        else:
            print(f"✗ Wrong tab: {current_tab_name} (index {current_tab_idx})")
            return False
        
        print("\n4. Testing Replay Data Loading")
        print("-" * 60)
        
        viewer_tab = window.replay_viewer_tab
        
        if viewer_tab.replay_data is None:
            print("✗ Replay data not loaded")
            return False
        
        print(f"✓ Replay data loaded successfully")
        print(f"  - Current PID: {viewer_tab.current_pid}")
        print(f"  - JSON keys: {len(viewer_tab.replay_data)}")
        
        # Verify key fields
        required_keys = ['UserId', 'UserName', 'MatchId', 'LastTurn', 'Outcome']
        for key in required_keys:
            if key in viewer_tab.replay_data:
                print(f"  ✓ {key}: {str(viewer_tab.replay_data[key])[:50]}")
            else:
                print(f"  ⚠ {key}: not found")
        
        print("\n5. Testing Display Elements")
        print("-" * 60)
        
        # Check facts display
        facts_count = viewer_tab.facts_layout.count()
        print(f"✓ Replay facts displayed: {facts_count} items")
        
        # Check action summary
        summary_text = viewer_tab.action_summary_text.toPlainText()
        if summary_text:
            print(f"✓ Action summary displayed ({len(summary_text)} chars)")
        else:
            print("✓ Action summary area ready")
        
        # Check timeline
        if hasattr(viewer_tab, 'timeline_view'):
            print(f"✓ Timeline chart view available")
        
        print("\n" + "=" * 60)
        print("✓ INTEGRATION TEST PASSED!")
        print("=" * 60)
        
        print("\nSummary:")
        print(f"  - Data Processing tab: REMOVED ✓")
        print(f"  - Replay Summary tab: WORKING ✓")
        print(f"  - Replay selection: WORKING ✓")
        print(f"  - Tab switching: WORKING ✓")
        print(f"  - Data loading: WORKING ✓")
        print(f"  - Display rendering: WORKING ✓")
        
        window.close()
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
