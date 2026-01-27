import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import time
import random
import csv
from typing import List, Tuple, Optional, Callable
import os
import threading
import subprocess
import sys

DOG_COLORS = {
    'primary': '#8B4513',      # Saddle Brown (dog fur)
    'secondary': '#D2691E',    # Chocolate (light brown)
    'accent': '#FFD700',       # Gold (like golden retriever)
    'light': '#F4A460',        # Sandy Brown
    'bg': '#FFF8DC',           # Cornsilk (light cream)
    'dark': '#654321',         # Dark brown
    'success': '#228B22',      # Forest Green
    'warning': '#FF8C00',      # Dark Orange
    'danger': '#DC143C',       # Crimson
    'text': '#2F4F4F'          # Dark Slate Gray
}

class SortingAlgorithms:
    """Contains implementations of various sorting algorithms with progress tracking"""
    
    @staticmethod
    def bubble_sort(arr: List, timer_cb: Optional[Callable] = None, stop_cb: Optional[Callable] = None) -> List:
        """Bubble Sort - O(n^2)"""
        n = len(arr)
        arr_copy = arr.copy()
        start_time = time.time()
        
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                if arr_copy[j] > arr_copy[j + 1]:
                    arr_copy[j], arr_copy[j + 1] = arr_copy[j + 1], arr_copy[j]
                    swapped = True
            
            if not swapped:
                break
            
            if stop_cb and stop_cb():
                return arr_copy  # Return partially sorted if stopped
            
            if timer_cb:
                timer_cb(time.time() - start_time)
        
        return arr_copy
    
    @staticmethod
    def insertion_sort(arr: List, timer_cb: Optional[Callable] = None, stop_cb: Optional[Callable] = None) -> List:
        """Insertion Sort - O(n^2)"""
        arr_copy = arr.copy()
        n = len(arr_copy)
        start_time = time.time()
        
        for i in range(1, n):
            key = arr_copy[i]
            j = i - 1
            
            while j >= 0 and arr_copy[j] > key:
                arr_copy[j + 1] = arr_copy[j]
                j -= 1
            
            arr_copy[j + 1] = key
            
            if stop_cb and stop_cb():
                return arr_copy  # Return partially sorted if stopped
            
            if timer_cb:
                timer_cb(time.time() - start_time)
        
        return arr_copy
    
    @staticmethod
    def merge_sort(arr: List, timer_cb: Optional[Callable] = None, stop_cb: Optional[Callable] = None) -> List:
        """Merge Sort - O(n log n)"""
        if len(arr) <= 1:
            return arr.copy()
        
        start_time = time.time()
        
        def merge(left: List, right: List) -> List:
            result = []
            i = j = 0
            
            while i < len(left) and j < len(right):
                if left[i] <= right[j]:
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1
            
            result.extend(left[i:])
            result.extend(right[j:])
            return result
        
        def merge_sort_recursive(arr: List) -> List:
            if len(arr) <= 1:
                return arr
            
            if stop_cb and stop_cb():
                return arr  # Return unsorted if stopped
            
            mid = len(arr) // 2
            left = merge_sort_recursive(arr[:mid])
            right = merge_sort_recursive(arr[mid:])
            
            result = merge(left, right)
            
            if timer_cb:
                timer_cb(time.time() - start_time)
            
            return result
        
        return merge_sort_recursive(arr.copy())

