"""
Replay Viewer Tab for SAP Replay Reader GUI.
Displays detailed information about a selected replay and visualizes the action timeline.
"""

import json
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QComboBox, QScrollArea, QFrame, QGridLayout, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QRadioButton, QButtonGroup,
    QPushButton, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from sapreplayreader import reader

# Use matplotlib for timeline visualization instead of PyQt charts
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


def parse_iso_timestamp(timestamp_str):
    """Parse ISO format timestamp, handling variable decimal precision."""
    try:
        # Replace Z with +00:00 for compatibility
        ts = timestamp_str.replace("Z", "+00:00")
        return datetime.fromisoformat(ts)
    except ValueError:
        # Try truncating microseconds to 6 digits if needed
        import re
        ts = re.sub(r'(\.\d{6})\d+(\+|-)', r'\1\2', timestamp_str)
        ts = ts.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(ts)
        except ValueError:
            # Last resort: try to parse manually
            import re
            match = re.match(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.(\d+)([\+\-]\d{2}:\d{2}|Z)', timestamp_str)
            if match:
                year, month, day, hour, minute, second, microsecond_str, tz_part = match.groups()
                # Pad or truncate microseconds to 6 digits
                microsecond = int(microsecond_str.ljust(6, '0')[:6])
                tz_str = "+00:00" if tz_part == "Z" else tz_part
                return datetime.fromisoformat(f"{year}-{month}-{day}T{hour}:{minute}:{second}.{microsecond}{tz_str}")
            else:
                raise ValueError(f"Cannot parse timestamp: {timestamp_str}")


class ReplayTimelineVisualization:
    """Handles timeline visualization data and rendering."""
    
    def __init__(self):
        self.actions = []
        self.x_axis_mode = "turns"  # Can be "turns" or "timestamp"
        self.y_axis_mode = "lives"  # Default Y-axis
    
    def load_actions(self, pid: str):
        """Load and process actions from a replay."""
        try:
            self.actions = reader.extract_actions(pid)
            return True
        except Exception as e:
            print(f"Error loading actions: {e}")
            return False
    
    def get_available_y_axes(self):
        """Get list of available Y-axis options from actions."""
        if not self.actions:
            return ["Lives"]
        
        # Always include Lives
        y_axes = ["Lives"]
        
        # Collect action breakdown items (exclude certain fields) - case insensitive matching
        excluded_patterns = {"end turn", "game ready", "game watch", "name board", "start turn", "game mode"}
        action_counts = {}
        
        for action in self.actions:
            action_type = action.get("Action Type", "Unknown")
            if action_type and action_type.lower() not in excluded_patterns:
                action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        y_axes.extend(sorted(action_counts.keys()))
        y_axes.append("Turn Time")
        
        return y_axes
    
    def get_timeline_data(self, x_axis_mode="turns", y_axis_mode="lives"):
        """Get timeline data for plotting."""
        self.x_axis_mode = x_axis_mode
        self.y_axis_mode = y_axis_mode
        
        if not self.actions:
            return [], []
        
        # Pre-process: build turn time map (turn_number -> seconds_elapsed)
        turn_times = {}
        if y_axis_mode == "turn time":
            for action in self.actions:
                turn_num = action.get("Turn", 0)
                action_type = action.get("Action Type", "")
                time_str = action.get("Time", "")
                
                if turn_num not in turn_times and action_type.lower() == "start turn" and time_str:
                    turn_times[turn_num] = {"start": time_str}
                elif turn_num in turn_times and action_type.lower() == "end turn" and time_str:
                    turn_times[turn_num]["end"] = time_str
                elif turn_num not in turn_times and action_type.lower() == "end turn" and time_str:
                    turn_times[turn_num] = {"end": time_str}
            
            # Calculate elapsed seconds for each turn
            for turn_num in turn_times:
                if "start" in turn_times[turn_num] and "end" in turn_times[turn_num]:
                    try:
                        start_time = parse_iso_timestamp(turn_times[turn_num]["start"])
                        end_time = parse_iso_timestamp(turn_times[turn_num]["end"])
                        turn_times[turn_num]["elapsed"] = max(0, (end_time - start_time).total_seconds())
                    except Exception as e:
                        print(f"Warning: Failed to parse turn {turn_num} timestamps: {e}")
                        turn_times[turn_num]["elapsed"] = 0
                else:
                    turn_times[turn_num]["elapsed"] = 0
        
        x_values = []
        y_values = []
        timestamp_base = None
        current_turn = None
        action_type_count = 0  # For count of specific action type in current turn
        last_turn_x = 0
        
        # Determine if this is action count mode (needs aggregation per turn)
        is_action_count = y_axis_mode not in ["lives", "turn time"]
        
        for idx, action in enumerate(self.actions):
            # X-axis
            if x_axis_mode == "turns":
                x = action.get("Turn", 0)
            else:  # timestamp
                time_str = action.get("Time", "")
                if idx == 0 and time_str:
                    try:
                        timestamp_base = parse_iso_timestamp(time_str)
                    except Exception as e:
                        print(f"Warning: Failed to parse base timestamp: {e}")
                
                if timestamp_base and time_str:
                    try:
                        current_time = parse_iso_timestamp(time_str)
                        x = (current_time - timestamp_base).total_seconds()
                    except Exception as e:
                        print(f"Warning: Failed to parse current timestamp: {e}")
                        x = len(x_values)
                else:
                    x = len(x_values)
            
            # Y-axis
            if y_axis_mode == "lives":
                y = int(action.get("Lives", 0))
                x_values.append(x)
                y_values.append(y)
            elif y_axis_mode == "turn time":
                # Get elapsed seconds for this turn from pre-computed map
                turn_num = action.get("Turn", 0)
                y = int(turn_times.get(turn_num, {}).get("elapsed", 0))
                x_values.append(x)
                y_values.append(y)
            else:
                # Per-turn count of specific action type (resets each turn)
                action_turn = action.get("Turn", 0)
                
                # Record previous turn's count when entering a new turn
                if action_turn != current_turn and current_turn is not None:
                    x_values.append(current_turn if x_axis_mode == "turns" else last_turn_x)
                    y_values.append(int(action_type_count))
                    current_turn = action_turn
                    action_type_count = 0
                elif current_turn is None:
                    current_turn = action_turn
                
                last_turn_x = x
                action_type = action.get("Action Type", "Unknown")
                if action_type.lower() == y_axis_mode.lower():
                    # For Buy Food, increment by the Amount field; otherwise increment by 1
                    if action_type.lower() == "buy food" and "Amount" in action:
                        action_type_count += int(action.get("Amount", 1))
                    else:
                        action_type_count += 1
        
        # For action counts, append the final turn's count after loop
        if is_action_count and current_turn is not None:
            x_values.append(current_turn if x_axis_mode == "turns" else last_turn_x)
            y_values.append(int(action_type_count))
        
        return x_values, y_values

    @staticmethod
    def get_timeline_data_from_actions(actions, x_axis_mode="turns", y_axis_mode="lives"):
        """Compute timeline x/y values from a provided actions list (independent of instance)."""
        if not actions:
            return [], []

        # Pre-process: build turn time map (turn_number -> seconds_elapsed)
        turn_times = {}
        if y_axis_mode == "turn time":
            for action in actions:
                turn_num = action.get("Turn", 0)
                action_type = action.get("Action Type", "")
                time_str = action.get("Time", "")

                if turn_num not in turn_times and action_type.lower() == "start turn" and time_str:
                    turn_times[turn_num] = {"start": time_str}
                elif turn_num in turn_times and action_type.lower() == "end turn" and time_str:
                    turn_times[turn_num]["end"] = time_str
                elif turn_num not in turn_times and action_type.lower() == "end turn" and time_str:
                    turn_times[turn_num] = {"end": time_str}

            # Calculate elapsed seconds for each turn
            for turn_num in turn_times:
                if "start" in turn_times[turn_num] and "end" in turn_times[turn_num]:
                    try:
                        start_time = parse_iso_timestamp(turn_times[turn_num]["start"])
                        end_time = parse_iso_timestamp(turn_times[turn_num]["end"])
                        turn_times[turn_num]["elapsed"] = max(0, (end_time - start_time).total_seconds())
                    except Exception:
                        turn_times[turn_num]["elapsed"] = 0
                else:
                    turn_times[turn_num]["elapsed"] = 0

        x_values = []
        y_values = []
        timestamp_base = None
        current_turn = None
        action_type_count = 0
        last_turn_x = 0

        # Determine if this is action count mode (needs aggregation per turn)
        is_action_count = y_axis_mode not in ["lives", "turn time"]

        for idx, action in enumerate(actions):
            # X-axis
            if x_axis_mode == "turns":
                x = action.get("Turn", 0)
            else:
                time_str = action.get("Time", "")
                if idx == 0 and time_str:
                    try:
                        timestamp_base = parse_iso_timestamp(time_str)
                    except Exception:
                        timestamp_base = None

                if timestamp_base and time_str:
                    try:
                        current_time = parse_iso_timestamp(time_str)
                        x = (current_time - timestamp_base).total_seconds()
                    except Exception:
                        x = len(x_values)
                else:
                    x = len(x_values)

            # Y-axis
            if y_axis_mode == "lives":
                y = int(action.get("Lives", 0))
                x_values.append(x)
                y_values.append(y)
            elif y_axis_mode == "turn time":
                turn_num = action.get("Turn", 0)
                y = int(turn_times.get(turn_num, {}).get("elapsed", 0))
                x_values.append(x)
                y_values.append(y)
            else:
                action_turn = action.get("Turn", 0)
                if action_turn != current_turn and current_turn is not None:
                    # Record previous turn's count when entering a new turn
                    x_values.append(current_turn if x_axis_mode == "turns" else last_turn_x)
                    y_values.append(int(action_type_count))
                    current_turn = action_turn
                    action_type_count = 0
                elif current_turn is None:
                    current_turn = action_turn

                last_turn_x = x
                action_type = action.get("Action Type", "Unknown")
                if action_type.lower() == y_axis_mode.lower():
                    if action_type.lower() == "buy food" and "Amount" in action:
                        action_type_count += int(action.get("Amount", 1))
                    else:
                        action_type_count += 1

        # For action counts, append the final turn's count after loop
        if is_action_count and current_turn is not None:
            x_values.append(current_turn if x_axis_mode == "turns" else last_turn_x)
            y_values.append(int(action_type_count))

        return x_values, y_values
    
    def get_action_summary(self):
        """Get summary statistics about actions."""
        if not self.actions:
            return {}
        
        action_counts = {}
        for action in self.actions:
            action_type = action.get("Action Type", "Unknown")
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        return {
            "total_actions": len(self.actions),
            "action_counts": action_counts,
            "max_turn": max((a.get("Turn", 0) for a in self.actions), default=0),
            "final_lives": self.actions[-1].get("Lives", 0) if self.actions else 0
        }



class ReplayViewerTab(QWidget):
    """Tab for viewing detailed replay information and timeline."""
    
    def __init__(self):
        super().__init__()
        self.current_pid = None
        self.replay_data = None
        self.summary_row = None
        self.timeline = ReplayTimelineVisualization()
        # Opponent replays mapping: pid -> {name, available(bool), data(dict)}
        self.opp_replays = {}
        self.selected_opp_pid = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI for the replay viewer tab."""
        main_layout = QVBoxLayout()
        
        # Top section: Replay details (compact, max 20% height)
        details_label = QLabel("Replay Details:")
        details_font = QFont("Arial", 9, QFont.Weight.Bold)
        details_label.setFont(details_font)
        main_layout.addWidget(details_label)
        
        # Create compact 3-column facts panel for Game and Player info
        self.facts_frame = QFrame()
        self.facts_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                padding: 0px;
            }
        """)
        self.facts_layout = QGridLayout(self.facts_frame)
        self.facts_layout.setSpacing(0)
        self.facts_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container for Game/Player info and scrollable Opponent table
        details_container = QWidget()
        details_container_layout = QHBoxLayout(details_container)
        details_container_layout.setContentsMargins(0, 0, 0, 0)
        details_container_layout.setSpacing(8)
        
        # Add facts frame (Game and Player columns)
        details_container_layout.addWidget(self.facts_frame, 2, Qt.AlignmentFlag.AlignTop)
        
        # Create opponent section (vertical layout with label and scrollable table)
        opponent_section = QWidget()
        opponent_section_layout = QVBoxLayout(opponent_section)
        opponent_section_layout.setContentsMargins(0, 0, 0, 0)
        opponent_section_layout.setSpacing(2)
        
        # Opponent section header
        opponent_header = QLabel("Opponent(s)")
        opponent_header_font = QFont("Arial", 10, QFont.Weight.Bold)
        opponent_header.setFont(opponent_header_font)
        opponent_section_layout.addWidget(opponent_header)
        
        # Create scrollable table for Opponent names and packs
        self.opponent_table = QTableWidget()
        self.opponent_table.setColumnCount(2)
        self.opponent_table.setHorizontalHeaderLabels(["Name", "Pack"])
        self.opponent_table.setMaximumHeight(120)
        self.opponent_table.setMinimumHeight(60)
        self.opponent_table.horizontalHeader().setFont(QFont("Arial", 8, QFont.Weight.Bold))
        self.opponent_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.opponent_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.opponent_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.opponent_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.opponent_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.opponent_table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                gridline-color: #eeeeee;
            }
            QTableWidget::item {
                padding: 2px;
                font-size: 7pt;
            }
            QHeaderView::section {
                padding: 2px;
                background-color: #f5f5f5;
                border: none;
            }
        """)
        opponent_section_layout.addWidget(self.opponent_table)
        # Opponent selection combo (for overlay/comparison and opening opponent replay)

        # Row: single-select combobox (for opening) + multi-select visibility list (for overlays)
        controls_row = QHBoxLayout()

        self.opp_combo = QComboBox()
        self.opp_combo.addItem("None", None)
        self.opp_combo.setMaximumWidth(160)
        self.opp_combo.currentIndexChanged.connect(self.on_opp_selected)
        controls_row.addWidget(self.opp_combo)

        # Multi-select list for opponent visibility (controls which opponent graphs are shown)
        self.opp_visibility_list = QListWidget()
        self.opp_visibility_list.setMaximumWidth(200)
        self.opp_visibility_list.setMaximumHeight(120)
        self.opp_visibility_list.itemChanged.connect(self.on_opp_visibility_changed)
        controls_row.addWidget(self.opp_visibility_list)

        opponent_section_layout.addLayout(controls_row)

        # Select All / Deselect All buttons for visibility list
        vis_btns = QHBoxLayout()
        self.select_all_btn = QPushButton("All")
        self.deselect_all_btn = QPushButton("None")
        self.select_all_btn.setMaximumWidth(60)
        self.deselect_all_btn.setMaximumWidth(60)
        self.select_all_btn.clicked.connect(self.select_all_opponents)
        self.deselect_all_btn.clicked.connect(self.deselect_all_opponents)
        vis_btns.addWidget(self.select_all_btn)
        vis_btns.addWidget(self.deselect_all_btn)
        opponent_section_layout.addLayout(vis_btns)

        self.open_opp_button = QPushButton("Open Opponent Replay")
        self.open_opp_button.setMaximumWidth(160)
        self.open_opp_button.clicked.connect(self.open_selected_opponent)
        opponent_section_layout.addWidget(self.open_opp_button)

        opponent_section_layout.addStretch()
        
        details_container_layout.addWidget(opponent_section, 1, Qt.AlignmentFlag.AlignTop)
        
        main_layout.addWidget(details_container, 0)
        
        # Bottom section: Timeline and visualization
        
        # Bottom section: Timeline and visualization
        # Timeline header and controls
        timeline_header = QHBoxLayout()
        timeline_label = QLabel("Action Timeline:")
        timeline_font = QFont("Arial", 10, QFont.Weight.Bold)
        timeline_label.setFont(timeline_font)
        timeline_header.addWidget(timeline_label)
        timeline_header.addStretch()
        
        # X-axis mode selector
        timeline_header.addWidget(QLabel("X-Axis:"))
        self.x_axis_combo = QComboBox()
        self.x_axis_combo.addItems(["Turns", "Timestamp"])
        self.x_axis_combo.currentIndexChanged.connect(self.update_timeline)
        self.x_axis_combo.setMaximumWidth(100)
        timeline_header.addWidget(self.x_axis_combo)
        
        main_layout.addLayout(timeline_header)
        
        # Timeline visualization
        self.timeline_view = TimelineChartView()
        main_layout.addWidget(self.timeline_view)
        
        # Y-axis selector (radio buttons)
        y_axis_label = QLabel("Y-Axis:")
        y_axis_label_font = QFont("Arial", 9, QFont.Weight.Bold)
        y_axis_label.setFont(y_axis_label_font)
        
        self.y_axis_button_group = QButtonGroup()
        y_axis_layout = QHBoxLayout()
        y_axis_layout.addWidget(y_axis_label)
        
        # Will be populated dynamically when replay loads
        self.y_axis_radio_buttons = {}
        self.y_axis_layout_container = y_axis_layout
        
        y_axis_widget = QWidget()
        y_axis_widget.setLayout(y_axis_layout)
        main_layout.addWidget(y_axis_widget)
        
        # Action summary
        summary_label = QLabel("Action Summary:")
        summary_font = QFont("Arial", 10, QFont.Weight.Bold)
        summary_label.setFont(summary_font)
        main_layout.addWidget(summary_label)
        
        self.action_summary_text = QTextEdit()
        self.action_summary_text.setReadOnly(True)
        self.action_summary_text.setMaximumHeight(120)
        self.action_summary_text.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                padding: 5px;
                font-family: Courier;
                font-size: 9pt;
            }
        """)
        main_layout.addWidget(self.action_summary_text)
        
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        self.setLayout(main_layout)
    
    def load_replay(self, pid: str):
        """Load and display a replay."""
        self.current_pid = pid
        
        try:
            # Load replay JSON
            self.replay_data = reader.get_replay(pid)
            
            # Load summary row for this replay
            try:
                summary_df = pd.read_csv('data/summary.csv')
                self.summary_row = summary_df[summary_df['pid'] == pid].iloc[0] if pid in summary_df['pid'].values else None
            except:
                self.summary_row = None
            
            # Load and process actions
            try:
                self.timeline.load_actions(pid)
                # Populate Y-axis buttons based on loaded actions
                self.populate_y_axis_buttons()
                # Load opponent pids and try to preload opponent replays
                try:
                    # initialize opp_replays mapping, combo and visibility list
                    self.opp_replays.clear()
                    self.opp_combo.clear()
                    self.opp_combo.addItem("None", None)
                    self.opp_visibility_list.clear()

                    if self.summary_row is not None:
                        def clean_list_value(value):
                            v = str(value)
                            if v.startswith('[') and v.endswith(']'):
                                v = v[1:-1]
                            return v

                        opp_pid_raw = self.summary_row.get("opp_pid_list") or self.summary_row.get("opp_pid") or ""
                        opp_name_raw = self.summary_row.get("opp_namelist") or self.summary_row.get("opponent") or ""
                        opp_pid_str = clean_list_value(str(opp_pid_raw))
                        opp_name_str = clean_list_value(str(opp_name_raw))

                        opp_pids = [p.strip().strip("'\"") for p in opp_pid_str.split(',') if p.strip()]
                        opp_names = [n.strip().strip("'\"") for n in opp_name_str.split(',') if n.strip()]

                        # align lengths
                        maxlen = max(len(opp_pids), len(opp_names))
                        for i in range(maxlen):
                            name = opp_names[i] if i < len(opp_names) else f"Opponent {i+1}"
                            pid_val = opp_pids[i] if i < len(opp_pids) else None

                            if not pid_val:
                                display = f"{name} (no pid)"
                                self.opp_combo.addItem(display, None)
                                # add disabled visibility item
                                item = QListWidgetItem(display)
                                item.setData(Qt.UserRole, None)
                                item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                                item.setCheckState(Qt.Unchecked)
                                self.opp_visibility_list.addItem(item)
                                continue

                            # try to preload replay/actions for opponent
                            available = False
                            opp_actions = None
                            try:
                                opp_replay = reader.get_replay(pid_val)
                                if opp_replay:
                                    try:
                                        opp_actions = reader.extract_actions(pid_val)
                                        available = True if opp_actions and len(opp_actions) > 0 else False
                                    except Exception:
                                        available = False
                                else:
                                    available = False
                            except Exception:
                                available = False

                            self.opp_replays[pid_val] = {"name": name, "available": available, "actions": opp_actions}
                            display = f"{name} ({pid_val[:8]})"
                            if not available:
                                display = f"{name} ({pid_val[:8]}) - missing"
                            self.opp_combo.addItem(display, pid_val)

                            # add to visibility list (checked by default if available)
                            vis_item = QListWidgetItem(display)
                            vis_item.setData(Qt.UserRole, pid_val)
                            vis_item.setFlags(vis_item.flags() | Qt.ItemIsUserCheckable)
                            if available:
                                vis_item.setCheckState(Qt.Checked)
                            else:
                                vis_item.setCheckState(Qt.Unchecked)
                                vis_item.setFlags(vis_item.flags() & ~Qt.ItemIsEnabled)
                            self.opp_visibility_list.addItem(vis_item)
                except Exception:
                    pass
            except Exception as e:
                print(f"Warning: Failed to load actions: {e}")
                # Continue anyway, actions won't display but facts will
            
            # Display facts
            self.display_facts()
            
            # Update timeline
            self.update_timeline()
            
            # Display action summary
            self.display_action_summary()
            
        except FileNotFoundError as e:
            print(f"Error: Replay file not found: {e}")
        except Exception as e:
            print(f"Error loading replay: {e}")
            import traceback
            traceback.print_exc()
    
    def display_facts(self):
        """Display replay facts in compact format: Game and Player columns, Opponent in scrollable table."""
        # Clear existing facts
        for i in reversed(range(self.facts_layout.count())):
            widget = self.facts_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Clear opponent table
        self.opponent_table.setRowCount(0)
        
        if not self.replay_data:
            return
        
        # Helper function to clean list strings (remove brackets)
        def clean_list_value(value):
            value_str = str(value)
            if value_str.startswith('[') and value_str.endswith(']'):
                value_str = value_str[1:-1]
            return value_str
        
        # Prepare data
        outcome_map = {0: "Draw", 1: "Win", 2: "Loss", 3: "Abandoned"}
        outcome = outcome_map.get(self.replay_data.get("Outcome", 0), "Unknown")
        
        mode_map = {0: "vs AI", 1: "Arena"}
        mode = mode_map.get(self.replay_data.get("Mode", 0), "Unknown")
        
        # Column 0: Game Information
        col = 0
        row = 0
        
        # Column header - increased font size
        header = QLabel("Game")
        header_font = QFont("Arial", 10, QFont.Weight.Bold)
        header.setFont(header_font)
        self.facts_layout.addWidget(header, row, col)
        row += 1
        
        game_info = [
            ("Match ID", str(self.replay_data.get("MatchId", "N/A"))[:12]),
            ("Mode", mode),
            ("Outcome", outcome),
            ("Turns", str(self.replay_data.get("LastTurn", "N/A"))),
            ("Date", str(self.replay_data.get("CreatedOn", "N/A"))[:10]),
        ]
        if self.summary_row is not None:
            game_info.append(("Ranked", "Yes" if pd.notna(self.summary_row.get("rankedgame")) else "No"))
        
        for label, value in game_info:
            combined_text = f"{label}: {value}"
            text_widget = QLabel(combined_text)
            text_widget.setFont(QFont("Courier", 7))
            text_widget.setWordWrap(False)
            
            self.facts_layout.addWidget(text_widget, row, col)
            row += 1
        
        # Column 1: Player Information
        col = 1
        row = 0
        
        # Column header - increased font size
        header = QLabel("Player")
        header_font = QFont("Arial", 10, QFont.Weight.Bold)
        header.setFont(header_font)
        self.facts_layout.addWidget(header, row, col)
        row += 1
        
        player_info = [
            ("Username", str(self.replay_data.get("UserName", "N/A"))),
            ("User ID", str(self.replay_data.get("UserId", "N/A"))[:12]),
        ]
        if self.summary_row is not None:
            player_info.append(("Pack", str(self.summary_row.get("userpack", "N/A"))[:15]))
            player_info.append(("Rank", str(self.summary_row.get("userrank", "N/A"))))
        
        for label, value in player_info:
            combined_text = f"{label}: {value}"
            text_widget = QLabel(combined_text)
            text_widget.setFont(QFont("Courier", 7))
            text_widget.setWordWrap(False)
            
            self.facts_layout.addWidget(text_widget, row, col)
            row += 1
        
        # Add row stretch to push content to top
        self.facts_layout.setRowStretch(row, 1)
        
        # Populate opponent table (scrollable)
        opponent_names = []
        opponent_packs = []
        
        if self.summary_row is not None:
            # Get opponent name(s) from the summary column 'opp_namelist'
            opponent_name_raw = self.summary_row.get("opp_namelist") or self.summary_row.get("opponent") or "N/A"
            opponent_name_str = clean_list_value(str(opponent_name_raw))
            
            # Get opponent pack(s) from 'opp_packlist'
            opp_pack_raw = self.summary_row.get("opp_packlist") or self.summary_row.get("opp pack") or "N/A"
            opp_pack_str = clean_list_value(str(opp_pack_raw))
            
            # Split by comma to extract individual items
            opponent_names = [name.strip().strip("'\"") for name in opponent_name_str.split(',') if name.strip()]
            opponent_packs = [pack.strip().strip("'\"") for pack in opp_pack_str.split(',') if pack.strip()]
        
        # If parsing failed or no data, show single N/A row
        if not opponent_names:
            opponent_names = ["N/A"]
        if not opponent_packs:
            opponent_packs = ["N/A"]
        
        # Populate opponent table with matched rows
        max_opponents = max(len(opponent_names), len(opponent_packs))
        self.opponent_table.setRowCount(max_opponents)
        
        for i in range(max_opponents):
            # Column 0: Opponent Name
            name_value = opponent_names[i] if i < len(opponent_names) else "N/A"
            name_item = QTableWidgetItem(name_value[:25])
            name_item.setFont(QFont("Courier", 7))
            self.opponent_table.setItem(i, 0, name_item)
            
            # Column 1: Opponent Pack
            pack_value = opponent_packs[i] if i < len(opponent_packs) else "N/A"
            pack_item = QTableWidgetItem(pack_value[:20])
            pack_item.setFont(QFont("Courier", 7))
            self.opponent_table.setItem(i, 1, pack_item)
    
    def populate_y_axis_buttons(self):
        """Populate Y-axis radio buttons based on available action types."""
        # Clear existing buttons
        for button in self.y_axis_radio_buttons.values():
            button.deleteLater()
        self.y_axis_radio_buttons.clear()
        
        # Get available Y-axis options
        y_axes = self.timeline.get_available_y_axes()
        
        for idx, y_axis in enumerate(y_axes):
            radio_btn = QRadioButton(y_axis)
            radio_btn.setFont(QFont("Arial", 8))
            radio_btn.toggled.connect(self.on_y_axis_selected)
            
            # Check the first button (Lives) by default
            if idx == 0:
                radio_btn.setChecked(True)
            
            self.y_axis_radio_buttons[y_axis.lower()] = radio_btn
            self.y_axis_button_group.addButton(radio_btn, idx)
            self.y_axis_layout_container.addWidget(radio_btn)
        
        self.y_axis_layout_container.addStretch()
    
    def on_y_axis_selected(self):
        """Handle Y-axis radio button selection."""
        # Find which button is selected
        for key, button in self.y_axis_radio_buttons.items():
            if button.isChecked():
                self.timeline.y_axis_mode = key
                self.update_timeline()
                break

    def on_opp_selected(self):
        """Handle opponent selection from combo box (overlay)."""
        pid = self.opp_combo.currentData()
        # Save selected pid (None if 'None' or missing)
        self.selected_opp_pid = pid
        # Refresh timeline to show/hide overlay
        self.update_timeline()

    def on_opp_visibility_changed(self, item):
        """Handle changes to opponent visibility checkboxes."""
        # simply refresh overlays when visibility toggles
        self.update_timeline()

    def select_all_opponents(self):
        for i in range(self.opp_visibility_list.count()):
            item = self.opp_visibility_list.item(i)
            if item.flags() & Qt.ItemIsEnabled and item.flags() & Qt.ItemIsUserCheckable:
                item.setCheckState(Qt.Checked)

    def deselect_all_opponents(self):
        for i in range(self.opp_visibility_list.count()):
            item = self.opp_visibility_list.item(i)
            if item.flags() & Qt.ItemIsEnabled and item.flags() & Qt.ItemIsUserCheckable:
                item.setCheckState(Qt.Unchecked)

    def open_selected_opponent(self):
        """Open the selected opponent's replay as the active replay (if available)."""
        pid = self.opp_combo.currentData()
        if not pid:
            QMessageBox.information(self, "Opponent Replay", "Opponent replay missing or not selected.")
            return

        # If opponent data is available, switch to it
        opp_entry = self.opp_replays.get(pid)
        if not opp_entry or not opp_entry.get('available'):
            QMessageBox.information(self, "Opponent Replay", "Opponent replay file is not available locally.")
            return

        # Load opponent replay
        try:
            self.load_replay(pid)
        except Exception as e:
            QMessageBox.warning(self, "Open Replay", f"Failed to open opponent replay: {e}")
    
    def update_timeline(self):
        """Update the timeline visualization."""
        if not self.timeline.actions:
            return
        
        # Get x-axis mode from combo box
        x_axis_mode = "turns" if self.x_axis_combo.currentIndex() == 0 else "timestamp"
        
        # Get y-axis mode from selected radio button
        y_axis_mode = self.timeline.y_axis_mode.lower()
        
        # Get timeline data
        x_values, y_values = self.timeline.get_timeline_data(x_axis_mode, y_axis_mode)
        
        # Determine Y-axis label
        if y_axis_mode == "lives":
            y_axis_label = "Lives"
        elif y_axis_mode == "turn time":
            y_axis_label = "Turn Time"
        else:
            y_axis_label = f"{y_axis_mode.title()} Count"
        
        # Prepare overlays based on visibility list (default: show all opponents)
        overlays = []
        try:
            from matplotlib import cm, colors as mcolors
            palette = cm.get_cmap('tab10')
        except Exception:
            palette = None

        for i in range(self.opp_visibility_list.count()):
            item = self.opp_visibility_list.item(i)
            if not item or item.checkState() != Qt.Checked:
                continue
            pid = item.data(Qt.UserRole)
            if not pid:
                continue
            opp_entry = self.opp_replays.get(pid)
            if not opp_entry or not opp_entry.get('available') or not opp_entry.get('actions'):
                continue
            opp_actions = opp_entry.get('actions')
            opp_x, opp_y = ReplayTimelineVisualization.get_timeline_data_from_actions(opp_actions, x_axis_mode, y_axis_mode)
            color = None
            try:
                if palette is not None:
                    color = mcolors.to_hex(palette(hash(pid) % 10))
            except Exception:
                color = None

            overlays.append({
                'x': opp_x,
                'y': opp_y,
                'label': f"{opp_entry.get('name', 'Opponent')} ({str(pid)[:8]})",
                'color': color
            })

        if not overlays:
            overlays = None

        # Update chart
        self.timeline_view.plot_timeline(
            x_values,
            y_values,
            x_label="Turns" if x_axis_mode == "turns" else "Time (seconds)",
            y_label=y_axis_label,
            title=f"{y_axis_label} Over Time",
            x_axis_mode=x_axis_mode,
            y_axis_mode=y_axis_mode,
            actions=self.timeline.actions,
            overlays=overlays
        )
    
    def display_action_summary(self):
        """Display summary of actions."""
        summary = self.timeline.get_action_summary()
        
        text = f"Total Actions: {summary.get('total_actions', 0)}\n"
        text += f"Max Turn: {summary.get('max_turn', 0)}\n"
        text += f"Final Lives: {summary.get('final_lives', 0)}\n\n"
        text += "Action Breakdown:\n"
        
        action_counts = summary.get('action_counts', {})
        for action_type, count in sorted(action_counts.items()):
            text += f"  {action_type}: {count}\n"
        
        self.action_summary_text.setText(text)


