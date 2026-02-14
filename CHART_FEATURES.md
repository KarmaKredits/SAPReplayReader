# Chart Visualization Features

This document describes the advanced chart visualization features available in the SAP Replay Reader GUI.

## Overview

The replay timeline viewer provides three main visualization modes:

1. **Histogram Rendering** - For action count data
2. **Line Chart Rendering** - For continuous metrics
3. **Turn Interval Bands** - For timestamp-based navigation

## Feature 1: Histogram Rendering (Turn X-Axis)

### When It Applies
- **X-axis:** Turns
- **Y-axis:** Any action type (Buy Pet, Buy Food, Combine Pet, Roll, Sell Pet)

### Characteristics
- Displays as a **bar chart** instead of a line chart
- Each bar represents the count of actions in that turn
- Y-axis values are **whole numbers** (1, 2, 3, etc.)
- Bars are colored in **steelblue** with **navy edge**
- Alpha (transparency) set to 0.7 for better visibility

### Visual Example
```
Buy Pet Actions Per Turn
       |
     3 |  ███       ███
     2 |  ███  ███  ███
     1 |  ███  ███  ███
       |__________________
         1    2    3    4   (Turn Number)
```

### Use Cases
- Compare action frequencies across turns
- Identify which turns had the most pet purchases
- Spot patterns in player behavior per turn

---

## Feature 2: Line Chart Rendering (Continuous Metrics)

### When It Applies
- **X-axis:** Turns or Timestamp
- **Y-axis:** Lives or Turn Time

### Characteristics
- Displays as a **line chart** with circular markers
- Line represents continuous changes in the metric
- Markers indicate individual data points
- Connected points show the trend over time
- Line width: 2px, marker size: 4px

### Visual Example
```
Lives Over Time
  |
6 |●
  | \
5 |   ●
  |    \
4 |      ●●
  |        \
3 |         ●
  |__________
   1  2  3  4 (Turn Number)
```

### Use Cases
- Track how many lives the player has at each turn
- Monitor turn duration trends
- Identify critical points where metrics changed significantly

---

## Feature 3: Turn Interval Bands (Timestamp X-Axis)

### When It Applies
- **X-axis:** Timestamp
- **Y-axis:** Any metric (Lives, Turn Time, or action counts)

