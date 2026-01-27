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
import glob

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
    def bubble_sort(arr: List,
                    timer_cb: Optional[Callable] = None,
                    stop_cb: Optional[Callable] = None,
                    progress_cb: Optional[Callable[[int, int], None]] = None,
                    reverse: bool = False) -> List:
        """Bubble Sort - O(n^2)
        reverse: False -> ascending, True -> descending
        """
        n = len(arr)
        arr_copy = arr.copy()
        start_time = time.time()

        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                if (not reverse and arr_copy[j] > arr_copy[j + 1]) or (reverse and arr_copy[j] < arr_copy[j + 1]):
                    arr_copy[j], arr_copy[j + 1] = arr_copy[j + 1], arr_copy[j]
                    swapped = True

            if progress_cb:
                try:
                    progress_cb(i + 1, n)
                except Exception:
                    pass

            if not swapped:
                break

            if stop_cb and stop_cb():
                return arr_copy

            if timer_cb:
                timer_cb(time.time() - start_time)

        return arr_copy

    @staticmethod
    def insertion_sort(arr: List,
                       timer_cb: Optional[Callable] = None,
                       stop_cb: Optional[Callable] = None,
                       progress_cb: Optional[Callable[[int, int], None]] = None,
                       reverse: bool = False) -> List:
        """Insertion Sort - O(n^2)"""
        arr_copy = arr.copy()
        n = len(arr_copy)
        start_time = time.time()

        for i in range(1, n):
            key = arr_copy[i]
            j = i - 1

            if not reverse:
                while j >= 0 and arr_copy[j] > key:
                    arr_copy[j + 1] = arr_copy[j]
                    j -= 1
            else:
                while j >= 0 and arr_copy[j] < key:
                    arr_copy[j + 1] = arr_copy[j]
                    j -= 1

            arr_copy[j + 1] = key

            if progress_cb:
                try:
                    progress_cb(i, n)
                except Exception:
                    pass

            if stop_cb and stop_cb():
                return arr_copy

            if timer_cb:
                timer_cb(time.time() - start_time)

        return arr_copy

    @staticmethod
    def merge_sort(arr: List,
                   timer_cb: Optional[Callable] = None,
                   stop_cb: Optional[Callable] = None,
                   progress_cb: Optional[Callable[[int, int], None]] = None,
                   reverse: bool = False) -> List:
        """Merge Sort - O(n log n)"""
        if len(arr) <= 1:
            return arr.copy()

        start_time = time.time()

        def merge(left: List, right: List) -> List:
            result = []
            i = j = 0
            while i < len(left) and j < len(right):
                if (not reverse and left[i] <= right[j]) or (reverse and left[i] >= right[j]):
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1
            result.extend(left[i:])
            result.extend(right[j:])
            return result

        # optional simple progress heuristic: count merges completed vs. total (not exact)
        merge_counter = {'count': 0, 'total': max(1, len(arr).bit_length() * len(arr))}

        def merge_sort_recursive(arr_local: List) -> List:
            if len(arr_local) <= 1:
                return arr_local

            if stop_cb and stop_cb():
                return arr_local

            mid = len(arr_local) // 2
            left = merge_sort_recursive(arr_local[:mid])
            right = merge_sort_recursive(arr_local[mid:])
            result = merge(left, right)

            # progress callback (best-effort)
            merge_counter['count'] += 1
            if progress_cb:
                try:
                    progress_cb(merge_counter['count'], merge_counter['total'])
                except Exception:
                    pass

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
        self.show_progress = tk.BooleanVar(value=False)
        self.is_sorting = False
        self.show_first_10 = tk.BooleanVar(value=True)
        self.available_datasets = []  # (path, filename, count)
        self.order_var = tk.StringVar(value="asc")  # 'asc' or 'desc'
        self.setup_ui()
        self.update_timer_visibility()
        self.update_progress_visibility()
        self.auto_load_data_folder()
        # overlay helper
        self._loading_overlay = None

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
        control_frame.pack(pady=10, padx=20, fill=tk.X)

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

        # Dataset combobox (auto-loaded)
        tk.Label(
            left,
            text="📂 Auto-loaded datasets:",
            font=("Arial", 9),
            bg=DOG_COLORS['bg'],
            fg=DOG_COLORS['dark']
        ).grid(row=1, column=0, padx=5, pady=3, sticky=tk.W)

        self.dataset_choice = tk.StringVar()
        self.dataset_combo = ttk.Combobox(left, textvariable=self.dataset_choice, state="readonly", width=30)
        self.dataset_combo.grid(row=1, column=1, padx=5, pady=3, sticky=tk.W)

        tk.Button(
            left,
            text="🔄 Load Selected",
            font=("Arial", 9),
            bg=DOG_COLORS['secondary'],
            fg="white",
            command=self.load_selected_dataset,
            cursor="hand2"
        ).grid(row=1, column=2, padx=5)

        btn_frame = tk.Frame(left, bg=DOG_COLORS['bg'])
        btn_frame.grid(row=2, column=0, columnspan=3, pady=5)

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
            text="🐾 Show Progress Bar (performance impact)",
            variable=self.show_progress,
            bg=DOG_COLORS['bg'],
            font=("Arial", 9),
            command=self.update_progress_visibility
        ).pack()

        tk.Checkbutton(
            middle,
            text="🐾 Show first 10 only",
            variable=self.show_first_10,
            bg=DOG_COLORS['bg'],
            font=("Arial", 9)
        ).pack()

        # Order selection (Ascending / Descending)
        order_frame = tk.Frame(middle, bg=DOG_COLORS['bg'])
        order_frame.pack(pady=4)
        tk.Label(order_frame, text="Order:", font=("Arial", 9, "bold"), bg=DOG_COLORS['bg']).pack(side=tk.LEFT, padx=(0,6))
        tk.Radiobutton(order_frame, text="Ascending", variable=self.order_var, value="asc", bg=DOG_COLORS['bg']).pack(side=tk.LEFT)
        tk.Radiobutton(order_frame, text="Descending", variable=self.order_var, value="desc", bg=DOG_COLORS['bg']).pack(side=tk.LEFT)

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

        # Timer & Progress
        timer_frame = tk.Frame(self.frame, bg=DOG_COLORS['bg'])
        timer_frame.pack(padx=20, fill=tk.X)

        self.timer_label = tk.Label(timer_frame, text="⏱️ 0.0000s",
                                   bg=DOG_COLORS['bg'], fg=DOG_COLORS['danger'],
                                   font=("Arial", 11, "bold"))
        self.timer_label.pack(anchor=tk.W)

        self.progress = ttk.Progressbar(timer_frame, orient='horizontal', mode='determinate', length=600)

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
            font=("Courier", 9),
            bg="white"
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

        # Status bar
        self.status_var = tk.StringVar(value="Ready! 🐕")
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
        if self.show_timer.get():
            self.timer_label.pack(anchor=tk.W)
        else:
            self.timer_label.pack_forget()

    def update_progress_visibility(self):
        if self.show_progress.get():
            self.progress.pack(anchor=tk.W, pady=(5,2))
        else:
            self.progress.pack_forget()
            self.progress['value'] = 0

    def auto_load_data_folder(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        except Exception:
            base_dir = os.getcwd()
        data_dir = os.path.normpath(os.path.join(base_dir, '..', 'data'))
        self.results_text.insert("1.0", f"Looking for datasets in: {data_dir}\n")

        if not os.path.isdir(data_dir):
            self.results_text.insert(tk.END, "No data folder found (expected ../data). Create a data folder and put .txt files there.\n")
            return

        found_files = glob.glob(os.path.join(data_dir, '*.txt'))
        valid_files = []
        invalid_files = []

        for path in found_files:
            filename = os.path.basename(path)
            try:
                nums = []
                with open(path, 'r', encoding='utf-8') as f:
                    for ln, line in enumerate(f, start=1):
                        stripped = line.strip()
                        if not stripped:
                            continue
                        try:
                            nums.append(int(stripped))
                        except ValueError:
                            raise ValueError(f"Non-integer on line {ln} in {filename}")
                if len(nums) == 0:
                    raise ValueError(f"No numeric data found in {filename}")
                valid_files.append((path, filename, len(nums)))
            except Exception as e:
                invalid_files.append((filename, str(e)))

        if valid_files:
            self.available_datasets = valid_files
            names = [f"{fn} ({count} lines)" for (_, fn, count) in valid_files]
            self.dataset_combo['values'] = names
            self.dataset_combo.current(0)
            first_path, first_name, first_count = valid_files[0]
            self.load_dataset_from_path(first_path, first_name, first_count, auto=True)
        else:
            self.dataset_combo['values'] = []
            self.results_text.insert(tk.END, "No valid .txt datasets found in data folder.\n")

        if invalid_files:
            self.results_text.insert(tk.END, "\nFiles with issues:\n")
            for fn, reason in invalid_files:
                self.results_text.insert(tk.END, f"- {fn}: {reason}\n")

    def load_selected_dataset(self):
        idx = self.dataset_combo.current()
        if idx < 0 or idx >= len(self.available_datasets):
            messagebox.showwarning("No selection", "Please choose a dataset from the auto-loaded list.")
            return
        path, filename, count = self.available_datasets[idx]
        self.load_dataset_from_path(path, filename, count)

    def load_dataset_from_path(self, path, filename, count, auto=False):
        try:
            nums = []
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    nums.append(int(stripped))
            self.dataset = nums
            self.size_var.set(str(len(self.dataset)))
            self.results_text.insert(tk.END, f"\n📂 Loaded {filename} with {len(self.dataset)} numbers from data folder.\n")
            self.status_var.set(f"Loaded {filename}")
            if auto:
                self.results_text.insert(tk.END, "Auto-loaded first valid dataset.\n")
        except Exception as e:
            messagebox.showerror("Load failed", f"Failed to load {filename}: {e}")

    def import_dataset(self):
        path = filedialog.askopenfilename(
            title="Import Dataset",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not path:
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.dataset = [int(line.strip()) for line in f if line.strip()]

            self.size_var.set(str(len(self.dataset)))
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", f"🐾 Imported {len(self.dataset)} numbers\n")

            messagebox.showinfo("Success! 🐕", f"Loaded {len(self.dataset)} numbers")

        except Exception as e:
            messagebox.showerror("Error! 😿", str(e))

    def generate_dataset(self):
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

    def run_algorithm(self, algorithm_name: str, dataset: List,
                      progress_cb: Optional[Callable[[int,int],None]] = None,
                      reverse: bool = False) -> Tuple[List, float]:
        """Run a specific sorting algorithm with reverse support"""
        start_time = time.time()
        if algorithm_name == "Bubble Sort":
            sorted_array = SortingAlgorithms.bubble_sort(
                dataset,
                timer_cb=self.update_timer if self.show_timer.get() else None,
                stop_cb=lambda: not self.is_sorting,
                progress_cb=progress_cb,
                reverse=reverse
            )
        elif algorithm_name == "Insertion Sort":
            sorted_array = SortingAlgorithms.insertion_sort(
                dataset,
                timer_cb=self.update_timer if self.show_timer.get() else None,
                stop_cb=lambda: not self.is_sorting,
                progress_cb=progress_cb,
                reverse=reverse
            )
        else:
            sorted_array = SortingAlgorithms.merge_sort(
                dataset,
                timer_cb=self.update_timer if self.show_timer.get() else None,
                stop_cb=lambda: not self.is_sorting,
                progress_cb=progress_cb,
                reverse=reverse
            )

        execution_time = time.time() - start_time
        return sorted_array, execution_time

    # ---------- Loading overlay & chunked render helpers ----------
    def show_loading_overlay(self, message="Rendering results... Please wait"):
        if self._loading_overlay:
            return
        overlay = tk.Toplevel(self.frame)
        overlay.transient(self.frame)
        overlay.grab_set()
        overlay.title("")  # no title
        overlay.geometry("+%d+%d" % (self.frame.winfo_rootx() + 40, self.frame.winfo_rooty() + 40))
        overlay.configure(bg="white")
        overlay.resizable(False, False)
        tk.Label(overlay, text=message, bg="white", font=("Arial", 10)).pack(padx=20, pady=(10,5))
        pb = ttk.Progressbar(overlay, mode='indeterminate', length=240)
        pb.pack(padx=20, pady=(0,10))
        pb.start(10)
        # store references
        self._loading_overlay = (overlay, pb)

    def hide_loading_overlay(self):
        if not self._loading_overlay:
            return
        overlay, pb = self._loading_overlay
        try:
            pb.stop()
            overlay.grab_release()
            overlay.destroy()
        except Exception:
            pass
        self._loading_overlay = None

    def render_lines_chunked(self, lines: List[str], chunk_size: int = 200, on_complete: Optional[Callable] = None):
        """Insert lines into the results_text in small chunks so the UI remains responsive."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        total = len(lines)
        idx = 0

        def _insert_chunk():
            nonlocal idx
            end = min(idx + chunk_size, total)
            # join chunk into a single insert call
            chunk_text = "".join(lines[idx:end])
            try:
                self.results_text.insert(tk.END, chunk_text)
            except Exception:
                pass
            idx = end
            # update visible UI
            try:
                self.results_text.see(tk.END)
            except Exception:
                pass
            if idx < total:
                # schedule next chunk
                self.frame.after(5, _insert_chunk)
            else:
                # done
                if on_complete:
                    on_complete()

        # start chunked insertion
        self.frame.after(1, _insert_chunk)

    # ---------- Run single algorithm ----------
    def run_single(self):
        if not self.dataset:
            messagebox.showwarning("No Data! 🐕", "Import or generate dataset first!")
            return

        if self.is_sorting:
            messagebox.showwarning("Busy! 🐕", "Already sorting!")
            return

        self.is_sorting = True
        algorithm = self.algorithm_var.get()
        reverse_flag = True if self.order_var.get() == 'desc' else False

        self.timer_label.config(text="⏱️ 0.0000s")
        self.stop_button_single.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", f"🐕 Running {algorithm} ({'Descending' if reverse_flag else 'Ascending'})...\n\n")
        self.frame.update()

        def sort_thread():
            try:
                # prepare progress callback
                def progress_cb_local(current, total):
                    def _update():
                        try:
                            self.progress['maximum'] = total
                            self.progress['value'] = current
                            self.status_var.set(f"Sorting {algorithm}... {current}/{total}")
                        except Exception:
                            pass
                    self.frame.after(0, _update)

                progress_cb = progress_cb_local if self.show_progress.get() else None

                sorted_array, exec_time = self.run_algorithm(algorithm, self.dataset, progress_cb=progress_cb, reverse=reverse_flag)
                self.sorted_arrays = {algorithm: sorted_array}

                # prepare output lines first (so timing is taken when sort finished)
                is_sorted = all(
                    (sorted_array[i] >= sorted_array[i+1]) if reverse_flag else (sorted_array[i] <= sorted_array[i+1])
                    for i in range(len(sorted_array)-1)
                )

                order_text = "Descending" if reverse_flag else "Ascending"
                lines = []
                lines.append("="*70 + "\n")
                lines.append(f"🦴 {algorithm.upper()} RESULTS ({order_text}) 🦴\n")
                lines.append("="*70 + "\n\n")
                lines.append(f"Size: {len(self.dataset)}\n")
                lines.append(f"Time: {exec_time:.4f}s ({exec_time*1000:.2f}ms)\n")
                lines.append(f"Status: {'✅ SORTED' if is_sorted else '❌ ERROR'}\n\n")
                header = "FIRST 10 SORTED RECORDS" if self.show_first_10.get() else f"COMPLETE SORTED ARRAY ({len(sorted_array)} elements)"
                lines.append("="*70 + "\n")
                lines.append(f"{header}\n")
                lines.append("="*70 + "\n")
                display_array = sorted_array[:10] if self.show_first_10.get() else sorted_array
                for num in display_array:
                    lines.append(f"{num}\n")
                lines.append("\n" + "="*70 + "\n")
                lines.append("🐾 Complete! 🐾\n" + "="*70 + "\n")

                # Show loading overlay and render chunked
                self.show_loading_overlay("Rendering results...")

                def on_render_done():
                    # hide overlay, finalize UI and show the final completion message
                    self.hide_loading_overlay()
                    self.timer_label.config(text=f"⏱️ {exec_time:.4f}s")
                    if self.show_progress.get():
                        try:
                            self.progress.config(value=self.progress['maximum'])
                        except Exception:
                            pass
                    self.status_var.set("--")
                    messagebox.showinfo("Done! 🐕", f"{algorithm} completed in {exec_time:.4f}s")
                    # finalize state
                    self.is_sorting = False
                    self.stop_button_single.config(state=tk.DISABLED)
                    try:
                        self.frame.after(300, lambda: self.progress.config(value=0))
                    except Exception:
                        pass

                # render
                self.frame.after(1, lambda: self.render_lines_chunked(lines, chunk_size=200, on_complete=on_render_done))

            except Exception as e:
                self.hide_loading_overlay()
                messagebox.showerror("Error! 😿", str(e))
                self.is_sorting = False
                self.stop_button_single.config(state=tk.DISABLED)
                try:
                    self.frame.after(300, lambda: self.progress.config(value=0))
                except Exception:
                    pass

        threading.Thread(target=sort_thread, daemon=True).start()

    def stop_sort(self):
        if self.is_sorting:
            self.is_sorting = False
            self.stop_button_single.config(state=tk.DISABLED)
            self.results_text.insert(tk.END, "\n⏹️ Sorting stopped by user!\n")
            self.status_var.set("Sorting stopped by user! ⏹️")
            messagebox.showinfo("Stopped! 🐕", "Sorting operation has been stopped!")
            try:
                self.progress['value'] = 0
            except Exception:
                pass
            # hide overlay if any
            self.hide_loading_overlay()

    def run_all(self):
        if not self.dataset:
            messagebox.showwarning("No Data! 🐕", "Import or generate dataset first!")
            return

        if self.is_sorting:
            messagebox.showwarning("Busy! 🐕", "Already sorting!")
            return

        self.is_sorting = True
        reverse_flag = True if self.order_var.get() == 'desc' else False

        self.timer_label.config(text="⏱️ 0.0000s")
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", f"🐕 Comparing all algorithms ({'Descending' if reverse_flag else 'Ascending'})...\n\n")
        self.frame.update()

        def compare_thread():
            try:
                algorithms = ["Bubble Sort", "Insertion Sort", "Merge Sort"]
                results = {}
                self.sorted_arrays = {}

                for algo in algorithms:
                    self.results_text.insert(tk.END, f"Running {algo}...\n")
                    self.frame.update()

                    def progress_cb_local(current, total, _algo=algo):
                        def _update():
                            try:
                                self.progress['maximum'] = total
                                self.progress['value'] = current
                                self.status_var.set(f"Sorting {_algo}... {current}/{total}")
                            except Exception:
                                pass
                        self.frame.after(0, _update)

                    progress_cb = progress_cb_local if (self.show_progress.get() and algo in ("Bubble Sort", "Insertion Sort", "Merge Sort")) else None

                    sorted_array, exec_time = self.run_algorithm(algo, self.dataset, progress_cb=progress_cb, reverse=reverse_flag)
                    results[algo] = exec_time
                    self.sorted_arrays[algo] = sorted_array

                    if self.show_progress.get():
                        try:
                            self.frame.after(0, lambda: self.progress.config(value=0))
                        except Exception:
                            pass

                # prepare comparative output lines (do not insert directly)
                lines = []
                lines.append("\n\n" + "="*70 + "\n")
                lines.append("🦴 COMPARATIVE ANALYSIS 🦴\n")
                lines.append("="*70 + "\n\n")
                lines.append(f"Dataset Size: {len(self.dataset)} elements\n\n")
                lines.append(f"{'Algorithm':<20} {'Time (sec)':<15} {'Time (ms)':<15} {'Complexity'}\n")
                lines.append("-"*70 + "\n")
                complexities = {
                    "Bubble Sort": "O(n²)",
                    "Insertion Sort": "O(n²)",
                    "Merge Sort": "O(n log n)"
                }
                for algo in algorithms:
                    time_sec = results[algo]
                    time_ms = time_sec * 1000
                    complexity = complexities[algo]
                    lines.append(f"{algo:<20} {time_sec:<15.4f} {time_ms:<15.2f} {complexity}\n")

                fastest = min(results, key=results.get)
                lines.append(f"\n🏆 Fastest: {fastest} ({results[fastest]:.4f}s)\n")
                if results["Bubble Sort"] > 0 and results["Merge Sort"] > 0:
                    ratio = results["Bubble Sort"] / results["Merge Sort"]
                    lines.append(f"📊 Merge Sort is {ratio:.2f}x faster than Bubble Sort!\n")

                if self.show_first_10.get():
                    lines.append("\n\n" + "="*70 + "\nFIRST 10 RECORDS FROM EACH ALGORITHM\n" + "="*70 + "\n\n")
                    for algo in algorithms:
                        lines.append(f"{algo}:\n")
                        for num in self.sorted_arrays[algo][:10]:
                            lines.append(f"{num}\n")
                        lines.append("\n")

                lines.append("\n🐾 All done! Good dogs! 🐾\n")

                # show overlay and render chunked
                self.show_loading_overlay("Rendering comparison results...")

                def on_render_done():
                    self.hide_loading_overlay()
                    if self.show_progress.get():
                        try:
                            self.progress.config(value=self.progress['maximum'])
                        except Exception:
                            pass
                    self.status_var.set("All algorithms completed! ✅")
                    messagebox.showinfo("Success! 🐕", "All algorithms completed!")
                    self.is_sorting = False
                    try:
                        self.frame.after(300, lambda: self.progress.config(value=0))
                    except Exception:
                        pass

                self.frame.after(1, lambda: self.render_lines_chunked(lines, chunk_size=200, on_complete=on_render_done))

            except Exception as e:
                self.hide_loading_overlay()
                messagebox.showerror("Error! 😿", str(e))
                self.is_sorting = False
                try:
                    self.frame.after(300, lambda: self.progress.config(value=0))
                except Exception:
                    pass

        threading.Thread(target=compare_thread, daemon=True).start()

    def export_report(self):
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
        self.root.title("🐕 ArfArf Sort - Prelim Lab Work 2 🦴")
        self.root.geometry("950x825")
        self.root.configure(bg=DOG_COLORS['bg'])
        self.root.resizable(False, False)

        self.main_container = tk.Frame(root, bg=DOG_COLORS['bg'])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.show_lab2()

    def clear_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_lab2(self):
        self.clear_container()
        lab_frame = tk.Frame(self.main_container, bg=DOG_COLORS['bg'])
        lab_frame.pack(fill=tk.BOTH, expand=True)
        PrelimLab2(lab_frame)
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