class TimelineChartView(FigureCanvasQTAgg):
    """Custom chart view for displaying timeline data using matplotlib."""
    
    def __init__(self, parent=None):
        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        super().__init__(self.figure)
        self.setParent(parent)
    
    def plot_timeline(self, x_values, y_values, x_label="Turns", y_label="Lives", title="Lives Over Time", 
                      x_axis_mode="turns", y_axis_mode="lives", actions=None, overlays=None):
        """Plot timeline data."""
        self.ax.clear()
        
        if not x_values or not y_values:
            self.ax.text(0.5, 0.5, 'No data to display', 
                        horizontalalignment='center',
                        verticalalignment='center',
                        transform=self.ax.transAxes)
            self.draw()
            return
        
        # Determine if this is action count mode (scatter dots) or line chart
        is_action_count = (x_axis_mode == "turns" and y_axis_mode not in ["lives", "turn time"])
        
        # Marker types to cycle through (player first, then opponents)
        markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', '+']
        marker_idx = 0

        if is_action_count:
            # Plot action counts as scatter (dots) for player
            self.ax.scatter(x_values, y_values, color='steelblue', marker=markers[marker_idx % len(markers)], 
                          s=60, alpha=0.7, edgecolor='navy', linewidth=1, zorder=2, label='Player')
            marker_idx += 1
        else:
            # Plot main line chart (for Lives, Turn Time, etc.)
            self.ax.plot(x_values, y_values, color='b', marker='o', markersize=4, linewidth=2, zorder=2, label='Player')

        # Plot overlay series (opponents) if provided
        if overlays:
            try:
                from matplotlib import cm, colors as mcolors
                palette = cm.get_cmap('tab10')
                for idx, ov in enumerate(overlays):
                    ox = ov.get('x') or ov.get('x_values') or ov.get('x_values', [])
                    oy = ov.get('y') or ov.get('y_values') or ov.get('y_values', [])
                    label = ov.get('label', f'Overlay {idx+1}')
                    color = ov.get('color')
                    if not color:
                        # deterministic color per index
                        color = mcolors.to_hex(palette(idx % 10))

                    if is_action_count:
                        # For action counts, use distinct marker per opponent
                        try:
                            marker = markers[marker_idx % len(markers)]
                            self.ax.scatter(ox, oy, color=color, marker=marker, s=60, alpha=0.7, 
                                          edgecolor='none', linewidth=1, zorder=3, label=label)
                            marker_idx += 1
                        except Exception:
                            continue
                    else:
                        # For line charts, use dashed line with 'x' markers
                        try:
                            self.ax.plot(ox, oy, linestyle='--', marker='x', markersize=4, linewidth=1.5, 
                                       color=color, zorder=3, label=label)
                        except Exception:
                            continue
            except Exception:
                pass
        
        # Add turn interval background bands when using timestamp x-axis
        if x_axis_mode == "timestamp" and actions:
            self._add_turn_interval_bands(actions)
        
        # Configure axes and labels
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.set_title(title)
        self.ax.grid(True, alpha=0.3)
        
        # Set y-axis limits with minimum always at 0
        if y_values:
            y_min = min(y_values)
            y_max = max(y_values)
            
            # Include all overlay maximum values in y-axis scaling
            if overlays:
                try:
                    for ov in overlays:
                        oy = ov.get('y') or ov.get('y_values', [])
                        if oy:
                            overlay_max = max(oy)
                            y_max = max(y_max, overlay_max)
                except Exception:
                    pass
            
            # Ensure Y-axis minimum is always 0
            self.ax.set_ylim(0, y_max + 1)
            
            # For action count Y-axes (Buy Pet, Buy Food, etc.), use integer ticks
            if y_label not in ["Lives", "Turn Time (seconds)"]:
                from matplotlib.ticker import MaxNLocator
                self.ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        # Show legend for overlays if any
        if overlays:
            try:
                self.ax.legend(loc='best', fontsize='small')
            except Exception:
                pass

        self.figure.tight_layout()
        self.draw()
    
    def _add_turn_interval_bands(self, actions):
        """Add alternating background bands to indicate turn intervals."""
        if not actions:
            return
        
        try:
            from matplotlib.patches import Rectangle
            
            # Find turn start and end times
            turn_intervals = {}
            for action in actions:
                turn = action.get("Turn", 0)
                time_str = action.get("Time", "")
                
                if time_str:
                    try:
                        timestamp = parse_iso_timestamp(time_str)
                    except:
                        continue
                    
                    if turn not in turn_intervals:
                        turn_intervals[turn] = {"start": timestamp, "end": timestamp}
                    else:
                        turn_intervals[turn]["end"] = timestamp
            
            if not turn_intervals:
                return
            
            # Get x-axis limits
            x_min, x_max = self.ax.get_xlim()
            y_min, y_max = self.ax.get_ylim()
            
            # Calculate timestamps to seconds for x-axis positioning
            min_timestamp = None
            for turn in turn_intervals:
                ts = turn_intervals[turn]["start"]
                if min_timestamp is None or ts < min_timestamp:
                    min_timestamp = ts
            
            if not min_timestamp:
                return
            
            # Add alternating bands
            colors = ['white', '#AAAAAA']  # white and darker gray
            color_index = 0
            
            for turn in sorted(turn_intervals.keys()):
                start_ts = turn_intervals[turn]["start"]
                end_ts = turn_intervals[turn]["end"]
                
                # Convert to seconds for x-axis
                start_x = (start_ts - min_timestamp).total_seconds()
                end_x = (end_ts - min_timestamp).total_seconds()
                
                # Add a small padding to separate turns slightly
                end_x = end_x + 0.5
                
                # Create rectangle for this turn
                rect = Rectangle((start_x, y_min), end_x - start_x, y_max - y_min,
                               facecolor=colors[color_index % 2], edgecolor='none', alpha=0.3, zorder=0)
                self.ax.add_patch(rect)
                
                color_index += 1
            
            # Reapply grid on top
            self.ax.set_axisbelow(True)
            
        except Exception as e:
            print(f"Warning: Failed to add turn interval bands: {e}")
