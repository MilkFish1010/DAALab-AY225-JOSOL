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

class PrelimLab2:
    """🦴 Prelim Lab Work 2 - Comparative Analysis of Sorting Algorithms"""
    
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.dataset = []
        self.sorted_arrays = {}
        self.show_timer = tk.BooleanVar(value=False)
        self.is_sorting = False
        self.show_first_10 = tk.BooleanVar(value=True)
        self.setup_ui()
        self.update_timer_visibility()
    
    def setup_ui(self):
        # Title
        title = tk.Label(
            self.frame,
            text="🦴 Prelim Lab Work 2: Multi-Algorithm Benchmarking 🐕",
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
            "🐾 Objective: Compare three distinct algorithms\n\n"
            "Algorithms:\n"
            "1. Bubble Sort - O(n²) exchange sort\n"
            "2. Insertion Sort - O(n²) comparison sort\n"
            "3. Merge Sort - O(n log n) divide-and-conquer\n"
            "Import TXT datasets or generate random! Full results + export! 🦮"
        )
        instructions.config(state=tk.DISABLED)
        
        # Controls
        control_frame = tk.Frame(self.frame, bg=DOG_COLORS['bg'])
        control_frame.pack(pady=15)
        
        # Left side - Dataset
        left = tk.Frame(control_frame, bg=DOG_COLORS['bg'])
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            left,
            text="🎲 Dataset Size:",
            font=("Arial", 10, "bold"),
            bg=DOG_COLORS['bg']
        ).grid(row=0, column=0, padx=5, pady=5)
        
        self.size_var = tk.StringVar(value="10000")
        tk.Entry(
            left,
            textvariable=self.size_var,
            font=("Arial", 10),
            width=10
        ).grid(row=0, column=1, padx=5, pady=5)
        
        btn_frame = tk.Frame(left, bg=DOG_COLORS['bg'])
        btn_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        tk.Button(
            btn_frame,
            text="📁 Import TXT",
            bg=DOG_COLORS['secondary'],
            fg="white",
            command=self.import_dataset,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=3)
        
        tk.Button(
            btn_frame,
            text="🎲 Generate",
            bg=DOG_COLORS['accent'],
            fg=DOG_COLORS['dark'],
            command=self.generate_dataset,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=3)
        
        # Middle - Algorithm selection
        middle = tk.Frame(control_frame, bg=DOG_COLORS['bg'])
        middle.pack(side=tk.LEFT, padx=20)
        
        tk.Label(
            middle,
            text="Algorithm:",
            font=("Arial", 10, "bold"),
            bg=DOG_COLORS['bg']
        ).pack()
        
        self.algorithm_var = tk.StringVar(value="Bubble Sort")
        ttk.Combobox(
            middle,
            textvariable=self.algorithm_var,
            values=["Bubble Sort", "Insertion Sort", "Merge Sort"],
            state="readonly",
            font=("Arial", 10),
            width=13
        ).pack(pady=5)
        
        tk.Checkbutton(
            middle,
            text="🐾 Timer (has performance impact)",
            variable=self.show_timer,
            bg=DOG_COLORS['bg'],
            font=("Arial", 9),
            command=self.update_timer_visibility
        ).pack()
        
        tk.Checkbutton(
            middle,
            text="🐾 Show first 10 only",
            variable=self.show_first_10,
            bg=DOG_COLORS['bg'],
            font=("Arial", 9)
        ).pack()
        
        # Right - Action buttons
        right = tk.Frame(control_frame, bg=DOG_COLORS['bg'])
        right.pack(side=tk.RIGHT)
        
        tk.Button(
            right,
            text="🏃 Run Selected",
            font=("Arial", 10, "bold"),
            bg=DOG_COLORS['success'],
            fg="white",
            padx=15,
            pady=8,
            command=self.run_single
        ).pack(pady=3)
        
        self.stop_button_single = tk.Button(
            right,
            text="⏹️ Stop",
            font=("Arial", 10, "bold"),
            bg=DOG_COLORS['danger'],
            fg="white",
            padx=15,
            pady=8,
            command=self.stop_sort,
            state=tk.DISABLED
        )
        self.stop_button_single.pack(pady=3)
        
        tk.Button(
            right,
            text="🔄 Compare All",
            font=("Arial", 10, "bold"),
            bg=DOG_COLORS['warning'],
            fg="white",
            padx=15,
            pady=8,
            command=self.run_all
        ).pack(pady=3)
        
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
            text="📋 Full Results:",
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
            text="📄 Export All Data",
            bg=DOG_COLORS['accent'],
            fg=DOG_COLORS['dark'],
            command=self.export_all_data,
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
    
    def import_dataset(self):
        """Import from TXT"""
        path = filedialog.askopenfilename(
            title="Import Dataset",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not path:
            return
        
        try:
            with open(path, 'r') as f:
                self.dataset = [int(line.strip()) for line in f if line.strip()]
            
            self.size_var.set(str(len(self.dataset)))
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", f"🐾 Imported {len(self.dataset)} numbers\n")
            
            messagebox.showinfo("Success! 🐕", f"Loaded {len(self.dataset)} numbers")
        
        except Exception as e:
            messagebox.showerror("Error! 😿", str(e))
    
    def generate_dataset(self):
        """Generate random dataset"""
        try:
            size = int(self.size_var.get())
            if size <= 0:
                raise ValueError("Size must be positive")
            
            self.dataset = [random.randint(1, 100000) for _ in range(size)]
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", f"🎲 Generated {size} numbers\n")
            
            messagebox.showinfo("Success! 🐕", f"Generated {size} numbers")
        
        except ValueError as e:
            messagebox.showerror("Error! 😿", str(e))
    
    def update_timer(self, elapsed):
        if self.show_timer.get():
            self.timer_label.config(text=f"⏱️ {elapsed:.4f}s")
            self.frame.update_idletasks()
    
    def run_algorithm(self, algorithm_name: str, dataset: List) -> Tuple[List, float]:
        """Run a specific sorting algorithm"""
        start_time = time.time()
        
        if algorithm_name == "Bubble Sort":
            sorted_array = SortingAlgorithms.bubble_sort(
                dataset, self.update_timer if self.show_timer.get() else None, lambda: not self.is_sorting)
        elif algorithm_name == "Insertion Sort":
            sorted_array = SortingAlgorithms.insertion_sort(
                dataset, self.update_timer if self.show_timer.get() else None, lambda: not self.is_sorting)
        else:
            sorted_array = SortingAlgorithms.merge_sort(
                dataset, self.update_timer if self.show_timer.get() else None, lambda: not self.is_sorting)
        
        execution_time = time.time() - start_time
        return sorted_array, execution_time
    
    def run_single(self):
        """Run single algorithm"""
        if not self.dataset:
            messagebox.showwarning("No Data! 🐕", "Import or generate dataset first!")
            return
        
        if self.is_sorting:
            messagebox.showwarning("Busy! 🐕", "Already sorting!")
            return
        
        self.is_sorting = True
        algorithm = self.algorithm_var.get()
        
        self.timer_label.config(text="⏱️ 0.0000s")
        self.stop_button_single.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", f"🐕 Running {algorithm}...\n\n")
        self.frame.update()
        
        def sort_thread():
            try:
                sorted_array, exec_time = self.run_algorithm(algorithm, self.dataset)
                self.sorted_arrays = {algorithm: sorted_array}
                
                is_sorted = all(sorted_array[i] <= sorted_array[i+1] 
                              for i in range(len(sorted_array)-1))
                
                self.results_text.insert(tk.END, "="*70 + "\n")
                self.results_text.insert(tk.END, f"🦴 {algorithm.upper()} RESULTS 🦴\n")
                self.results_text.insert(tk.END, "="*70 + "\n\n")
                self.results_text.insert(tk.END, f"Size: {len(self.dataset)}\n")
                self.results_text.insert(tk.END, f"Time: {exec_time:.4f}s ({exec_time*1000:.2f}ms)\n")
                self.results_text.insert(tk.END, f"Status: {'✅ SORTED' if is_sorted else '❌ ERROR'}\n\n")
                
                array_to_show = sorted_array[:10] if self.show_first_10.get() else sorted_array
                header = "FIRST 10 SORTED RECORDS" if self.show_first_10.get() else f"COMPLETE SORTED ARRAY ({len(sorted_array)} elements)"
                self.results_text.insert(tk.END, "="*70 + "\n")
                self.results_text.insert(tk.END, f"{header}\n")
                self.results_text.insert(tk.END, "="*70 + "\n")
                
                for num in array_to_show:
                    self.results_text.insert(tk.END, f"{num}\n")
                
                self.results_text.insert(tk.END, "\n" + "="*70 + "\n")
                self.results_text.insert(tk.END, "🐾 Complete! 🐾\n" + "="*70 + "\n")
                
                self.timer_label.config(text=f"⏱️ {exec_time:.4f}s")
                
                messagebox.showinfo("Done! 🐕", f"{algorithm} completed in {exec_time:.4f}s")
            
            except Exception as e:
                messagebox.showerror("Error! 😿", str(e))
            finally:
                self.is_sorting = False
                self.stop_button_single.config(state=tk.DISABLED)
        
        threading.Thread(target=sort_thread, daemon=True).start()
    
    def stop_sort(self):
        """Stop the current sorting operation"""
        if self.is_sorting:
            self.is_sorting = False
            self.stop_button_single.config(state=tk.DISABLED)
            self.results_text.insert(tk.END, "\n⏹️ Sorting stopped by user!\n")
            messagebox.showinfo("Stopped! 🐕", "Sorting operation has been stopped!")
    
    def run_all(self):
        """Compare all algorithms"""
        if not self.dataset:
            messagebox.showwarning("No Data! 🐕", "Import or generate dataset first!")
            return
        
        if self.is_sorting:
            messagebox.showwarning("Busy! 🐕", "Already sorting!")
            return
        
        self.is_sorting = True
        
        self.timer_label.config(text="⏱️ 0.0000s")
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", f"🐕 Comparing all algorithms...\n\n")
        self.frame.update()
        
        def compare_thread():
            try:
                algorithms = ["Bubble Sort", "Insertion Sort", "Merge Sort"]
                results = {}
                self.sorted_arrays = {}
                
                for algo in algorithms:
                    self.results_text.insert(tk.END, f"Running {algo}...\n")
                    self.frame.update()
                    
                    sorted_array, exec_time = self.run_algorithm(algo, self.dataset)
                    results[algo] = exec_time
                    self.sorted_arrays[algo] = sorted_array
                
                # Display comparison
                self.results_text.insert(tk.END, "\n\n" + "="*70 + "\n")
                self.results_text.insert(tk.END, "🦴 COMPARATIVE ANALYSIS 🦴\n")
                self.results_text.insert(tk.END, "="*70 + "\n\n")
                self.results_text.insert(tk.END, f"Dataset Size: {len(self.dataset)} elements\n\n")
                
                self.results_text.insert(tk.END, f"{'Algorithm':<20} {'Time (sec)':<15} {'Time (ms)':<15} {'Complexity'}\n")
                self.results_text.insert(tk.END, "-"*70 + "\n")
                
                complexities = {
                    "Bubble Sort": "O(n²)",
                    "Insertion Sort": "O(n²)",
                    "Merge Sort": "O(n log n)"
                }
                
                for algo in algorithms:
                    time_sec = results[algo]
                    time_ms = time_sec * 1000
                    complexity = complexities[algo]
                    self.results_text.insert(tk.END, 
                        f"{algo:<20} {time_sec:<15.4f} {time_ms:<15.2f} {complexity}\n")
                
                fastest = min(results, key=results.get)
                self.results_text.insert(tk.END, f"\n🏆 Fastest: {fastest} ({results[fastest]:.4f}s)\n")
                
                if results["Bubble Sort"] > 0:
                    ratio = results["Bubble Sort"] / results["Merge Sort"]
                    self.results_text.insert(tk.END, 
                        f"📊 Merge Sort is {ratio:.2f}x faster than Bubble Sort!\n")
                
                if self.show_first_10.get():
                    self.results_text.insert(tk.END, "\n\n" + "="*70 + "\nFIRST 10 RECORDS FROM EACH ALGORITHM\n" + "="*70 + "\n\n")
                    for algo in algorithms:
                        self.results_text.insert(tk.END, f"{algo}:\n")
                        for num in self.sorted_arrays[algo][:10]:
                            self.results_text.insert(tk.END, f"{num}\n")
                        self.results_text.insert(tk.END, "\n")
                
                self.results_text.insert(tk.END, "\n🐾 All done! Good dogs! 🐾\n")
                
                messagebox.showinfo("Success! 🐕", "All algorithms completed!")
            
            except Exception as e:
                messagebox.showerror("Error! 😿", str(e))
            finally:
                self.is_sorting = False
        
        threading.Thread(target=compare_thread, daemon=True).start()
    
    def export_report(self):
        """Export full report"""
        if not self.sorted_arrays:
            messagebox.showwarning("No Data! 🐕", "Run algorithms first!")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile="comparison_report.txt"
        )
        
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.get("1.0", tk.END))
                
                messagebox.showinfo("Saved! 🐕", "Report exported!")
            except Exception as e:
                messagebox.showerror("Error! 😿", str(e))
    
    def export_all_data(self):
        """Export all sorted arrays"""
        if not self.sorted_arrays:
            messagebox.showwarning("No Data! 🐕", "Run algorithms first!")
            return
        
        folder = filedialog.askdirectory(title="Select Export Folder")
        
        if folder:
            try:
                for algo_name, sorted_array in self.sorted_arrays.items():
                    filename = f"sorted_{algo_name.replace(' ', '_').lower()}.txt"
                    filepath = os.path.join(folder, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        for num in sorted_array:
                            f.write(f"{num}\n")
                
                messagebox.showinfo("Saved! 🐕", 
                    f"Exported {len(self.sorted_arrays)} sorted arrays!")
            except Exception as e:
                messagebox.showerror("Error! 😿", str(e))

class ArfArfSort:
    """🐕 Specialized Application for Prelim Lab Work 2 🦴"""
    
    def __init__(self, root):
        self.root = root
        # Updated title to reflect specific lab
        self.root.title("🐕 ArfArf Sort - Prelim Lab Work 2 🦴")
        self.root.geometry("950x825")
        self.root.configure(bg=DOG_COLORS['bg'])
        self.root.resizable(False, False)
        
        self.main_container = tk.Frame(root, bg=DOG_COLORS['bg'])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Launch Lab 2 immediately
        self.show_lab2()
    
    def clear_container(self):
        """Removes existing widgets before drawing new ones"""
        for widget in self.main_container.winfo_children():
            widget.destroy()
    
    def show_lab2(self):
        """Initializes the Prelim Lab Work 2 interface"""
        self.clear_container()
        
        # Main frame for the lab content
        lab_frame = tk.Frame(self.main_container, bg=DOG_COLORS['bg'])
        lab_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instantiate your Lab 2 logic here
        # (Assuming PrelimLab2 is defined elsewhere in your script)
        PrelimLab2(lab_frame)
        
        # Footer branding (replaced Back button with status text)
        tk.Label(
            lab_frame,
            text="🐾 Algorithm Laboratory: Lab Work 2 Active 🐾",
            font=("Arial", 10, "italic"),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['text']
        ).pack(side=tk.BOTTOM, pady=10)

def main():
    root = tk.Tk()
    app = ArfArfSort(root)
    root.mainloop()

if __name__ == "__main__":
    main()