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
    'primary': '#8B4513',       # Saddle Brown (professional dog theme)
    'secondary': '#A0522D',     # Sienna (warm brown)
    'accent': '#DAA520',        # Goldenrod (golden retriever)
    'light': '#F5DEB3',         # Wheat (light cream)
    'bg': '#FFFAF0',            # Floral White (soft background)
    'dark': '#654321',          # Dark Brown
    'success': '#228B22',       # Forest Green
    'warning': '#FF8C00',       # Dark Orange
    'danger': '#DC143C',        # Crimson
    'text': '#3E2723',          # Dark Brown text
    'border': '#D2B48C',        # Tan (border)
    'table_bg': '#FFFFFF',      # White for tables
    'table_alt': '#FFF8DC'      # Cornsilk for alternating rows
}

class SortingAlgorithms:
    """Contains implementations of various sorting algorithms with progress tracking"""
    
    @staticmethod
    def bubble_sort(arr: List, timer_cb: Optional[Callable] = None, stop_cb: Optional[Callable] = None, 
                    progress_cb: Optional[Callable] = None, reverse: bool = False) -> List:
        """Bubble Sort - O(n^2)"""
        n = len(arr)
        arr_copy = arr.copy()
        start_time = time.time()
        
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                if (arr_copy[j] > arr_copy[j + 1]) if not reverse else (arr_copy[j] < arr_copy[j + 1]):
                    arr_copy[j], arr_copy[j + 1] = arr_copy[j + 1], arr_copy[j]
                    swapped = True
            
            if not swapped:
                break
            
            if stop_cb and stop_cb():
                return arr_copy
            
            if timer_cb:
                timer_cb(time.time() - start_time)
            
            if progress_cb and i % max(1, n // 100) == 0:
                progress_cb((i + 1) / n * 100)
        
        return arr_copy
    
    @staticmethod
    def insertion_sort(arr: List, timer_cb: Optional[Callable] = None, stop_cb: Optional[Callable] = None,
                       progress_cb: Optional[Callable] = None, reverse: bool = False) -> List:
        """Insertion Sort - O(n^2)"""
        arr_copy = arr.copy()
        n = len(arr_copy)
        start_time = time.time()
        
        for i in range(1, n):
            key = arr_copy[i]
            j = i - 1
            
            while j >= 0 and ((arr_copy[j] > key) if not reverse else (arr_copy[j] < key)):
                arr_copy[j + 1] = arr_copy[j]
                j -= 1
            
            arr_copy[j + 1] = key
            
            if stop_cb and stop_cb():
                return arr_copy
            
            if timer_cb:
                timer_cb(time.time() - start_time)
            
            if progress_cb and i % max(1, n // 100) == 0:
                progress_cb(i / n * 100)
        
        return arr_copy
    
    @staticmethod
    def merge_sort(arr: List, timer_cb: Optional[Callable] = None, stop_cb: Optional[Callable] = None,
                   progress_cb: Optional[Callable] = None, reverse: bool = False) -> List:
        """Merge Sort - O(n log n)"""
        if len(arr) <= 1:
            return arr.copy()
        
        start_time = time.time()
        progress_counter = [0]
        total_operations = len(arr)
        
        def merge(left: List, right: List) -> List:
            result = []
            i = j = 0
            
            while i < len(left) and j < len(right):
                if (left[i] <= right[j]) if not reverse else (left[i] >= right[j]):
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
                return arr
            
            mid = len(arr) // 2
            left = merge_sort_recursive(arr[:mid])
            right = merge_sort_recursive(arr[mid:])
            
            result = merge(left, right)
            
            progress_counter[0] += len(arr)
            if progress_cb and progress_counter[0] % max(1, total_operations // 100) == 0:
                progress_cb(min(100, (progress_counter[0] / total_operations) * 100))
            
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
        self.show_progress = tk.BooleanVar(value=False)
        self.is_sorting = False
        self.show_first_10 = tk.BooleanVar(value=True)
        self.last_sort_time = 0
        self.last_algorithm = ""
        self.last_rows = 0
        self.last_column = ""
        self.is_rendering = False
        self.sort_order = tk.StringVar(value="Ascending")
        
        self.setup_ui()
        self.update_timer_visibility()
        self.update_progress_visibility()
        self.auto_load_data()
    
    def setup_ui(self):
        # Title Bar
        title_bar = tk.Frame(self.frame, bg=DOG_COLORS['primary'], height=80)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)
        
        title_container = tk.Frame(title_bar, bg=DOG_COLORS['primary'])
        title_container.pack(expand=True)
        
        tk.Label(
            title_container,
            text="🐕 ",
            font=("Segoe UI", 24),
            bg=DOG_COLORS['primary'],
            fg=DOG_COLORS['accent']
        ).pack(side=tk.LEFT)
        
        title = tk.Label(
            title_container,
            text="Prelim Lab Exam: Sorting Algorithm Analysis",
            font=("Segoe UI", 18, "bold"),
            bg=DOG_COLORS['primary'],
            fg="white"
        )
        title.pack(side=tk.LEFT)
        
        tk.Label(
            title_container,
            text=" 🦴",
            font=("Segoe UI", 24),
            bg=DOG_COLORS['primary'],
            fg=DOG_COLORS['accent']
        ).pack(side=tk.LEFT)
        
        # Main content area - split 50/50
        main_container = tk.Frame(self.frame, bg=DOG_COLORS['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # LEFT SIDE - Controls and Report (50%)
        left_side = tk.Frame(main_container, bg=DOG_COLORS['bg'])
        left_side.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Instructions Panel
        self.create_instructions_panel(left_side)
        
        # File Management Panel
        self.create_file_panel(left_side)
        
        # Control Panel
        self.create_control_panel(left_side)
        
        # Progress and Timer Panel
        self.create_progress_panel(left_side)
        
        # Report Panel
        self.create_report_panel(left_side)
        
        # Export Panel
        self.create_export_panel(left_side)
        
        # RIGHT SIDE - Data Tables (50%)
        right_side = tk.Frame(main_container, bg=DOG_COLORS['bg'])
        right_side.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Results Panel (Original + Sorted)
        self.create_data_tables_panel(right_side)
    
    def create_instructions_panel(self, parent):
        """Create professional instructions panel"""
        panel = tk.LabelFrame(
            parent,
            text="📋 Objective",
            font=("Segoe UI", 11, "bold"),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['text'],
            relief=tk.RIDGE,
            borderwidth=2
        )
        panel.pack(fill=tk.X, pady=(0, 15))
        
        instructions = tk.Text(
            panel,
            height=4,
            wrap=tk.WORD,
            bg=DOG_COLORS['light'],
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=10
        )
        instructions.pack(padx=10, pady=10, fill=tk.BOTH)
        instructions.insert("1.0",
            "• Process large CSV datasets (up to 100,000 records)\n"
            "• Sort by any column with multiple algorithm options\n"
            "• Compare performance with built-in benchmarking\n"
            "• Export sorted data and comprehensive reports"
        )
        instructions.config(state=tk.DISABLED)
    
    def create_file_panel(self, parent):
        """Create file management panel"""
        panel = tk.LabelFrame(
            parent,
            text="📁 Data Management",
            font=("Segoe UI", 11, "bold"),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['text'],
            relief=tk.RIDGE,
            borderwidth=2
        )
        panel.pack(fill=tk.X, pady=(0, 15))
        
        inner_frame = tk.Frame(panel, bg=DOG_COLORS['bg'])
        inner_frame.pack(padx=15, pady=15, fill=tk.X)
        
        # Buttons
        btn_frame = tk.Frame(inner_frame, bg=DOG_COLORS['bg'])
        btn_frame.pack(side=tk.LEFT)
        
        self.load_button = tk.Button(
            btn_frame,
            text="📁 Load CSV File",
            font=("Segoe UI", 10),
            bg=DOG_COLORS['secondary'],
            fg="white",
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.load_csv
        )
        self.load_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.generate_button = tk.Button(
            btn_frame,
            text="🎲 Generate Sample Data",
            font=("Segoe UI", 10),
            bg=DOG_COLORS['accent'],
            fg=DOG_COLORS['text'],
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.generate_sample_csv
        )
        self.generate_button.pack(side=tk.LEFT)
        
        # Status label
        self.file_label = tk.Label(
            inner_frame,
            text="No file loaded",
            font=("Segoe UI", 10),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['border'],
            anchor=tk.W
        )
        self.file_label.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
    
    def create_control_panel(self, parent):
        """Create control panel with professional styling"""
        panel = tk.LabelFrame(
            parent,
            text="⚙️ Configuration",
            font=("Segoe UI", 11, "bold"),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['text'],
            relief=tk.RIDGE,
            borderwidth=2
        )
        panel.pack(fill=tk.X, pady=(0, 15))
        
        inner_frame = tk.Frame(panel, bg=DOG_COLORS['bg'])
        inner_frame.pack(padx=15, pady=15, fill=tk.X)
        
        # Left side - parameters
        left_frame = tk.Frame(inner_frame, bg=DOG_COLORS['bg'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Rows
        row1 = tk.Frame(left_frame, bg=DOG_COLORS['bg'])
        row1.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row1,
            text="Number of Rows:",
            font=("Segoe UI", 10),
            bg=DOG_COLORS['bg'],
            width=15,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        self.rows_var = tk.StringVar(value="1000")
        self.rows_entry = tk.Entry(
            row1,
            textvariable=self.rows_var,
            font=("Segoe UI", 10),
            width=15,
            relief=tk.SOLID,
            borderwidth=1
        )
        self.rows_entry.pack(side=tk.LEFT, padx=10)
        
        # Column
        row2 = tk.Frame(left_frame, bg=DOG_COLORS['bg'])
        row2.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row2,
            text="Sort by Column:",
            font=("Segoe UI", 10),
            bg=DOG_COLORS['bg'],
            width=15,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        self.column_var = tk.StringVar(value="ID")
        self.column_combo = ttk.Combobox(
            row2,
            textvariable=self.column_var,
            values=["ID", "FirstName", "LastName"],
            state="readonly",
            font=("Segoe UI", 10),
            width=13
        )
        self.column_combo.pack(side=tk.LEFT, padx=10)
        
        # Algorithm
        row3 = tk.Frame(left_frame, bg=DOG_COLORS['bg'])
        row3.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row3,
            text="Algorithm:",
            font=("Segoe UI", 10),
            bg=DOG_COLORS['bg'],
            width=15,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        self.algorithm_var = tk.StringVar(value="Merge Sort")
        self.algo_combo = ttk.Combobox(
            row3,
            textvariable=self.algorithm_var,
            values=["Bubble Sort", "Insertion Sort", "Merge Sort"],
            state="readonly",
            font=("Segoe UI", 10),
            width=13
        )
        self.algo_combo.pack(side=tk.LEFT, padx=10)
        
        # Sort Order
        row3b = tk.Frame(left_frame, bg=DOG_COLORS['bg'])
        row3b.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row3b,
            text="Sort Order:",
            font=("Segoe UI", 10),
            bg=DOG_COLORS['bg'],
            width=15,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        self.order_combo = ttk.Combobox(
            row3b,
            textvariable=self.sort_order,
            values=["Ascending", "Descending"],
            state="readonly",
            font=("Segoe UI", 10),
            width=13
        )
        self.order_combo.pack(side=tk.LEFT, padx=10)
        
        # Options
        row4 = tk.Frame(left_frame, bg=DOG_COLORS['bg'])
        row4.pack(fill=tk.X, pady=5)
        
        self.timer_check = tk.Checkbutton(
            row4,
            text="Show Timer (impacts performance)",
            variable=self.show_timer,
            bg=DOG_COLORS['bg'],
            font=("Segoe UI", 9),
            command=self.update_timer_visibility
        )
        self.timer_check.pack(side=tk.LEFT, padx=(0, 20))
        
        self.progress_check = tk.Checkbutton(
            row4,
            text="Show Progress Bar (impacts performance)",
            variable=self.show_progress,
            bg=DOG_COLORS['bg'],
            font=("Segoe UI", 9),
            command=self.update_progress_visibility
        )
        self.progress_check.pack(side=tk.LEFT)
        
        row5 = tk.Frame(left_frame, bg=DOG_COLORS['bg'])
        row5.pack(fill=tk.X, pady=5)
        
        self.display_check = tk.Checkbutton(
            row5,
            text="Display first 10 records only",
            variable=self.show_first_10,
            bg=DOG_COLORS['bg'],
            font=("Segoe UI", 9)
        )
        self.display_check.pack(side=tk.LEFT)
        
        # Right side - action buttons
        right_frame = tk.Frame(inner_frame, bg=DOG_COLORS['bg'])
        right_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        self.run_button = tk.Button(
            right_frame,
            text="▶ Run Sort",
            font=("Segoe UI", 11, "bold"),
            bg=DOG_COLORS['success'],
            fg="white",
            padx=25,
            pady=12,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.run_sort
        )
        self.run_button.pack(pady=5)
        
        self.stop_button = tk.Button(
            right_frame,
            text="⏹ Stop",
            font=("Segoe UI", 11, "bold"),
            bg=DOG_COLORS['danger'],
            fg="white",
            padx=30,
            pady=12,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.stop_sort,
            state=tk.DISABLED
        )
        self.stop_button.pack(pady=5)
        
        self.benchmark_button = tk.Button(
            right_frame,
            text="📊 Benchmark",
            font=("Segoe UI", 11, "bold"),
            bg=DOG_COLORS['warning'],
            fg="white",
            padx=20,
            pady=12,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.run_benchmark
        )
        self.benchmark_button.pack(pady=5)
    
    def create_progress_panel(self, parent):
        """Create progress and timer panel"""
        panel = tk.Frame(parent, bg=DOG_COLORS['bg'])
        panel.pack(fill=tk.X, pady=(0, 15))
        
        # Timer
        self.timer_frame = tk.Frame(panel, bg=DOG_COLORS['bg'])
        
        tk.Label(
            self.timer_frame,
            text="⏱ Elapsed Time:",
            font=("Segoe UI", 10, "bold"),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['text']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.timer_label = tk.Label(
            self.timer_frame,
            text="0.0000s",
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['danger'],
            font=("Segoe UI", 12, "bold")
        )
        self.timer_label.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_frame = tk.Frame(panel, bg=DOG_COLORS['bg'])
        
        tk.Label(
            self.progress_frame,
            text="Progress:",
            font=("Segoe UI", 10, "bold"),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['text']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.progress_label = tk.Label(
            self.progress_frame,
            text="0%",
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['text'],
            font=("Segoe UI", 10),
            width=6
        )
        self.progress_label.pack(side=tk.LEFT, padx=(10, 0))
    
    def create_report_panel(self, parent):
        """Create report panel for left side"""
        panel = tk.LabelFrame(
            parent,
            text="📊 Sort Report",
            font=("Segoe UI", 11, "bold"),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['text'],
            relief=tk.RIDGE,
            borderwidth=2
        )
        panel.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.report_text = scrolledtext.ScrolledText(
            panel,
            height=12,
            wrap=tk.WORD,
            font=("Consolas", 9),
            relief=tk.FLAT,
            bg=DOG_COLORS['light']
        )
        self.report_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    def create_data_tables_panel(self, parent):
        """Create data tables panel for right side - Original and Sorted"""
        # Original Dataset (Top 50%)
        original_panel = tk.LabelFrame(
            parent,
            text="📄 Original Dataset",
            font=("Segoe UI", 11, "bold"),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['text'],
            relief=tk.RIDGE,
            borderwidth=2
        )
        original_panel.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        original_table_frame = tk.Frame(original_panel, bg=DOG_COLORS['table_bg'])
        original_table_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Scrollbars for original
        original_vsb = ttk.Scrollbar(original_table_frame, orient="vertical")
        original_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        original_hsb = ttk.Scrollbar(original_table_frame, orient="horizontal")
        original_hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Original Treeview
        self.original_table = ttk.Treeview(
            original_table_frame,
            columns=("No", "ID", "FirstName", "LastName"),
            show="headings",
            yscrollcommand=original_vsb.set,
            xscrollcommand=original_hsb.set
        )
        
        original_vsb.config(command=self.original_table.yview)
        original_hsb.config(command=self.original_table.xview)
        
        # Define columns for original
        self.original_table.heading("No", text="#")
        self.original_table.heading("ID", text="ID")
        self.original_table.heading("FirstName", text="First Name")
        self.original_table.heading("LastName", text="Last Name")
        
        self.original_table.column("No", width=50, anchor=tk.CENTER)
        self.original_table.column("ID", width=80, anchor=tk.CENTER)
        self.original_table.column("FirstName", width=120, anchor=tk.W)
        self.original_table.column("LastName", width=120, anchor=tk.W)
        
        self.original_table.pack(fill=tk.BOTH, expand=True)
        
        # Striped rows for original
        self.original_table.tag_configure('oddrow', background=DOG_COLORS['table_bg'])
        self.original_table.tag_configure('evenrow', background=DOG_COLORS['table_alt'])
        
        # Sorted Results (Bottom 50%)
        sorted_panel = tk.LabelFrame(
            parent,
            text="📋 Results (Sorted)",
            font=("Segoe UI", 11, "bold"),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['text'],
            relief=tk.RIDGE,
            borderwidth=2
        )
        sorted_panel.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Loading frame
        self.loading_frame = tk.Frame(sorted_panel, bg=DOG_COLORS['light'])
        
        tk.Label(
            self.loading_frame,
            text="⏳ Rendering results...",
            font=("Segoe UI", 14, "bold"),
            bg=DOG_COLORS['light'],
            fg=DOG_COLORS['primary']
        ).pack(pady=20)
        
        self.loading_label = tk.Label(
            self.loading_frame,
            text="Please wait",
            font=("Segoe UI", 11),
            bg=DOG_COLORS['light'],
            fg=DOG_COLORS['text']
        )
        self.loading_label.pack(pady=10)
        
        # Create Treeview for sorted table display
        self.table_frame = tk.Frame(sorted_panel, bg=DOG_COLORS['table_bg'])
        self.table_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.results_table = ttk.Treeview(
            self.table_frame,
            columns=("No", "ID", "FirstName", "LastName"),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.results_table.yview)
        hsb.config(command=self.results_table.xview)
        
        # Define columns
        self.results_table.heading("No", text="#")
        self.results_table.heading("ID", text="ID")
        self.results_table.heading("FirstName", text="First Name")
        self.results_table.heading("LastName", text="Last Name")
        
        self.results_table.column("No", width=50, anchor=tk.CENTER)
        self.results_table.column("ID", width=80, anchor=tk.CENTER)
        self.results_table.column("FirstName", width=120, anchor=tk.W)
        self.results_table.column("LastName", width=120, anchor=tk.W)
        
        self.results_table.pack(fill=tk.BOTH, expand=True)
        
        # Striped rows
        self.results_table.tag_configure('oddrow', background=DOG_COLORS['table_bg'])
        self.results_table.tag_configure('evenrow', background=DOG_COLORS['table_alt'])
    
    def create_export_panel(self, parent):
        """Create export panel"""
        panel = tk.Frame(parent, bg=DOG_COLORS['bg'])
        panel.pack(fill=tk.X)
        
        self.export_report_button = tk.Button(
            panel,
            text="💾 Export Report",
            bg=DOG_COLORS['secondary'],
            fg="white",
            command=self.export_report,
            font=("Segoe UI", 10),
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.export_report_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_csv_button = tk.Button(
            panel,
            text="📄 Export Sorted CSV",
            bg=DOG_COLORS['accent'],
            fg=DOG_COLORS['text'],
            command=self.export_sorted_csv,
            font=("Segoe UI", 10),
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.export_csv_button.pack(side=tk.LEFT)
    
    def update_timer_visibility(self):
        """Update timer visibility"""
        if self.show_timer.get():
            self.timer_frame.pack(fill=tk.X, pady=(0, 10))
        else:
            self.timer_frame.pack_forget()
    
    def update_progress_visibility(self):
        """Update progress bar visibility"""
        if self.show_progress.get():
            self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        else:
            self.progress_frame.pack_forget()
    
    def disable_controls(self):
        """Disable all controls during processing"""
        self.rows_entry.config(state=tk.DISABLED)
        self.column_combo.config(state=tk.DISABLED)
        self.algo_combo.config(state=tk.DISABLED)
        self.order_combo.config(state=tk.DISABLED)
        self.timer_check.config(state=tk.DISABLED)
        self.progress_check.config(state=tk.DISABLED)
        self.display_check.config(state=tk.DISABLED)
        self.run_button.config(state=tk.DISABLED)
        self.benchmark_button.config(state=tk.DISABLED)
        self.load_button.config(state=tk.DISABLED)
        self.generate_button.config(state=tk.DISABLED)
        self.export_report_button.config(state=tk.DISABLED)
        self.export_csv_button.config(state=tk.DISABLED)
    
    def enable_controls(self):
        """Enable all controls after processing"""
        self.rows_entry.config(state=tk.NORMAL)
        self.column_combo.config(state="readonly")
        self.algo_combo.config(state="readonly")
        self.order_combo.config(state="readonly")
        self.timer_check.config(state=tk.NORMAL)
        self.progress_check.config(state=tk.NORMAL)
        self.display_check.config(state=tk.NORMAL)
        self.run_button.config(state=tk.NORMAL)
        self.benchmark_button.config(state=tk.NORMAL)
        self.load_button.config(state=tk.NORMAL)
        self.generate_button.config(state=tk.NORMAL)
        self.export_report_button.config(state=tk.NORMAL)
        self.export_csv_button.config(state=tk.NORMAL)
    
    def auto_load_data(self):
        """Automatically load data from ../data directory (relative to script)"""
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Look for data directory at the same level as src
        data_dir = os.path.join(os.path.dirname(script_dir), "data")
        
        if not os.path.exists(data_dir):
            # Try absolute /data path as fallback
            data_dir = "/data"
            if not os.path.exists(data_dir):
                # Try relative data path as fallback
                data_dir = "data"
                if not os.path.exists(data_dir):
                    self.report_text.insert("1.0", "ℹ No data directory found. Please load or generate CSV data.\n")
                    self.report_text.insert(tk.END, f"Expected location: {os.path.join(os.path.dirname(script_dir), 'data')}\n")
                    return
        
        # Find CSV files
        try:
            csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        except Exception as e:
            self.report_text.insert("1.0", f"ℹ Could not access data directory: {e}\n")
            return
        
        if not csv_files:
            self.report_text.insert("1.0", f"ℹ No CSV files found in {data_dir}\n")
            return
        
        # Load the first CSV file
        csv_path = os.path.join(data_dir, csv_files[0])
        self.csv_file_path = csv_path
        
        self.report_text.insert("1.0", f"🔍 Auto-loading data from: {csv_path}\n")
        self.frame.update()
        
        try:
            start_time = time.time()
            
            with open(csv_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                self.csv_data = list(reader)
            
            load_time = time.time() - start_time
            
            # Verify data structure
            if self.csv_data and all(key in self.csv_data[0] for key in ['ID', 'FirstName', 'LastName']):
                self.report_text.insert(tk.END, f"✓ Successfully loaded {len(self.csv_data):,} records\n")
                self.report_text.insert(tk.END, f"✓ Load time: {load_time:.4f}s\n")
                self.report_text.insert(tk.END, f"✓ Data verification: PASSED\n")
                self.report_text.insert(tk.END, f"✓ Columns: ID, FirstName, LastName\n\n")
                
                # Show first 10 records in original table (as they appear - unsorted)
                data_to_show = self.csv_data[:10]
                self.populate_original_table(data_to_show)
                
                self.file_label.config(
                    text=f"✓ {os.path.basename(csv_path)} ({len(self.csv_data):,} records)",
                    fg=DOG_COLORS['success']
                )
            else:
                raise ValueError("CSV must contain ID, FirstName, and LastName columns")
        
        except Exception as e:
            self.report_text.insert(tk.END, f"✗ Auto-load failed: {e}\n")
            self.file_label.config(text="Failed to load", fg=DOG_COLORS['danger'])
    
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
            self.report_text.delete("1.0", tk.END)
            self.report_text.insert("1.0", "🎲 Generating 100,000 random records...\n")
            self.frame.update()
            
            first_names = ["John", "Jane", "Michael", "Emily", "David", "Sarah", "Robert", "Lisa",
                          "James", "Mary", "William", "Patricia", "Richard", "Jennifer", "Joseph",
                          "Linda", "Thomas", "Barbara", "Charles", "Elizabeth"]
            
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
                         "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
                         "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

            ids = list(range(1, 100001))
            random.shuffle(ids)
            
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['ID', 'FirstName', 'LastName'])
                
                for count, i in enumerate(ids, 1):
                    writer.writerow([i, random.choice(first_names), random.choice(last_names)])
                    
                    if count % 10000 == 0:
                        self.report_text.insert(tk.END, f"Generated {count:,}...\n")
                        self.frame.update()
            
            self.report_text.insert(tk.END, "\n✓ Successfully generated 100,000 random records!\n")
            self.report_text.insert(tk.END, f"File: {file_path}\n")
            
            self.csv_file_path = file_path
            self.load_csv_data()
            
            messagebox.showinfo("Success", "Randomized CSV generated successfully!")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate CSV: {e}")
    
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
            # Clear previous results
            for item in self.results_table.get_children():
                self.results_table.delete(item)
            for item in self.original_table.get_children():
                self.original_table.delete(item)
            self.sorted_data = []
            
            self.report_text.delete("1.0", tk.END)
            self.report_text.insert("1.0", f"📁 Loading: {self.csv_file_path}\n")
            self.frame.update()
            
            start_time = time.time()
            
            with open(self.csv_file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                self.csv_data = list(reader)
            
            load_time = time.time() - start_time
            
            # Verify data
            if self.csv_data and all(key in self.csv_data[0] for key in ['ID', 'FirstName', 'LastName']):
                self.report_text.insert(tk.END, f"\n✓ Loaded {len(self.csv_data):,} records\n")
                self.report_text.insert(tk.END, f"✓ Load time: {load_time:.4f}s\n")
                self.report_text.insert(tk.END, f"✓ Data verification: PASSED\n")
                
                # Show first 10 records in original table (as they appear in file - unsorted)
                data_to_show = self.csv_data[:10]
                self.populate_original_table(data_to_show)
                
                self.file_label.config(
                    text=f"✓ {os.path.basename(self.csv_file_path)} ({len(self.csv_data):,} records)",
                    fg=DOG_COLORS['success']
                )
            else:
                raise ValueError("CSV must contain ID, FirstName, and LastName columns")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {e}")
            self.file_label.config(text="Failed to load", fg=DOG_COLORS['danger'])
    
    def update_timer(self, elapsed):
        if self.show_timer.get():
            self.timer_label.config(text=f"{elapsed:.4f}s")
            self.frame.update_idletasks()
    
    def update_progress(self, percent):
        if self.show_progress.get():
            self.progress_bar['value'] = percent
            self.progress_label.config(text=f"{int(percent)}%")
            self.frame.update_idletasks()
    
    def populate_table(self, data):
        """Populate the results table with loading animation"""
        self.is_rendering = True
        self.loading_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.table_frame.pack_forget()
        
        def render_thread():
            try:
                # Clear existing data
                for item in self.results_table.get_children():
                    self.results_table.delete(item)
                
                total = len(data)
                batch_size = 100
                
                # Insert new data in batches
                for i, record in enumerate(data, 1):
                    tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                    self.results_table.insert('', tk.END, values=(
                        i,
                        record['ID'],
                        record['FirstName'],
                        record['LastName']
                    ), tags=(tag,))
                    
                    if i % batch_size == 0 or i == total:
                        percent = (i / total) * 100
                        self.loading_label.config(text=f"Rendering: {i:,} / {total:,} ({percent:.0f}%)")
                        self.frame.update_idletasks()
                
                self.loading_frame.pack_forget()
                self.table_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
            finally:
                self.is_rendering = False
        
        threading.Thread(target=render_thread, daemon=True).start()
    
    def populate_original_table(self, data):
        """Populate the original dataset table"""
        # Clear existing data
        for item in self.original_table.get_children():
            self.original_table.delete(item)
        
        # Insert new data
        for i, record in enumerate(data, 1):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.original_table.insert('', tk.END, values=(
                i,
                record['ID'],
                record['FirstName'],
                record['LastName']
            ), tags=(tag,))
    
    def run_sort(self):
        """Run sorting on CSV data"""
        if not self.csv_data:
            messagebox.showwarning("No Data", "Please load CSV data first!")
            return
        
        if self.is_sorting:
            messagebox.showwarning("Busy", "Already sorting!")
            return
        
        try:
            n_rows = int(self.rows_var.get())
            if n_rows <= 0 or n_rows > len(self.csv_data):
                raise ValueError(f"Rows must be between 1 and {len(self.csv_data)}")
            
            column = self.column_var.get()
            algorithm = self.algorithm_var.get()
            sort_order = self.sort_order.get()
            reverse = (sort_order == "Descending")
            
            # Warning for large O(n²)
            if n_rows > 10000 and algorithm in ["Bubble Sort", "Insertion Sort"]:
                response = messagebox.askyesno(
                    "Performance Warning",
                    f"Sorting {n_rows:,} records with {algorithm} may take a long time.\n\nContinue?"
                )
                if not response:
                    return
            
            self.is_sorting = True
            self.disable_controls()
            self.timer_label.config(text="0.0000s")
            self.progress_bar['value'] = 0
            self.progress_label.config(text="0%")
            self.stop_button.config(state=tk.NORMAL)
            
            self.report_text.delete("1.0", tk.END)
            self.report_text.insert("1.0", f"⚙ Processing {n_rows:,} rows with {algorithm} ({sort_order})...\n\n")
            self.frame.update()
            
            # Show original data in the original table
            data_subset = self.csv_data[:n_rows]
            data_to_show_original = data_subset[:10] if self.show_first_10.get() else data_subset
            self.populate_original_table(data_to_show_original)
            
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
                    
                    algo_map = {
                        "Bubble Sort": SortingAlgorithms.bubble_sort,
                        "Insertion Sort": SortingAlgorithms.insertion_sort,
                        "Merge Sort": SortingAlgorithms.merge_sort
                    }
                    
                    sort_func = algo_map[algorithm]
                    sorted_keys = sort_func(
                        keys,
                        self.update_timer if self.show_timer.get() else None,
                        lambda: not self.is_sorting,
                        self.update_progress if self.show_progress.get() else None,
                        reverse
                    )
                    
                    sort_time = time.time() - start_time
                    
                    # Show completion notification immediately after sort completes
                    messagebox.showinfo("Complete! 🐕", f"Sorted {n_rows:,} records in {sort_time:.4f}s")
                    
                    # Create sorted data
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
                    
                    # Store for export
                    self.last_sort_time = sort_time
                    self.last_algorithm = algorithm
                    self.last_rows = n_rows
                    self.last_column = column
                    
                    # Update report with sorted data
                    self.report_text.delete("1.0", tk.END)
                    self.report_text.insert("1.0", "="*60 + "\n")
                    self.report_text.insert(tk.END, "               SORTING REPORT\n")
                    self.report_text.insert(tk.END, "="*60 + "\n\n")
                    self.report_text.insert(tk.END, f"Algorithm:        {algorithm}\n")
                    self.report_text.insert(tk.END, f"Records Sorted:   {n_rows:,}\n")
                    self.report_text.insert(tk.END, f"Sort Column:      {column}\n")
                    self.report_text.insert(tk.END, f"Sort Order:       {sort_order}\n")
                    self.report_text.insert(tk.END, f"Execution Time:   {sort_time:.4f}s ({sort_time*1000:.2f}ms)\n")
                    self.report_text.insert(tk.END, f"Status:           ✓ Completed\n\n")
                    self.report_text.insert(tk.END, "="*60 + "\n")
                    
                    # Add sorted data to report
                    data_to_show_report = self.sorted_data[:10] if self.show_first_10.get() else self.sorted_data
                    header = f"FIRST 10 SORTED RECORDS" if self.show_first_10.get() else f"ALL {len(self.sorted_data):,} SORTED RECORDS"
                    self.report_text.insert(tk.END, f"{header}\n")
                    self.report_text.insert(tk.END, "="*60 + "\n\n")
                    
                    for i, record in enumerate(data_to_show_report, 1):
                        self.report_text.insert(tk.END, 
                            f"{i:5d}. ID:{record['ID']:>6} | "
                            f"{record['FirstName']:>10} {record['LastName']:<12}\n")
                    
                    self.report_text.insert(tk.END, "\n" + "="*60 + "\n")
                    self.report_text.insert(tk.END, "🐾 Complete! Good dog! 🐾\n")
                    self.report_text.insert(tk.END, "="*60 + "\n")
                    
                    # Update table
                    data_to_show_table = self.sorted_data[:10] if self.show_first_10.get() else self.sorted_data
                    self.populate_table(data_to_show_table)
                    
                    # Update timer and progress
                    self.timer_label.config(text=f"{sort_time:.4f}s")
                    self.progress_bar['value'] = 100
                    self.progress_label.config(text="100%")
                
                except Exception as e:
                    messagebox.showerror("Error! 😿", str(e))
                finally:
                    self.is_sorting = False
                    self.stop_button.config(state=tk.DISABLED)
                    self.enable_controls()
            
            threading.Thread(target=sort_thread, daemon=True).start()
        
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
    
    def stop_sort(self):
        """Stop the current sorting operation"""
        if self.is_sorting:
            self.is_sorting = False
            self.stop_button.config(state=tk.DISABLED)
            self.enable_controls()
            self.report_text.insert(tk.END, "\n⏹ Sorting stopped by user!\n")
            messagebox.showinfo("Stopped", "Sorting operation has been stopped!")
    
    def run_benchmark(self):
        """Run comprehensive benchmark"""
        if not self.csv_data:
            messagebox.showwarning("No Data", "Please load CSV data first!")
            return
        
        if self.is_sorting:
            messagebox.showwarning("Busy", "Already processing!")
            return
        
        algorithm = self.algorithm_var.get()
        
        # Safety Check
        if algorithm in ["Bubble Sort", "Insertion Sort"]:
            response = messagebox.askyesno(
                "Performance Warning",
                f"Benchmarking 100,000 records with {algorithm} could take hours.\n\nContinue?"
            )
            if not response:
                return

        self.is_sorting = True
        self.disable_controls()
        self.stop_button.config(state=tk.NORMAL)
        self.timer_label.config(text="0.0000s")
        self.progress_bar['value'] = 0
        self.progress_label.config(text="0%")
        
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert("1.0", f"📊 Running benchmark for {algorithm}...\n\n")
        self.frame.update()
        
        def benchmark_thread():
            try:
                sizes = [1000, 10000, 100000]
                results = {}
                
                algo_map = {
                    "Bubble Sort": SortingAlgorithms.bubble_sort,
                    "Insertion Sort": SortingAlgorithms.insertion_sort,
                    "Merge Sort": SortingAlgorithms.merge_sort
                }
                sort_func = algo_map[algorithm]
                
                # Track overall benchmark
                benchmark_start_time = time.time()
                total_records = sum(sizes[:len([s for s in sizes if s <= len(self.csv_data)])])
                records_processed = 0

                for idx, size in enumerate(sizes):
                    if not self.is_sorting:
                        break
                    
                    if size > len(self.csv_data):
                        continue
                    
                    self.report_text.insert(tk.END, f"Testing {size:,} rows...\n")
                    self.frame.update()
                    
                    data_subset = self.csv_data[:size]
                    keys = [int(row['ID']) for row in data_subset]
                    
                    # Individual test with progress tracking
                    start_time = time.time()
                    
                    # Create a progress callback that updates based on total records
                    def progress_callback(percent):
                        if self.show_progress.get():
                            # Calculate overall progress based on records processed
                            base_progress = (records_processed / total_records) * 100
                            current_test_contribution = (size / total_records) * 100
                            overall_progress = base_progress + (percent / 100) * current_test_contribution
                            self.progress_bar['value'] = overall_progress
                            self.progress_label.config(text=f"{int(overall_progress)}%")
                            self.frame.update_idletasks()
                    
                    sort_func(keys, None, lambda: not self.is_sorting, progress_callback if self.show_progress.get() else None)
                    exec_time = time.time() - start_time
                    
                    results[size] = exec_time
                    records_processed += size
                    
                    # Update timer to show total elapsed time
                    total_elapsed = time.time() - benchmark_start_time
                    if self.show_timer.get():
                        self.timer_label.config(text=f"{total_elapsed:.4f}s")
                    
                    self.report_text.insert(tk.END, f"  ✓ Completed in {exec_time:.4f}s\n")
                    self.frame.update()
                
                # Calculate total elapsed time
                total_elapsed = time.time() - benchmark_start_time
                
                # Show completion notification immediately
                if self.is_sorting:
                    messagebox.showinfo("Complete! 🐕", f"{algorithm} benchmark completed in {total_elapsed:.4f}s!")
                
                # Display Results
                self.report_text.delete("1.0", tk.END)
                self.report_text.insert("1.0", "="*60 + "\n")
                self.report_text.insert(tk.END, f"           BENCHMARK: {algorithm.upper()}\n")
                self.report_text.insert(tk.END, "="*60 + "\n\n")
                self.report_text.insert(tk.END, f"{'Size':<15} {'Time (sec)':<20} {'Time (ms)':<20}\n")
                self.report_text.insert(tk.END, "-"*60 + "\n")
                
                for size in sizes:
                    if size in results:
                        time_sec = results[size]
                        time_ms = time_sec * 1000
                        self.report_text.insert(tk.END, f"{size:<15,} {time_sec:<20.4f} {time_ms:<20.2f}\n")
                
                self.report_text.insert(tk.END, "\n" + "="*60 + "\n")
                self.report_text.insert(tk.END, f"\nTotal benchmark time: {total_elapsed:.4f}s\n")
                self.report_text.insert(tk.END, "🐾 Benchmark complete! 🐾\n")
                
                self.progress_bar['value'] = 100
                self.progress_label.config(text="100%")
                
                if self.show_timer.get():
                    self.timer_label.config(text=f"{total_elapsed:.4f}s")
                    
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                self.is_sorting = False
                self.stop_button.config(state=tk.DISABLED)
                self.enable_controls()
        
        threading.Thread(target=benchmark_thread, daemon=True).start()
    
    def export_report(self):
        """Export full report"""
        if not self.sorted_data:
            messagebox.showwarning("No Data", "Run sort first!")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile="sort_report.txt"
        )
        
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write("="*70 + "\n")
                    f.write("                    SORTING REPORT\n")
                    f.write("="*70 + "\n\n")
                    f.write(f"Algorithm:        {self.last_algorithm}\n")
                    f.write(f"Records Sorted:   {self.last_rows:,}\n")
                    f.write(f"Sort Column:      {self.last_column}\n")
                    f.write(f"Execution Time:   {self.last_sort_time:.4f}s ({self.last_sort_time*1000:.2f}ms)\n\n")
                    f.write("="*70 + "\n")
                    f.write(f"                SORTED DATA ({len(self.sorted_data):,} records)\n")
                    f.write("="*70 + "\n\n")
                    
                    for i, record in enumerate(self.sorted_data, 1):
                        f.write(f"{i:5d}. ID:{record['ID']:>6} | {record['FirstName']:>10} {record['LastName']:<12}\n")
                    
                    f.write("\n" + "="*70 + "\n")
                
                messagebox.showinfo("Saved", "Report exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def export_sorted_csv(self):
        """Export sorted CSV file"""
        if not self.sorted_data:
            messagebox.showwarning("No Data", "Run sort first!")
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
                
                messagebox.showinfo("Saved", f"Exported {len(self.sorted_data):,} sorted records to CSV!")
            except Exception as e:
                messagebox.showerror("Error", str(e))


class ArfArfSort:
    """🐕 Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ArfArf Sort - Professional Edition")
        self.root.geometry("1200x1000")
        self.root.configure(bg=DOG_COLORS['bg'])
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.main_container = tk.Frame(root, bg=DOG_COLORS['bg'])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        self.show_home()
    
    def clear_container(self):
        """Clears the current frame content"""
        for widget in self.main_container.winfo_children():
            widget.destroy()
    
    def show_home(self):
        """Main Menu"""
        self.clear_container()
        
        # Title bar
        title_frame = tk.Frame(self.main_container, bg=DOG_COLORS['primary'], height=150)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_container = tk.Frame(title_frame, bg=DOG_COLORS['primary'])
        title_container.pack(expand=True)
        
        tk.Label(
            title_container,
            text="🐕 ",
            font=("Segoe UI", 48),
            bg=DOG_COLORS['primary'],
            fg=DOG_COLORS['accent']
        ).pack(side=tk.LEFT)
        
        tk.Label(
            title_container,
            text="ArfArf Sort",
            font=("Segoe UI", 36, "bold"),
            bg=DOG_COLORS['primary'],
            fg="white"
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            title_container,
            text="🦴",
            font=("Segoe UI", 48),
            bg=DOG_COLORS['primary'],
            fg=DOG_COLORS['accent']
        ).pack(side=tk.LEFT)
        
        tk.Label(
            title_frame,
            text="Professional Algorithm Analysis Laboratory",
            font=("Segoe UI", 14),
            bg=DOG_COLORS['primary'],
            fg=DOG_COLORS['light']
        ).pack(pady=(0, 20))
        
        # Menu
        menu_frame = tk.Frame(self.main_container, bg=DOG_COLORS['bg'])
        menu_frame.pack(expand=True)
        
        tk.Button(
            menu_frame,
            text="🏆 PRELIM LAB EXAM",
            font=("Segoe UI", 16, "bold"),
            bg=DOG_COLORS['accent'],
            fg=DOG_COLORS['text'],
            width=35,
            height=3,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.show_exam
        ).pack(pady=20)
        
        footer = tk.Frame(self.main_container, bg=DOG_COLORS['bg'])
        footer.pack(side=tk.BOTTOM, pady=30)
        
        tk.Label(
            footer,
            text="🐾 ",
            font=("Segoe UI", 14),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['primary']
        ).pack(side=tk.LEFT)
        
        tk.Label(
            footer,
            text="Ready to start? Click above to begin.",
            font=("Segoe UI", 11),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['text']
        ).pack(side=tk.LEFT)
        
        tk.Label(
            footer,
            text=" 🐾",
            font=("Segoe UI", 14),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['primary']
        ).pack(side=tk.LEFT)
    
    def create_back_button(self, parent):
        """Standard back button"""
        btn_frame = tk.Frame(parent, bg=DOG_COLORS['bg'])
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=15)
        
        tk.Button(
            btn_frame,
            text="← Back to Home",
            font=("Segoe UI", 10),
            bg=DOG_COLORS['secondary'],
            fg="white",
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.show_home
        ).pack()
    
    def show_exam(self):
        """Show Prelim Exam"""
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
