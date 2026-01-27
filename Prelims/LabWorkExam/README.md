# Prelim Exam: CSV Sorting

## What This Lab Is About
This lab lets you work with a big list of information, like names and IDs from a file. You'll learn how to organize this data by sorting it in different ways. You can sort by ID numbers, first names, or last names, and choose how many items to sort. It's a way to see how quickly different methods can arrange large amounts of data, and you can save your results or run tests to compare speeds.

## Step-by-Step Instructions
1. **Start the App**: Open the exam application. It will show a main menu where you can choose the exam lab.
2. **Load Your Data**:
   - The app tries to load a file called `generated_data.csv` automatically from the `data` folder.
   - If it doesn't load, click "Load CSV File" to choose your own file. The file should have columns for ID, FirstName, and LastName.
   - Or, click "Generate Sample Data" to create a new file with 100,000 random entries.
3. **Set Up Your Sort**:
   - **Number of Rows**: Enter how many items from the file you want to sort (e.g., 1000 or 10000).
   - **Sort by Column**: Choose what to sort by: ID, FirstName, or LastName.
   - **Algorithm**: Pick the sorting method: Bubble Sort, Insertion Sort, or Merge Sort.
   - **Sort Order**: Choose Ascending (smallest to largest) or Descending (largest to smallest).
   - **Options**: Check "Show Timer" to see how long it takes, "Show Progress Bar" to watch the progress, or "Display first 10 records only" to show just the top 10 results.
4. **Run the Sort**: Click "Run Sort" to start. You can stop it anytime with the "Stop" button.
5. **View Results**: The app will show the sorted list in a table, how long it took, and a report. The original data is shown on the left, sorted on the right.
6. **Run a Benchmark**: Click "Benchmark" to test the sorting method on different sizes (1000, 10000, 100000 rows) and see the times.
7. **Export**:
   - "Export Report" saves the full details to a text file.
   - "Export Sorted CSV" saves the sorted data to a new file.

## What You'll See
- A table with your original data on the left and the sorted data on the right.
- A report showing what you sorted, how long it took, and the first 10 results.
- Progress updates if you enabled them.
- Benchmark results comparing times for different amounts of data.

## Tips
- Start with smaller numbers of rows to see results quickly.
- Bubble Sort works but can be slow for big lists – try Merge Sort for faster results.
- If sorting takes too long, use the "Stop" button or check fewer rows.
- Generating sample data is a good way to practice without your own file.
- The progress bar and timer help you understand how the sorting is going.

## Benchmark Results

### 1,000 Rows
- Bubble Sort: ~0.05s
- Insertion Sort: 0.07s
- Merge Sort: 0.01s

### 10,000 Rows
- Bubble Sort: ~5s
- Insertion Sort: ~1.5s
- Merge Sort: ~0.02s

### 100,000 Rows
- Bubble Sort: ~50 min (very slow!)
- Insertion Sort: ~3 min
- Merge Sort: ~0.2