class PrelimExam:
    """🏆 Prelim Lab Exam - Sorting with CSV data"""
    
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.csv_data = []
        self.sorted_data = []
        self.csv_file_path = None
        self.show_timer = tk.BooleanVar(value=False)
        self.is_sorting = False
        self.show_first_10 = tk.BooleanVar(value=True)
        self.setup_ui()
        self.update_timer_visibility()
    
    def setup_ui(self):
        # Title
        title = tk.Label(
            self.frame,
            text="🏆 Prelim Exam: Sorting Algorithm Stress Test 🐕",
            font=("Comic Sans MS", 16, "bold"),
            bg=DOG_COLORS['primary'],
            fg=DOG_COLORS['accent'],
            pady=15
        )
        title.pack(fill=tk.X)
        
        # Instructions
        instructions = tk.Text(
            self.frame,
            height=6,
            wrap=tk.WORD,
            bg=DOG_COLORS['light'],
            font=("Arial", 10)
        )
        instructions.pack(padx=20, pady=10, fill=tk.BOTH)
        instructions.insert("1.0",
            "🐾 Objective: Handle 100,000 CSV records!\n\n"
            "Dataset: CSV file with ID, FirstName, LastName\n"
            "• Sort by any column • Display FULL results\n"
            "• Export sorted CSV • Track load vs sort time\n"
            "• real-time timer • Woof! 🦮"
        )
        instructions.config(state=tk.DISABLED)
        
        # File selection
        file_frame = tk.Frame(self.frame, bg=DOG_COLORS['bg'])
        file_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Button(
            file_frame,
            text="📁 Load CSV",
            font=("Arial", 10, "bold"),
            bg=DOG_COLORS['secondary'],
            fg="white",
            padx=12,
            pady=6,
            command=self.load_csv
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            file_frame,
            text="🎲 Generate CSV",
            font=("Arial", 10, "bold"),
            bg=DOG_COLORS['accent'],
            fg=DOG_COLORS['dark'],
            padx=12,
            pady=6,
            command=self.generate_sample_csv
        ).pack(side=tk.LEFT, padx=5)
        
        self.file_label = tk.Label(
            file_frame,
            text="No file loaded",
            font=("Arial", 9),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['text']
        )
        self.file_label.pack(side=tk.LEFT, padx=10)
        
        # Controls
        control_frame = tk.Frame(self.frame, bg=DOG_COLORS['bg'])
        control_frame.pack(pady=10)
        
        # Rows
        tk.Label(
            control_frame,
            text="Rows (N):",
            font=("Arial", 10, "bold"),
            bg=DOG_COLORS['bg']
        ).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.rows_var = tk.StringVar(value="1000")
        tk.Entry(
            control_frame,
            textvariable=self.rows_var,
            font=("Arial", 10),
            width=10
        ).grid(row=0, column=1, padx=5, pady=5)
        
        # Column
        tk.Label(
            control_frame,
            text="Sort by:",
            font=("Arial", 10, "bold"),
            bg=DOG_COLORS['bg']
        ).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.column_var = tk.StringVar(value="ID")
        ttk.Combobox(
            control_frame,
            textvariable=self.column_var,
            values=["ID", "FirstName", "LastName"],
            state="readonly",
            font=("Arial", 10),
            width=11
        ).grid(row=1, column=1, padx=5, pady=5)
        
        # Algorithm
        tk.Label(
            control_frame,
            text="Algorithm:",
            font=("Arial", 10, "bold"),
            bg=DOG_COLORS['bg']
        ).grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.algorithm_var = tk.StringVar(value="Merge Sort")
        ttk.Combobox(
            control_frame,
            textvariable=self.algorithm_var,
            values=["Bubble Sort", "Insertion Sort", "Merge Sort"],
            state="readonly",
            font=("Arial", 10),
            width=11
        ).grid(row=2, column=1, padx=5, pady=5)
        
        # Timer checkbox
        tk.Checkbutton(
            control_frame,
            text="🐾 Timer (has performance impact)",
            variable=self.show_timer,
            bg=DOG_COLORS['bg'],
            font=("Arial", 9),
            command=self.update_timer_visibility
        ).grid(row=3, column=0, columnspan=2, pady=3)
        
        tk.Checkbutton(
            control_frame,
            text="🐾 Show first 10 only",
            variable=self.show_first_10,
            bg=DOG_COLORS['bg'],
            font=("Arial", 9)
        ).grid(row=4, column=0, columnspan=2, pady=3)
        
        # Buttons
        tk.Button(
            control_frame,
            text="🏃 Run Sort",
            font=("Arial", 10, "bold"),
            bg=DOG_COLORS['success'],
            fg="white",
            padx=18,
            pady=8,
            command=self.run_sort
        ).grid(row=0, column=2, rowspan=4, padx=15)
        
        self.stop_button = tk.Button(
            control_frame,
            text="⏹️ Stop",
            font=("Arial", 10, "bold"),
            bg=DOG_COLORS['danger'],
            fg="white",
            padx=18,
            pady=8,
            command=self.stop_sort,
            state=tk.DISABLED
        )
        self.stop_button.grid(row=0, column=4, rowspan=4, padx=5)
        
        tk.Button(
            control_frame,
            text="📊 Benchmark",
            font=("Arial", 10, "bold"),
            bg=DOG_COLORS['warning'],
            fg="white",
            padx=15,
            pady=8,
            command=self.run_benchmark
        ).grid(row=0, column=3, rowspan=4, padx=5)
        
        # Timer
        timer_frame = tk.Frame(self.frame, bg=DOG_COLORS['bg'])
        timer_frame.pack(padx=20, fill=tk.X)
        
        self.timer_label = tk.Label(timer_frame, text="⏱️ 0.0000s",
                                   bg=DOG_COLORS['bg'], fg=DOG_COLORS['danger'],
                                   font=("Arial", 11, "bold"))
        self.timer_label.pack(anchor=tk.W)
        
        # Results
        tk.Label(
            self.frame,
            text="📋 Results:",
            font=("Arial", 11, "bold"),
            bg=DOG_COLORS['bg']
        ).pack(anchor=tk.W, padx=20, pady=(10,0))
        
        self.results_text = scrolledtext.ScrolledText(
            self.frame,
            height=12,
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.results_text.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        
        # Export
        export_frame = tk.Frame(self.frame, bg=DOG_COLORS['bg'])
        export_frame.pack(pady=10)
        
        tk.Button(
            export_frame,
            text="💾 Export Report",
            bg=DOG_COLORS['secondary'],
            fg="white",
            command=self.export_report,
            font=("Arial", 9, "bold"),
            padx=12,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            export_frame,
            text="📄 Export Sorted CSV",
            bg=DOG_COLORS['accent'],
            fg=DOG_COLORS['dark'],
            command=self.export_sorted_csv,
            font=("Arial", 9, "bold"),
            padx=12,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def update_timer_visibility(self):
        """Update timer label visibility based on checkbox"""
        if self.show_timer.get():
            self.timer_label.pack(anchor=tk.W)
        else:
            self.timer_label.pack_forget()
    
    def generate_sample_csv(self):
        """Generate 100,000 record CSV with shuffled IDs"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="generated_data.csv"
        )
        
        if not file_path:
            return
        
        try:
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", "🐕 Generating 100,000 random records...\n")
            self.frame.update()
            
            first_names = ["John", "Jane", "Michael", "Emily", "David", "Sarah", "Robert", "Lisa",
                          "James", "Mary", "William", "Patricia", "Richard", "Jennifer", "Joseph",
                          "Linda", "Thomas", "Barbara", "Charles", "Elizabeth"]
            
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
                         "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
                         "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

            # --- NEW LOGIC: Shuffle the IDs ---
            ids = list(range(1, 100001))
            random.shuffle(ids) # This creates the "unorganized" order
            
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['ID', 'FirstName', 'LastName'])
                
                for count, i in enumerate(ids, 1):
                    writer.writerow([i, random.choice(first_names), random.choice(last_names)])
                    
                    if count % 10000 == 0:
                        self.results_text.insert(tk.END, f"Generated {count}...\n")
                        self.frame.update()
            # ----------------------------------
            
            self.results_text.insert(tk.END, "\n✓ Successfully generated 100,000 random records!\n")
            self.results_text.insert(tk.END, f"File: {file_path}\n")
            
            self.csv_file_path = file_path
            self.load_csv_data()
            
            messagebox.showinfo("Success! 🐕", "Randomized CSV generated!")
        
        except Exception as e:
            messagebox.showerror("Error! 😿", f"Failed: {e}")
    
    def load_csv(self):
        """Load CSV file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.csv_file_path = file_path
            self.load_csv_data()
    
    def load_csv_data(self):
        """Load data from CSV"""
        try:
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", f"Loading: {self.csv_file_path}\n")
            self.frame.update()
            
            start_time = time.time()
            
            with open(self.csv_file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                self.csv_data = list(reader)
            
            load_time = time.time() - start_time
            
            self.results_text.insert(tk.END, f"\n✓ Loaded {len(self.csv_data)} records\n")
            self.results_text.insert(tk.END, f"Load time: {load_time:.4f}s\n")
            
            self.file_label.config(
                text=f"Loaded: {os.path.basename(self.csv_file_path)} ({len(self.csv_data)} records)",
                fg=DOG_COLORS['success']
            )
        
        except Exception as e:
            messagebox.showerror("Error! 😿", f"Failed: {e}")
            self.file_label.config(text="Failed to load", fg=DOG_COLORS['danger'])
    
    def update_timer(self, elapsed):
        if self.show_timer.get():
            self.timer_label.config(text=f"⏱️ {elapsed:.4f}s")
            self.frame.update_idletasks()
    
    def run_sort(self):
        """Run sorting on CSV data"""
        if not self.csv_data:
            messagebox.showwarning("No Data! 🐕", "Load CSV first!")
            return
        
        if self.is_sorting:
            messagebox.showwarning("Busy! 🐕", "Already sorting!")
            return
        
        try:
            n_rows = int(self.rows_var.get())
            if n_rows <= 0 or n_rows > len(self.csv_data):
                raise ValueError(f"Rows must be 1-{len(self.csv_data)}")
            
            column = self.column_var.get()
            algorithm = self.algorithm_var.get()
            
            # Warning for large O(n²)
            if n_rows > 10000 and algorithm in ["Bubble Sort", "Insertion Sort"]:
                response = messagebox.askyesno(
                    "Warning! 🐕",
                    f"Sorting {n_rows} with {algorithm} may be very slow!\n\nContinue?"
                )
                if not response:
                    return
            
            self.is_sorting = True
            self.timer_label.config(text="⏱️ 0.0000s")
            self.stop_button.config(state=tk.NORMAL)
            
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", f"🐕 Sorting {n_rows} rows by {column}...\n\n")
            self.frame.update()
            
            def sort_thread():
                try:
                    data_subset = self.csv_data[:n_rows]
                    
                    # Extract keys
                    if column == "ID":
                        keys = [int(row['ID']) for row in data_subset]
                    else:
                        keys = [row[column] for row in data_subset]
                    
                    # Sort
                    start_time = time.time()
                    
                    if algorithm == "Bubble Sort":
                        sorted_keys = SortingAlgorithms.bubble_sort(
                            keys, self.update_timer if self.show_timer.get() else None, lambda: not self.is_sorting)
                    elif algorithm == "Insertion Sort":
                        sorted_keys = SortingAlgorithms.insertion_sort(
                            keys, self.update_timer if self.show_timer.get() else None, lambda: not self.is_sorting)
                    else:
                        sorted_keys = SortingAlgorithms.merge_sort(
                            keys, self.update_timer if self.show_timer.get() else None, lambda: not self.is_sorting)
                    
                    sort_time = time.time() - start_time
                    
                    # Create sorted data maintaining order
                    key_to_rows = {}
                    for i, row in enumerate(data_subset):
                        key = keys[i]
                        if key not in key_to_rows:
                            key_to_rows[key] = []
                        key_to_rows[key].append(row)
                    
                    self.sorted_data = []
                    for key in sorted_keys:
                        if key in key_to_rows and key_to_rows[key]:
                            self.sorted_data.append(key_to_rows[key].pop(0))
                    
                    # Display FULL results
                    self.results_text.insert(tk.END, "="*70 + "\n")
                    self.results_text.insert(tk.END, "🏆 SORTING RESULTS 🏆\n")
                    self.results_text.insert(tk.END, "="*70 + "\n\n")
                    self.results_text.insert(tk.END, f"Algorithm: {algorithm}\n")
                    self.results_text.insert(tk.END, f"Rows: {n_rows}\n")
                    self.results_text.insert(tk.END, f"Column: {column}\n")
                    self.results_text.insert(tk.END, f"Time: {sort_time:.4f}s ({sort_time*1000:.2f}ms)\n\n")
                    
                    self.results_text.insert(tk.END, "="*70 + "\n")
                    data_to_show = self.sorted_data[:10] if self.show_first_10.get() else self.sorted_data
                    header = f"FIRST 10 SORTED RECORDS" if self.show_first_10.get() else f"ALL {len(self.sorted_data)} SORTED RECORDS"
                    self.results_text.insert(tk.END, f"{header}\n")
                    self.results_text.insert(tk.END, "="*70 + "\n\n")
                    
                    for i, record in enumerate(data_to_show):
                        self.results_text.insert(tk.END, 
                            f"{i+1:5d}. ID:{record['ID']:>6} | "
                            f"{record['FirstName']:>10} {record['LastName']:<12}\n")
                    
                    self.results_text.insert(tk.END, "\n" + "="*70 + "\n")
                    self.results_text.insert(tk.END, "🐾 Complete! Good dog! 🐾\n")
                    self.results_text.insert(tk.END, "="*70 + "\n")
                    
                    self.timer_label.config(text=f"⏱️ {sort_time:.4f}s")
                    
                    messagebox.showinfo("Done! 🐕", f"Sorted in {sort_time:.4f}s")
                
                except Exception as e:
                    messagebox.showerror("Error! 😿", str(e))
                finally:
                    self.is_sorting = False
                    self.stop_button.config(state=tk.DISABLED)
            
            threading.Thread(target=sort_thread, daemon=True).start()
        
        except ValueError as e:
            messagebox.showerror("Error! 😿", str(e))
    
    def stop_sort(self):
        """Stop the current sorting operation"""
        if self.is_sorting:
            self.is_sorting = False
            self.stop_button.config(state=tk.DISABLED)
            self.results_text.insert(tk.END, "\n⏹️ Sorting stopped by user!\n")
            messagebox.showinfo("Stopped! 🐕", "Sorting operation has been stopped!")
    
    def run_benchmark(self):
        """Run comprehensive benchmark using the selected algorithm"""
        if not self.csv_data:
            messagebox.showwarning("No Data! 🐕", "Load CSV first!")
            return
        
        algorithm = self.algorithm_var.get()
        
        # Safety Check: O(n²) algorithms will take a very long time for 100,000 records
        if algorithm in ["Bubble Sort", "Insertion Sort"]:
            response = messagebox.askyesno(
                "Warning! 🐕",
                f"Benchmarking 100,000 records with {algorithm} could take hours.\n\n"
                "Do you want to proceed anyway?"
            )
            if not response:
                return

        self.is_sorting = True
        self.timer_label.config(text="⏱️ 0.0000s")
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", f"🐕 Benchmarking {algorithm}...\n\n")
        self.frame.update()
        
        def benchmark_thread():
            try:
                sizes = [1000, 10000, 100000]
                results = {}
                
                # Map the string name to the actual function
                algo_map = {
                    "Bubble Sort": SortingAlgorithms.bubble_sort,
                    "Insertion Sort": SortingAlgorithms.insertion_sort,
                    "Merge Sort": SortingAlgorithms.merge_sort
                }
                sort_func = algo_map.get(algorithm)

                for size in sizes:
                    if size > len(self.csv_data):
                        continue
                        
                    self.results_text.insert(tk.END, f"Testing {size} rows with {algorithm}...\n")
                    self.frame.update()
                    
                    # Prepare subset of data (just the IDs/keys)
                    data_subset = self.csv_data[:size]
                    keys = [int(row['ID']) for row in data_subset]
                    
                    start_time = time.time()
                    # Call the selected function (we pass None for callbacks to get pure speed)
                    sort_func(keys, None, lambda: not self.is_sorting) 
                    exec_time = time.time() - start_time
                    
                    results[size] = exec_time
                    
                    # If user pressed stop during benchmark
                    if not self.is_sorting:
                        break
                
                # Display Results Table
                self.results_text.insert(tk.END, "\n\n" + "="*70 + "\n")
                self.results_text.insert(tk.END, f"🏆 BENCHMARK: {algorithm.upper()} 🏆\n")
                self.results_text.insert(tk.END, "="*70 + "\n\n")
                self.results_text.insert(tk.END, f"{'Size':<10} {'Time (sec)':<15} {'Time (ms)':<15}\n")
                self.results_text.insert(tk.END, "-"*70 + "\n")
                
                for size in sizes:
                    if size in results:
                        time_sec = results[size]
                        time_ms = time_sec * 1000
                        self.results_text.insert(tk.END, f"{size:<10} {time_sec:<15.4f} {time_ms:<15.2f}\n")
                
                if self.is_sorting:
                    messagebox.showinfo("Done! 🐕", f"{algorithm} benchmark completed!")
                    
            except Exception as e:
                messagebox.showerror("Error! 😿", str(e))
            finally:
                self.is_sorting = False
        
        threading.Thread(target=benchmark_thread, daemon=True).start()
    
    def export_report(self):
        """Export full report"""
        if not self.sorted_data:
            messagebox.showwarning("No Data! 🐕", "Run sort first!")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile="csv_sort_report.txt"
        )
        
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.get("1.0", tk.END))
                
                messagebox.showinfo("Saved! 🐕", "Report exported!")
            except Exception as e:
                messagebox.showerror("Error! 😿", str(e))
    
    def export_sorted_csv(self):
        """Export sorted CSV file"""
        if not self.sorted_data:
            messagebox.showwarning("No Data! 🐕", "Run sort first!")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="sorted_data.csv"
        )
        
        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=['ID', 'FirstName', 'LastName'])
                    writer.writeheader()
                    writer.writerows(self.sorted_data)
                
                messagebox.showinfo("Saved! 🐕", 
                    f"Exported {len(self.sorted_data)} sorted records to CSV!")
            except Exception as e:
                messagebox.showerror("Error! 😿", str(e))


