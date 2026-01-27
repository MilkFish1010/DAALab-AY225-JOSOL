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
    
class PrelimLab1:
    """🐕 Prelim Lab Work 1 - Bubble Sort with 10,000 elements"""
    
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.dataset = []
        self.sorted_array = []
        self.show_timer = tk.BooleanVar(value=False)  # OFF by default for speed
        self.is_sorting = False
        self.show_first_10 = tk.BooleanVar(value=True)
        self.setup_ui()
        self.update_timer_visibility()
    
    def setup_ui(self):
        # Title with dog theme
        title = tk.Label(
            self.frame,
            text="🐕 Prelim Lab Work 1: Bubble Sort Analysis 🦴",
            font=("Comic Sans MS", 16, "bold"),
            bg=DOG_COLORS['primary'],
            fg=DOG_COLORS['accent'],
            pady=15
        )
        title.pack(fill=tk.X)
        
        # Instructions
        instructions = tk.Text(
            self.frame,
            height=7,
            wrap=tk.WORD,
            bg=DOG_COLORS['light'],
            font=("Arial", 10),
            fg=DOG_COLORS['text']
        )
        instructions.pack(padx=20, pady=10, fill=tk.BOTH)
        instructions.insert("1.0", 
            "🐾 Objective: Bubble Sort performance measurement\n"
            "📊 Dataset: 10,000 integers (or import from TXT - one per line!)\n"
            "⚙️ Algorithm: Classic Bubble Sort (O(n²))\n"
            "📈 Output: FULL sorted array + execution time + export options\n\n"
            "🦮 Dog Wisdom: Like training a puppy, we compare neighbors!\n"
            "   TXT Format: One number per line. Woof! 🐶"
        )
        instructions.config(state=tk.DISABLED)
        
        # Controls
        control_frame = tk.Frame(self.frame, bg=DOG_COLORS['bg'])
        control_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # Left - Dataset controls
        left_controls = tk.Frame(control_frame, bg=DOG_COLORS['bg'])
        left_controls.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            left_controls,
            text="🎲 Dataset Size:",
            font=("Arial", 10, "bold"),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['dark']
        ).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.size_var = tk.StringVar(value="10000")
        tk.Entry(
            left_controls,
            textvariable=self.size_var,
            font=("Arial", 10),
            width=10
        ).grid(row=0, column=1, padx=5, pady=5)
        
        # Import/Generate buttons
        btn_frame = tk.Frame(left_controls, bg=DOG_COLORS['bg'])
        btn_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        tk.Button(
            btn_frame,
            text="📁 Import TXT",
            font=("Arial", 9),
            bg=DOG_COLORS['secondary'],
            fg="white",
            command=self.import_dataset,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=3)
        
        tk.Button(
            btn_frame,
            text="🎲 Generate",
            font=("Arial", 9),
            bg=DOG_COLORS['accent'],
            fg=DOG_COLORS['dark'],
            command=self.generate_dataset,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=3)
        
        # Right - Action buttons
        right_controls = tk.Frame(control_frame, bg=DOG_COLORS['bg'])
        right_controls.pack(side=tk.RIGHT)
        
        tk.Checkbutton(
            right_controls,
            text="🐾 Timer (has performance impact)",
            variable=self.show_timer,
            font=("Arial", 9),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['dark'],
            command=self.update_timer_visibility
        ).pack()
        
        tk.Checkbutton(
            right_controls,
            text="🐾 Show first 10 only",
            variable=self.show_first_10,
            font=("Arial", 9),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['dark']
        ).pack()
        
        tk.Button(
            right_controls,
            text="🏃 Run Sort",
            font=("Arial", 10, "bold"),
            bg=DOG_COLORS['success'],
            fg="white",
            padx=15,
            pady=6,
            command=self.run_sort,
            cursor="hand2"
        ).pack(pady=2)
        
        self.stop_button = tk.Button(
            right_controls,
            text="⏹️ Stop",
            font=("Arial", 10, "bold"),
            bg=DOG_COLORS['danger'],
            fg="white",
            padx=15,
            pady=6,
            command=self.stop_sort,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.stop_button.pack(pady=2)
        
        # Timer
        timer_frame = tk.Frame(self.frame, bg=DOG_COLORS['bg'])
        timer_frame.pack(padx=20, fill=tk.X)
        
        self.timer_label = tk.Label(
            timer_frame,
            text="⏱️ Time: 0.0000s",
            font=("Arial", 11, "bold"),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['danger']
        )
        self.timer_label.pack(anchor=tk.W)
        
        # Results
        tk.Label(
            self.frame,
            text="📋 Full Results:",
            font=("Arial", 11, "bold"),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['dark']
        ).pack(anchor=tk.W, padx=20, pady=(10,0))
        
        self.results_text = scrolledtext.ScrolledText(
            self.frame,
            height=12,
            wrap=tk.WORD,
            font=("Courier", 9),
            bg="white"
        )
        self.results_text.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        
        # Export buttons
        export_frame = tk.Frame(self.frame, bg=DOG_COLORS['bg'])
        export_frame.pack(pady=10)
        
        tk.Button(
            export_frame,
            text="💾 Export Report",
            font=("Arial", 9, "bold"),
            bg=DOG_COLORS['secondary'],
            fg="white",
            padx=12,
            pady=5,
            command=self.export_report,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            export_frame,
            text="📄 Export Data",
            font=("Arial", 9, "bold"),
            bg=DOG_COLORS['accent'],
            fg=DOG_COLORS['dark'],
            padx=12,
            pady=5,
            command=self.export_data,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        # Add a status bar at the bottom
        self.status_var = tk.StringVar()
        self.status_var.set("Ready! 🐕")
        status_bar = tk.Label(
            self.frame,
            textvariable=self.status_var,
            font=("Arial", 8),
            bg=DOG_COLORS['light'],
            fg=DOG_COLORS['text'],
            anchor='w'
        )
        status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def update_timer_visibility(self):
        """Update timer label visibility based on checkbox"""
        if self.show_timer.get():
            self.timer_label.pack(anchor=tk.W)
        else:
            self.timer_label.pack_forget()
    
    def import_dataset(self):
        """Import dataset from TXT file (one number per line)"""
        path = filedialog.askopenfilename(
            title="🐕 Select Dataset File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not path:
            return
        
        try:
            with open(path, 'r') as f:
                self.dataset = [int(line.strip()) for line in f if line.strip()]
            
            self.size_var.set(str(len(self.dataset)))
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", f"🐾 Imported {len(self.dataset)} numbers from {os.path.basename(path)}\n")
            
            messagebox.showinfo("Success! 🐕", f"Loaded {len(self.dataset)} numbers")
        
        except Exception as e:
            messagebox.showerror("Error! 😿", f"Failed to import: {e}")
    
    def generate_dataset(self):
        """Generate random dataset"""
        try:
            size = int(self.size_var.get())
            if size <= 0:
                raise ValueError("Size must be positive")
            
            self.dataset = [random.randint(1, 100000) for _ in range(size)]
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", f"🎲 Generated {size} random numbers!\n")
            
            messagebox.showinfo("Success! 🐕", f"Generated {size} numbers")
        
        except ValueError as e:
            messagebox.showerror("Error! 😿", str(e))
    
    def update_timer(self, elapsed):
        """Update timer display"""
        if self.show_timer.get():
            self.timer_label.config(text=f"⏱️ {elapsed:.4f}s")
            self.frame.update_idletasks()
    
    def run_sort(self):
        """Run Bubble Sort"""
        if not self.dataset:
            messagebox.showwarning("No Data! 🐕", "Please import or generate dataset first!")
            return
        
        if self.is_sorting:
            messagebox.showwarning("Busy! 🐕", "Sorting is already in progress!")
            return
        
        self.is_sorting = True
        self.timer_label.config(text="⏱️ Time: 0.0000s")
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Sorting in progress... 🐕")
        
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", f"🐕 Starting Bubble Sort with {len(self.dataset)} elements...\n\n")
        self.frame.update()
        
        def sort_thread():
            try:
                start_time = time.time()
                
                self.sorted_array = SortingAlgorithms.bubble_sort(
                    self.dataset,
                    timer_cb=self.update_timer if self.show_timer.get() else None,
                    stop_cb=lambda: not self.is_sorting
                )
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Verify correctness
                is_sorted = all(self.sorted_array[i] <= self.sorted_array[i+1] 
                               for i in range(len(self.sorted_array)-1))
                
                # Display FULL results
                self.results_text.insert(tk.END, f"{'='*70}\n")
                self.results_text.insert(tk.END, f"🦴 BUBBLE SORT RESULTS 🦴\n")
                self.results_text.insert(tk.END, f"{'='*70}\n\n")
                self.results_text.insert(tk.END, f"Dataset Size: {len(self.dataset)} elements\n")
                self.results_text.insert(tk.END, f"Algorithm: Bubble Sort (O(n²))\n")
                self.results_text.insert(tk.END, f"Execution Time: {execution_time:.4f} seconds ({execution_time*1000:.2f} ms)\n")
                self.results_text.insert(tk.END, f"Verification: {'✅ PASSED (Good boy!)' if is_sorted else '❌ FAILED (Bad dog!)'}\n\n")
                
                self.results_text.insert(tk.END, f"{'='*70}\n")
                self.results_text.insert(tk.END, f"COMPLETE SORTED ARRAY ({len(self.sorted_array)} elements)\n")
                self.results_text.insert(tk.END, f"{'='*70}\n\n")
                
                # Display elements based on toggle
                array_to_show = self.sorted_array[:10] if self.show_first_10.get() else self.sorted_array
                header = "FIRST 10 SORTED RECORDS" if self.show_first_10.get() else f"COMPLETE SORTED ARRAY ({len(self.sorted_array)} elements)"
                self.results_text.insert(tk.END, f"{'='*70}\n")
                self.results_text.insert(tk.END, f"{header}\n")
                self.results_text.insert(tk.END, f"{'='*70}\n\n")
                
                for num in array_to_show:
                    self.results_text.insert(tk.END, f"{num}\n")
                
                self.results_text.insert(tk.END, f"\n{'='*70}\n")
                self.results_text.insert(tk.END, f"🐾 Sorting complete! Good dog! 🐾\n")
                self.results_text.insert(tk.END, f"{'='*70}\n")
                
                self.timer_label.config(text=f"⏱️ Time: {execution_time:.4f}s")
                
                messagebox.showinfo("Success! 🐕", 
                    f"Bubble Sort completed in {execution_time:.4f} seconds!\n"
                    f"{'Sorted correctly! Good boy! 🦴' if is_sorted else 'Error in sorting! 😿'}")
                
                self.status_var.set("Sorting complete! ✅")
            
            except Exception as e:
                messagebox.showerror("Error! 😿", f"An error occurred: {e}")
            
            finally:
                self.is_sorting = False
                self.stop_button.config(state=tk.DISABLED)
        
        threading.Thread(target=sort_thread, daemon=True).start()
    
    def stop_sort(self):
        """Stop the current sorting operation"""
        if self.is_sorting:
            self.is_sorting = False
            self.stop_button.config(state=tk.DISABLED)
            self.results_text.insert(tk.END, "\n⏹️ Sorting stopped by user!\n")
            self.status_var.set("Sorting stopped by user! ⏹️")
            messagebox.showinfo("Stopped! 🐕", "Sorting operation has been stopped!")
    
    def export_report(self):
        """Export full report to TXT"""
        if not self.sorted_array:
            messagebox.showwarning("No Results! 🐕", "Please run Bubble Sort first!")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="bubble_sort_report.txt"
        )
        
        if path:
            try:
                content = self.results_text.get("1.0", tk.END)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                messagebox.showinfo("Exported! 🐕", 
                    f"Report saved to {os.path.basename(path)}")
            
            except Exception as e:
                messagebox.showerror("Error! 😿", f"Failed to export: {e}")
    
    def export_data(self):
        """Export sorted data only (one per line)"""
        if not self.sorted_array:
            messagebox.showwarning("No Results! 🐕", "Please run Bubble Sort first!")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="sorted_data.txt"
        )
        
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    for num in self.sorted_array:
                        f.write(f"{num}\n")
                
                messagebox.showinfo("Exported! 🐕", 
                    f"Sorted data ({len(self.sorted_array)} numbers) saved to {os.path.basename(path)}")
            
            except Exception as e:
                messagebox.showerror("Error! 😿", f"Failed to export: {e}")

class ArfArfSort:
    """🐕 Main application class - Lab 1 Only Edition"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🐕 ArfArf Sort - Prelim Lab 1 🦴")
        self.root.geometry("950x825")
        self.root.configure(bg=DOG_COLORS['bg'])
        self.root.resizable(False, False)
        
        self.main_container = tk.Frame(root, bg=DOG_COLORS['bg'])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Start directly with Lab 1
        self.show_lab1()
    
    def clear_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
    
    def show_lab1(self):
        self.clear_container()
        lab_frame = tk.Frame(self.main_container, bg=DOG_COLORS['bg'])
        lab_frame.pack(fill=tk.BOTH, expand=True)
        
        # This calls your specific Lab 1 class
        PrelimLab1(lab_frame)
        
        # Optional: Add a footer instead of a back button since there is nowhere to go back to
        tk.Label(
            lab_frame,
            text="🐾 Lab 1: Algorithm Analysis Laboratory 🐾",
            font=("Arial", 10),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['text']
        ).pack(side=tk.BOTTOM, pady=10)

def main():
    root = tk.Tk()
    app = ArfArfSort(root)
    root.mainloop()

if __name__ == "__main__":
    main()