### Characteristics
- Background divided into **alternating bands**
- Each band represents **one game turn**
- Bands use **white** and **darker gray** (#AAAAAA) colors
- Bands automatically calculated based on action timestamps
- Helps visualize turn boundaries in a continuous timeline

### Visual Example
```
Lives Over Time (Continuous Timeline)

White     Gray      White     Gray
────────────────────────────────────────
│ Turn 1  │ Turn 2  │ Turn 3  │ Turn 4│
│  ●      │ ●       │ ●       │ ●     │
│   ●     │  ●      │  ●      │  ●    │
│    ●    │   ●     │   ●     │   ●   │
────────────────────────────────────────
```

### Use Cases
- Correlate timeline metrics with specific turns
- Identify when turns occurred chronologically
- Spot temporal patterns in action sequences
- Navigate to specific turns within the game timeline

---

## Data Properties

### Per-Turn Action Counts
- Counts **reset** at turn boundaries (not cumulative)
- Maximum value per turn equals actual count in that turn
- Turn 1 might have 3 Buy Pets → Y goes 1, 2, 3
- Turn 2 might have 2 Buy Pets → Y resets to 1, 2
- Turn 3 might have 1 Buy Pet → Y shows only 1

### Y-Axis Minimum
- **Always set to 0** for all action-type axes
- Ensures consistent visual comparison across turns

### Timestamp Format
- Automatically parsed from ISO 8601 format
- Handles variable microsecond precision gracefully
- Converts to elapsed seconds for readable X-axis

---

## Implementation Details

### File: `src/sapreplayreader/gui_replay_viewer.py`

#### Key Methods

**`plot_timeline()`**
```python
def plot_timeline(self, x_values, y_values, x_label="", y_label="",
                  title="", x_axis_mode="turns", y_axis_mode="lives",
                  actions=None):
    """
    Render the timeline chart with appropriate visualization type.
    
    Parameters:
    - x_axis_mode: "turns" or "timestamp"
    - y_axis_mode: "buy pet", "lives", "turn time", etc.
    - actions: List of action dictionaries for band calculations
    """
```

**Histogram Logic**
```python
is_histogram = (x_axis_mode == "turns" and 
                y_axis_mode not in ["lives", "turn time"])
if is_histogram:
    self.ax.bar(x_values, y_values, color='steelblue', 
                edgecolor='navy', alpha=0.7)
else:
    self.ax.plot(x_values, y_values, 'b-', marker='o', 
                 markersize=4, linewidth=2)
```

**Turn Interval Band Logic**
```python
if x_axis_mode == "timestamp" and actions:
    self._add_turn_interval_bands(actions)
```

**`_add_turn_interval_bands()`**
- Calculates turn start/end from action timestamps
- Creates Rectangle patches with alternating colors
- Adds patches as background layer to chart

---

## Axis Options Available

### X-Axis Options
- **Turns** - Game turn numbers (1, 2, 3, ...)
- **Timestamp** - Elapsed seconds from game start

### Y-Axis Options
- **Buy Pet** - Number of Buy Pet actions
- **Buy Food** - Number of Buy Food actions
- **Combine Pet** - Number of Combine Pet actions
- **Roll** - Number of Roll actions
- **Sell Pet** - Number of Sell Pet actions
- **Lives** - Remaining lives (continuous metric)
- **Turn Time** - Duration of each turn in seconds (continuous metric)

### Chart Rendering Rules
| X-Axis | Y-Axis | Chart Type | Background |
|--------|--------|------------|------------|
| Turns | Action | Histogram | ✗ |
| Turns | Lives/Turn Time | Line | ✗ |
| Timestamp | Any | Line | ✓ (Turn bands) |

---

## Example Usage

### In GUI
1. Open replay selection dialog
2. Select a replay file
3. Choose X-axis: "Turns" or "Timestamp"
4. Choose Y-axis: "Buy Pet", "Lives", etc.
5. Chart automatically renders with appropriate visualization

### Programmatically
```python
from gui_replay_viewer import ReplayTimelineVisualization, TimelineChartView

viz = ReplayTimelineVisualization()
viz.load_actions(replay_id)

# Get data for histogram
x_vals, y_vals = viz.get_timeline_data(x_axis_mode="turns", 
                                       y_axis_mode="buy pet")

# Create and render chart
chart = TimelineChartView()
chart.plot_timeline(x_vals, y_vals,
                    title="Buy Pet Actions",
                    x_axis_mode="turns",
                    y_axis_mode="buy pet",
                    actions=viz.actions)
```

---

## Testing

Run the comprehensive feature demonstration:
```bash
python test_chart_features.py
```

This test:
- ✓ Verifies histogram rendering for action counts
- ✓ Verifies line chart rendering for Lives
- ✓ Verifies turn interval bands for timestamp axis
- ✓ Tests with actual replay data

---

## Troubleshooting

### Charts Not Showing
- Ensure replay file is selected
- Check that X-axis and Y-axis modes are valid
- Verify replay data is loading correctly

### Bands Not Visible
- Ensure X-axis is set to "Timestamp"
- Check that action data is being loaded
- Verify matplotlib is using interactive backend

### Performance Issues
- For large replays (>1000 actions), rendering may be slower
- Consider filtering to specific turn ranges
- Chart auto-scales and should handle data correctly

---

## Related Documentation
- [README.md](README.md) - Project overview
- [QUICKSTART_GUI.md](QUICKSTART_GUI.md) - GUI quickstart guide
- [GUI_README.md](GUI_README.md) - Detailed GUI documentation
- [GUI_TROUBLESHOOTING.md](GUI_TROUBLESHOOTING.md) - Troubleshooting guide
