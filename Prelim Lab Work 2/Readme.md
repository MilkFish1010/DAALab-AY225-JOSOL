
# Lab 2: Multi-Algorithm Benchmarking Tool

## Project Overview
**MilkFish Sort** is a **GUI-based** multi-algorithm sorting benchmarking tool that implements and compares three distinct sorting algorithms with real-time performance analysis.

## Algorithms Implemented

### 1. **Bubble Sort** - O(n²)
- Simple exchange sort that repeatedly steps through the list
- Swaps adjacent elements if they're in the wrong order
- Best for: Small datasets
- Worst case: Quadratic time complexity

### 2. **Insertion Sort** - O(n²)
- Builds the sorted array one item at a time
- Efficient for small and partially sorted datasets
- Best for: Small to medium datasets
- Worst case: Quadratic time complexity

### 3. **Merge Sort** - O(n log n)
- Divide-and-conquer algorithm
- Recursively divides array and merges sorted subarrays
- Best for: Large datasets
- Guaranteed: O(n log n) performance

## Features

### 🎯 Core Functionality
- **Three sorting algorithms** with independent implementations
- **Auto Sort** - Intelligently selects optimal algorithm based on dataset size
- **Real-time timer** with millisecond precision (updates every 50ms)
- **Progress tracking** for long-running sorts
- **Data verification** confirming sorted output

### 🎨 GUI Interface (Tkinter)
- Import custom datasets or use default (10,000 elements)
- Individual algorithm buttons for manual selection
- **AUTO SORT button** (gold) for automatic optimization
- Real-time timer display during sorting
- Separate panels for output and detailed reports
- Scrollable text areas for large data display

### 🖥️ Terminal Interface
- Menu-driven console option
- Same algorithm selection capability
- Command-line reporting

## Performance Optimizations

### Lag Reduction
1. **Reduced callback overhead**: Progress updates reduced from 50 to 100 intervals
2. **Independent timer updates**: Timer runs separately from progress bar (50ms refresh)
3. **Threading**: Sorting runs in background thread, keeping UI responsive
4. **Efficient UI updates**: Non-blocking `root.after()` calls for smooth interaction

### Real-Time Timer
- Updates every 50ms for smooth, fluid display
- Independent of sorting algorithm speed
- Automatically syncs with actual elapsed time when sort completes
- No artificial progress-like behavior

## Installation & Usage

### Requirements
```bash
# Only Tkinter is required (included with Python)
python 3.7+
```

### Running the Program

**GUI Mode:**
```bash
python MilkFishSort.py
```
Then select "Launch GUI Mode" or run directly if set to GUI startup.

**Terminal Mode:**
```bash
python MilkFishSort.py
```
Select option 1-4 for manual sorts or option 5 for GUI.

## File Structure
```
LAB-1/
├── MilkFishSort.py       # Main program (GUI + Terminal)
├── dataset.txt           # Default dataset (10,000 random integers)
└── README.md            # This file
```

## How It Works

### Auto Sort Algorithm
- **Dataset < 50 elements**: Uses Insertion Sort (O(n²) but better constant factors)
- **Dataset ≥ 50 elements**: Uses Merge Sort (O(n log n) advantage becomes significant)

### Benchmarking Process
1. User selects algorithm and loads dataset
2. Timer starts when sort begins
3. Progress bar updates show sort completion percentage
4. Real-time timer counts elapsed seconds
5. Upon completion:
   - Actual elapsed time displayed
   - Algorithm timer (internal sort time) shown separately
   - Sorted output verified
   - Performance report generated

## Lab Requirements Compliance ✓
- [x] Three distinct algorithms (Bubble, Insertion, Merge Sort)
- [x] GUI Interface (Tkinter-based)
- [x] Dynamic input handling (Import custom datasets)
- [x] Execution timing (excluding data generation)
- [x] Array verification (Output confirms sort correctness)
- [x] Separate functions for each algorithm (no spaghetti code)
- [x] Auto sort function for intelligent algorithm selection
- [x] Real-time timer (independent, smooth updates)
- [x] Lag optimization (reduced callbacks, efficient threading)


---
**Lab 2 - Comparative Analysis of Sorting Algorithms**
