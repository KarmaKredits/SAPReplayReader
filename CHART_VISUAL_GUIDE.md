# Visual Guide: Chart Visualization Features

Quick visual reference for the three chart visualization features in SAP Replay Reader.

## Feature 1: Histogram Chart (Action Counts by Turn)

### When to Use
- **X-axis**: Turns (1, 2, 3, ...)
- **Y-axis**: Any action type (Buy Pet, Buy Food, Combine Pet, Roll, Sell Pet)

### Visual Example
```
Buy Pet Count Per Turn

        |
      3 |  ███
        |  ███  ███
      2 |  ███  ███
        |  ███  ███  ███
      1 |  ███  ███  ███
        |__________________
          1    2    3    4
          Turn Number
```

### Characteristics
- **Chart Type**: Bar chart (histogram)
- **Bar Color**: Steel blue (#4682B4)
- **Edge Color**: Navy
- **Transparency**: 70% (alpha=0.7)
- **Y-Values**: Whole numbers only (1, 2, 3, ...)
- **Reset**: Counts reset at each turn boundary

### Use Cases
- Compare pet purchases across turns
- Identify which turns had most buying activity
- Spot behavioral patterns by turn

---

## Feature 2: Line Chart (Continuous Metrics)

### When to Use
- **X-axis**: Turns OR Timestamp
- **Y-axis**: Lives or Turn Time

### Visual Example - Lives Over Turns
```
Lives Over Game

6 |●
  | \
5 |  ●
  |   \●
4 |      ●
  |       \
3 |        ●
  |         ●
2 |________●
  |
  1  2  3  4  5
  Turn Number
```

### Visual Example - Turn Time Over Turns
```
Turn Duration by Turn

100 |  ●--●
    |     \
 80 |      ●--●
    |          \
 60 |           ●
    |____________
    1  2  3  4  5
    Turn Number
```

### Characteristics
- **Chart Type**: Line chart with markers
- **Line Color**: Blue
- **Marker**: Circular dots
- **Marker Size**: 4 pixels
- **Line Width**: 2 pixels
- **Connection**: Points connected by straight lines

### Use Cases
- Track how lives change each turn
- Monitor turn duration trends
- Identify critical decision points

---

## Feature 3: Turn Interval Bands (Timestamp X-Axis)

### When to Use
- **X-axis**: Timestamp (continuous time)
- **Y-axis**: Any metric (Lives, Turn Time, or action counts)

### Visual Example
```
Lives Over Time with Turn Separation

Lives
  6 |    ●      ●
    |   / \    / \
  5 |  ●   ●  ●   ●
    | /     \/     \
  4 |●             ●
    |_______________
    |Turn 1|Turn 2|Turn 3|
    White  Gray   White
    ^^     ^^     ^^
    Turn boundaries
```

### Band Details
- **Color Pattern**: Alternating white and darker gray (#AAAAAA)
- **Turn 1**: White background
- **Turn 2**: Darker gray background
- **Turn 3**: White background
- **Turn 4**: Darker gray background
- **... and so on**

### Characteristics
- **Band Heights**: Full height of chart area
- **Band Width**: Duration of that turn (based on timestamps)
- **Opacity**: 100% opaque (fully visible)
- **Background Layer**: Behind data points and lines
- **Calculation**: Automatic from action timestamps

### Use Cases
- See turn boundaries in continuous timeline
- Correlate timestamp-based data with specific turns
- Navigate to specific turns chronologically
- Identify temporal patterns

---

## Side-by-Side Comparison

### Action Count Visualization

| Feature | Histogram | Line Chart |
|---------|-----------|-----------|
| **X-Axis** | Turns (1, 2, 3...) | Turns OR Timestamp |
| **Y-Data** | Buy Pet, Buy Food, etc. | Lives, Turn Time |
| **Shape** | Vertical bars | Connected line with dots |
| **Values** | Per-turn count (resets) | Continuous values |
| **Color** | Steel blue bars | Blue line |
| **Best For** | Compare action frequency | Track metric changes |

### Timeline Visualization

| Feature | Timestamp + Line Chart | Timestamp + Bands |
|---------|----------------------|-------------------|
| **Background** | White only | Alternating white/gray bands |
| **Purpose** | Line chart rendering | Visual turn separation |
| **Interaction** | Works together | Works together |
| **Effect** | Clean data visualization | Clearer turn boundaries |

---

## Decision Tree: Which Chart to Use?

```
START
  |
  +-- Do you want to see ACTION COUNTS?
  |    |
  |    +-- YES, by TURN
  |    |    → Use Histogram (X-axis: Turns, Y-axis: Action type)
  |    |
  |    +-- YES, over TIME
  |         → Use Line Chart (X-axis: Timestamp, Y-axis: Action type)
  |         → Add Turn Bands for clarity
  |
  +-- Do you want to see CONTINUOUS METRICS (Lives, Turn Time)?
       |
       +-- YES, DISCRETE BY TURN
       |    → Use Line Chart (X-axis: Turns, Y-axis: Lives/Turn Time)
       |
       +-- YES, CONTINUOUS OVER TIME
            → Use Line Chart (X-axis: Timestamp, Y-axis: Lives/Turn Time)
            → Add Turn Bands for clarity
```

---

## Color Reference

### Histogram Chart
- **Bar Fill**: Steel Blue (#4682B4)
- **Bar Edge**: Navy (#000080)
- **Background**: White

### Line Chart
- **Line**: Blue (#0000FF)
- **Markers**: Blue (#0000FF)
- **Background**: White

### Turn Interval Bands
- **Odd Turns**: White (#FFFFFF)
- **Even Turns**: Darker Gray (#AAAAAA)
- **Band Edge**: None (seamless)

---

## Interactive Tips

### Histogram Viewing
1. Bars represent action count in each turn
2. Taller bar = more actions in that turn
3. No bar for a turn = 0 actions of that type that turn
4. Easily compare across turns at a glance

### Line Chart Viewing
1. Upward slope = metric increasing
2. Downward slope = metric decreasing
3. Flat line = metric stayed same
4. Each dot marks actual data point

### Turn Band Viewing
1. Bands help you identify "chunks" in continuous time
2. Each band = one complete game turn
3. Alternating colors make boundaries clear
4. Helpful when timeline spans many turns

---

## Example Scenarios

### Scenario 1: Analyzing Pet Purchases
```
Show: X-axis = Turns, Y-axis = Buy Pet
Result: HISTOGRAM
What you see: Bar height = pets bought that turn
Analysis: Turn 3 has 5 bars → 5 pets bought in Turn 3
```

### Scenario 2: Tracking Lives Across Game
```
Show: X-axis = Turns, Y-axis = Lives
Result: LINE CHART
What you see: Line showing life progression
Analysis: Lives drop from 6 to 4 over first 3 turns
```

### Scenario 3: Detailed Timeline Analysis
```
Show: X-axis = Timestamp, Y-axis = Lives
Result: LINE CHART with TURN BANDS
What you see: Lives over continuous time with turn markers
Analysis: See exactly when lives dropped, which turn, duration
```

---

## Performance Notes

- **Small Replays** (< 100 actions): All features instant
- **Medium Replays** (100-1000 actions): All features fast (< 1 second)
- **Large Replays** (> 1000 actions): All features responsive (1-3 seconds)

---

## Troubleshooting

### Histogram Not Appearing
- Check: X-axis is set to "Turns"
- Check: Y-axis is an action type, not Lives/Turn Time
- Check: Replay has action data loaded

### Line Chart Not Smooth
- Normal: Discrete data points are connected
- Fix: Use more granular X-axis if available

### Turn Bands Not Visible
- Check: X-axis is set to "Timestamp"
- Check: Bands should be behind the lines/data
- Zoom: Use chart zoom/pan to inspect details

---

## Related Documentation
- [CHART_FEATURES.md](CHART_FEATURES.md) - Detailed technical documentation
- [GUI_README.md](GUI_README.md) - GUI feature documentation
- [GUI_TROUBLESHOOTING.md](GUI_TROUBLESHOOTING.md) - Troubleshooting guide
