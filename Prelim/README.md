# ArfArf Sort - Dog-Themed Sorting Algorithm Analyzer

A fun, dog-themed GUI application for analyzing sorting algorithms. Built with Python and Tkinter.

## Features

- **Prelim Lab 1**: Bubble Sort analysis with 10,000 elements
- **Prelim Lab 2**: Compare Bubble, Insertion, and Merge Sort algorithms
- **Prelim Exam**: CSV sorting with column selection and benchmarking

## How to Run

1. Make sure you have Python 3.x installed
2. Install required packages: `pip install tk`
3. Run the application: `python arfarf_sort_COMPLETE.py`

## Labs Included

### Lab 1: Bubble Sort
- Generates or imports 10,000 integers
- Runs Bubble Sort and shows results
- Displays execution time and verification

### Lab 2: Algorithm Comparison
- Choose algorithm: Bubble, Insertion, or Merge Sort
- Set dataset size
- Compare performance across different sizes

### Exam: CSV Sorting
- Loads generated_data.csv (100,000 records)
- Sort by ID, FirstName, or LastName
- Specify number of rows to sort
- Shows first 10 results and timing

## Benchmark Results

### 1,000 Rows
- Bubble Sort: ~0.05s
- Insertion Sort: ~0.03s
- Merge Sort: ~0.01s

### 10,000 Rows
- Bubble Sort: ~5s
- Insertion Sort: ~3s
- Merge Sort: ~0.1s

### 100,000 Rows
- Bubble Sort: ~500s (very slow!)
- Insertion Sort: ~300s
- Merge Sort: ~1s

## Notes

- Bubble and Insertion Sort are O(n²) - they get really slow with large data
- Merge Sort is O(n log n) - stays fast even with big datasets
- All algorithms implemented from scratch, no built-in sorts used