"""
Replay Summary Tab for SAP Replay Reader GUI.
Displays and filters replay data from summary.csv with table view and replay selection.
"""

import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QLabel, QSpinBox,
    QCheckBox, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class ReplaySummaryTab(QWidget):
    """Tab for browsing and filtering replays from summary.csv."""
    
    replay_selected = pyqtSignal(str)  # Signal passes the PID
    
    def __init__(self, on_replay_selected_callback=None):
        super().__init__()
        self.on_replay_selected_callback = on_replay_selected_callback
        self.summary_df = None
        self.filtered_df = None
        self.init_ui()
        self.load_summary_data()
    
    def init_ui(self):
        """Initialize the UI for the replay summary tab."""
        layout = QHBoxLayout()
        
        # Left panel: Filter options
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Filters:"))
        left_layout.setSpacing(8)
        
        # Username filter
        left_layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Filter by username...")
        self.username_input.textChanged.connect(self.apply_filters)
        left_layout.addWidget(self.username_input)
        
        # Opponent name filter
        left_layout.addWidget(QLabel("Opponent:"))
        self.opponent_input = QLineEdit()
        self.opponent_input.setPlaceholderText("Filter by opponent...")
        self.opponent_input.textChanged.connect(self.apply_filters)
        left_layout.addWidget(self.opponent_input)
        
        # Outcome filter
        left_layout.addWidget(QLabel("Outcome:"))
        self.outcome_combo = QComboBox()
        self.outcome_combo.addItems(["All", "Win (1)", "Loss (2)", "Draw (0)", "Abandoned (3)"])
        self.outcome_combo.currentIndexChanged.connect(self.apply_filters)
        left_layout.addWidget(self.outcome_combo)
        
        # Game Mode filter
        left_layout.addWidget(QLabel("Game Mode:"))
        self.gamemode_combo = QComboBox()
        self.gamemode_combo.addItems(["All", "Standard (0)", "Weekly (1)", "Custom (2)"])
        self.gamemode_combo.currentIndexChanged.connect(self.apply_filters)
        left_layout.addWidget(self.gamemode_combo)
        
        # Ranked game filter
        self.ranked_checkbox = QCheckBox("Ranked Games Only")
        self.ranked_checkbox.stateChanged.connect(self.apply_filters)
        left_layout.addWidget(self.ranked_checkbox)
        
        # Min turns filter
        left_layout.addWidget(QLabel("Min Turns:"))
        self.min_turns_spin = QSpinBox()
        self.min_turns_spin.setValue(0)
        self.min_turns_spin.setMaximum(100)
        self.min_turns_spin.valueChanged.connect(self.apply_filters)
        left_layout.addWidget(self.min_turns_spin)
        
        # Clear filters button
        clear_btn = QPushButton("Clear Filters")
        clear_btn.clicked.connect(self.clear_filters)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        left_layout.addWidget(clear_btn)
        
        # Result count label
        self.count_label = QLabel("Replays: 0")
        self.count_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        left_layout.addWidget(self.count_label)
        
        left_layout.addStretch()
        left_panel = QWidget()
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(200)
        
        # Right panel: Table
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Summary Data:"))
        
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "Username", "Opponent", "Outcome", "Turns", "Mode", "Ranked",
            "User Pack", "Opp Pack", "User Rank", "Date", "PID", "Match ID"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setColumnHidden(10, True)  # Hide PID column (but keep it available)
        self.table.setColumnHidden(11, True)  # Hide Match ID column
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(self.table.SelectionMode.SingleSelection)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)  # Read-only
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        right_layout.addWidget(self.table)
        
        # Button to view selected replay
        view_btn = QPushButton("View Selected Replay")
        view_btn.clicked.connect(self.view_selected_replay)
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        right_layout.addWidget(view_btn)
        
        layout.addWidget(left_panel)
        layout.addLayout(right_layout, 1)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.setLayout(layout)
    
    def load_summary_data(self):
        """Load summary data from CSV file."""
        try:
            self.summary_df = pd.read_csv('data/summary.csv')
            self.filtered_df = self.summary_df.copy()
            self.populate_table()
        except FileNotFoundError:
            # Silently handle missing file - table stays empty with helpful message in console
            self.summary_df = None
            self.filtered_df = None
            self.table.setRowCount(0)
        except Exception as e:
            # Silently handle errors - let user try to generate data from Data Processing tab
            print(f"Error loading summary data: {e}")
            self.summary_df = None
            self.filtered_df = None
            self.table.setRowCount(0)
    
    def apply_filters(self):
        """Apply all active filters to the data."""
        if self.summary_df is None:
            return
        
        self.filtered_df = self.summary_df.copy()
        
        # Username filter
        username = self.username_input.text().strip()
        if username:
            self.filtered_df = self.filtered_df[
                self.filtered_df['username'].astype(str).str.contains(username, case=False, na=False)
            ]
        
        # Opponent filter
        opponent = self.opponent_input.text().strip()
        if opponent:
            self.filtered_df = self.filtered_df[
                self.filtered_df['opp_namelist'].astype(str).str.contains(opponent, case=False, na=False)
            ]
        
        # Outcome filter
        outcome_idx = self.outcome_combo.currentIndex()
        if outcome_idx > 0:
            outcome_values = {1: 1, 2: 2, 3: 0, 4: 3}
            self.filtered_df = self.filtered_df[self.filtered_df['outcome'] == outcome_values[outcome_idx]]
        
        # Game mode filter
        gamemode_idx = self.gamemode_combo.currentIndex()
        if gamemode_idx > 0:
            gamemode_values = {1: 0, 2: 1, 3: 2}
            self.filtered_df = self.filtered_df[self.filtered_df['gamemode'] == gamemode_values[gamemode_idx]]
        
        # Ranked games filter
        if self.ranked_checkbox.isChecked():
            self.filtered_df = self.filtered_df[self.filtered_df['rankedgame'].astype(str) != 'nan']
        
        # Min turns filter
        min_turns = self.min_turns_spin.value()
        if min_turns > 0:
            self.filtered_df = self.filtered_df[self.filtered_df['turns'] >= min_turns]
        
        self.populate_table()
    
    def clear_filters(self):
        """Clear all filters."""
        self.username_input.clear()
        self.opponent_input.clear()
        self.outcome_combo.setCurrentIndex(0)
        self.gamemode_combo.setCurrentIndex(0)
        self.ranked_checkbox.setChecked(False)
        self.min_turns_spin.setValue(0)
    
    def populate_table(self):
        """Populate the table with filtered data."""
        if self.filtered_df is None or len(self.filtered_df) == 0:
            self.table.setRowCount(0)
            self.count_label.setText("Replays: 0")
            return
        
        self.table.setRowCount(len(self.filtered_df))
        
        for row, (idx, record) in enumerate(self.filtered_df.iterrows()):
            # Column 0: Username
            self.table.setItem(row, 0, QTableWidgetItem(str(record.get('username', ''))))
            
            # Column 1: Opponent names
            opp_names = str(record.get('opp_namelist', ''))
            self.table.setItem(row, 1, QTableWidgetItem(opp_names[:50]))  # Truncate for display
            
            # Column 2: Outcome mapping
            outcome_map = {1: "Win", 2: "Loss", 0: "Draw", 3: "Abandoned"}
            outcome = outcome_map.get(record.get('outcome', 0), str(record.get('outcome', '')))
            self.table.setItem(row, 2, QTableWidgetItem(outcome))
            
            # Column 3: Turns
            self.table.setItem(row, 3, QTableWidgetItem(str(record.get('turns', ''))))
            
            # Column 4: Game mode mapping
            gamemode_map = {0: "Standard", 1: "Weekly", 2: "Custom"}
            gamemode = gamemode_map.get(record.get('gamemode', 0), str(record.get('gamemode', '')))
            self.table.setItem(row, 4, QTableWidgetItem(gamemode))
            
            # Column 5: Ranked
            ranked = "Yes" if pd.notna(record.get('rankedgame')) and record.get('rankedgame') != 'nan' else "No"
            self.table.setItem(row, 5, QTableWidgetItem(ranked))
            
            # Column 6: User pack
            self.table.setItem(row, 6, QTableWidgetItem(str(record.get('userpack', ''))))
            
            # Column 7: Opponent pack list
            opp_pack = str(record.get('opp_packlist', ''))
            self.table.setItem(row, 7, QTableWidgetItem(opp_pack[:40] if opp_pack else ''))  # Truncate for display
            
            # Column 8: User rank
            user_rank = record.get('userrank', '')
            self.table.setItem(row, 8, QTableWidgetItem(str(user_rank) if pd.notna(user_rank) else ''))
            
            # Column 9: Date
            date_str = str(record.get('datestart', ''))[:10]  # Take just the date part
            self.table.setItem(row, 9, QTableWidgetItem(date_str))
            
            # Column 10: PID (hidden)
            self.table.setItem(row, 10, QTableWidgetItem(str(record.get('pid', ''))))
            
            # Column 11: Match ID (hidden)
            self.table.setItem(row, 11, QTableWidgetItem(str(record.get('matchid', ''))))
        
        self.count_label.setText(f"Replays: {len(self.filtered_df)}")
    
    def view_selected_replay(self):
        """Switch to replay viewer for the selected replay."""
        current_row = self.table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a replay to view.")
            return
        
        # Get PID from hidden column (column 10)
        pid_item = self.table.item(current_row, 10)
        if pid_item:
            pid = pid_item.text()
            if self.on_replay_selected_callback:
                self.on_replay_selected_callback(pid)
            else:
                self.replay_selected.emit(pid)
