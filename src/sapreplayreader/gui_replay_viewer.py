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
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from sapreplayreader import reader

# Use matplotlib for timeline visualization instead of PyQt charts
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class ReplayTimelineVisualization:
    """Handles timeline visualization data and rendering."""
    
    def __init__(self):
        self.actions = []
        self.x_axis_mode = "turns"  # Can be "turns" or "timestamp"
    
    def load_actions(self, pid: str):
        """Load and process actions from a replay."""
        try:
            self.actions = reader.extract_actions(pid)
            return True
        except Exception as e:
            print(f"Error loading actions: {e}")
            return False
    
    def get_timeline_data(self, x_axis_mode="turns"):
        """Get timeline data for plotting."""
        self.x_axis_mode = x_axis_mode
        
        if not self.actions:
            return [], []
        
        x_values = []
        y_values = []
        
        for action in self.actions:
            if x_axis_mode == "turns":
                x = action.get("Turn", 0)
            else:  # timestamp
                # Parse timestamp to a numeric value (seconds since start)
                time_str = action.get("Time", "")
                if x_values and "timestamp_base" in locals():
                    # Calculate seconds from first timestamp
                    try:
                        current_time = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                        x = (current_time - timestamp_base).total_seconds()
                    except:
                        x = len(x_values)
                else:
                    if not x_values and time_str:
                        try:
                            timestamp_base = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                        except:
                            pass
                    x = len(x_values)
            
            lives = action.get("Lives", 0)
            
            x_values.append(x)
            y_values.append(lives)
        
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
                summary_df = pd.read_csv('summary.csv')
                self.summary_row = summary_df[summary_df['pid'] == pid].iloc[0] if pid in summary_df['pid'].values else None
            except:
                self.summary_row = None
            
            # Load and process actions
            try:
                self.timeline.load_actions(pid)
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
    
    def update_timeline(self):
        """Update the timeline visualization."""
        if not self.timeline.actions:
            return
        
        # Get x-axis mode from combo box
        x_axis_mode = "turns" if self.x_axis_combo.currentIndex() == 0 else "timestamp"
        
        # Get timeline data
        x_values, y_values = self.timeline.get_timeline_data(x_axis_mode)
        
        # Update chart
        self.timeline_view.plot_timeline(
            x_values,
            y_values,
            x_label="Turns" if x_axis_mode == "turns" else "Time (seconds)",
            title="Lives Over Time"
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
    
    def plot_timeline(self, x_values, y_values, x_label="Turns", title="Lives Over Time"):
        """Plot timeline data."""
        self.ax.clear()
        
        if not x_values or not y_values:
            self.ax.text(0.5, 0.5, 'No data to display', 
                        horizontalalignment='center',
                        verticalalignment='center',
                        transform=self.ax.transAxes)
            self.draw()
            return
        
        # Plot the line
        self.ax.plot(x_values, y_values, 'b-', marker='o', markersize=4, linewidth=2)
        
        # Configure axes and labels
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel('Lives')
        self.ax.set_title(title)
        self.ax.grid(True, alpha=0.3)
        
        # Set y-axis limits
        if y_values:
            y_min = min(y_values)
            y_max = max(y_values)
            self.ax.set_ylim(max(0, y_min - 1), y_max + 1)
        
        self.figure.tight_layout()
        self.draw()