class ArfArfSort:
    """🐕 Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🐕 ArfArf Sort - Dog-Themed Edition 🦴")
        self.root.geometry("950x825")
        self.root.configure(bg=DOG_COLORS['bg'])
        self.root.resizable(False, False)  # Prevent resizing to maintain layout
        
        self.main_container = tk.Frame(root, bg=DOG_COLORS['bg'])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        self.show_home()
    
    def clear_container(self):
        """Clears the current frame content"""
        for widget in self.main_container.winfo_children():
            widget.destroy()
    
    def show_home(self):
        """Main Menu - Only Exam remains"""
        self.clear_container()
        
        # Title
        title_frame = tk.Frame(self.main_container, bg=DOG_COLORS['primary'], height=120)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="🐕 ArfArf Sort 🦴",
            font=("Comic Sans MS", 32, "bold"),
            bg=DOG_COLORS['primary'],
            fg=DOG_COLORS['accent']
        ).pack(pady=10)
        
        tk.Label(
            title_frame,
            text="Dog-Themed Algorithm Analysis Laboratory",
            font=("Arial", 14),
            bg=DOG_COLORS['primary'],
            fg=DOG_COLORS['light']
        ).pack()
        
        # Menu
        menu_frame = tk.Frame(self.main_container, bg=DOG_COLORS['bg'])
        menu_frame.pack(expand=True)
        
        button_config = {
            "font": ("Arial", 14, "bold"),
            "width": 30,
            "height": 2,
            "cursor": "hand2"
        }
        
        # Only the Exam button remains
        tk.Button(
            menu_frame,
            text="🏆 PRELIM LAB EXAM",
            bg=DOG_COLORS['danger'],
            fg="white",
            command=self.show_exam,
            **button_config
        ).pack(pady=15)
        
        tk.Label(
            self.main_container,
            text="🐾 Woof! Ready to start the exam? 🐾",
            font=("Arial", 10),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['text']
        ).pack(side=tk.BOTTOM, pady=20)
    
    def create_back_button(self, parent):
        """Standard back button for sub-pages"""
        tk.Button(
            parent,
            text="← Back to Home",
            font=("Arial", 10),
            bg=DOG_COLORS['secondary'],
            fg="white",
            padx=15,
            pady=5,
            command=self.show_home
        ).pack(side=tk.BOTTOM, pady=10)
    
    def show_exam(self):
        """Switches view to the Prelim Exam work"""
        self.clear_container()
        exam_frame = tk.Frame(self.main_container, bg=DOG_COLORS['bg'])
        exam_frame.pack(fill=tk.BOTH, expand=True)
        
        PrelimExam(exam_frame)
        self.create_back_button(exam_frame)


def main():
    root = tk.Tk()
    app = ArfArfSort(root)
    root.mainloop()


if __name__ == "__main__":
    main()
