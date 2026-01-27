import time
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, ttk
import threading

# --- SORTING ALGORITHMS ---

def bubble_sort(arr, update_callback=None):
    start_time = time.time()
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] < arr[j + 1]: # Descending
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
            
        # Update progress every N iterations (reduce callback overhead)
        if update_callback and i % max(1, n // 100) == 0:
            update_callback((i + 1) / n * 100)
            
        if not swapped:
            break
            
    if update_callback: update_callback(100)
    return arr, time.time() - start_time

def insertion_sort(arr, update_callback=None):
    start_time = time.time()
    n = len(arr)
    for i in range(1, n):
        key = arr[i]
        j = i - 1
        while j >= 0 and key > arr[j]: # Descending
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
        
        # Update progress every N iterations (reduce callback overhead)
        if update_callback and i % max(1, n // 100) == 0:
            update_callback((i + 1) / n * 100)
            
    if update_callback: update_callback(100)
    return arr, time.time() - start_time

def merge_sort_logic(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort_logic(arr[:mid])
    right = merge_sort_logic(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] > right[j]: # Descending
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def merge_sort_wrapper(arr, update_callback=None):
    start_time = time.time()
    if update_callback: update_callback(10) # Started
    sorted_arr = merge_sort_logic(arr)
    if update_callback: update_callback(100)
    return sorted_arr, time.time() - start_time

# --- DATA HANDLING ---

def read_dataset(filename="dataset.txt"):
    try:
        with open(filename, 'r') as f:
            return [int(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        return None

# --- GUI INTERFACE ---

class MilkFishGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MilkFish Sort - Premium Edition")
        self.root.state("zoomed")
        
        self.dataset_path = None
        self.current_data = []
        self.sorting = False
        self.sort_start_time = 0
        self.timer_id = None
        self.final_duration = 0.0

        tk.Label(root, text="MilkFish Sort System", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Main container for controls
        controls_frame = ttk.Frame(root)
        controls_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Import & reset controls
        self.btn_import = tk.Button(controls_frame, text="Import Dataset", width=25, command=self.import_dataset)
        self.btn_import.pack(pady=5)
        self.btn_reset = tk.Button(controls_frame, text="View Default Dataset", width=25, command=self.reset_to_default)
        self.btn_reset.pack(pady=5)

        # Sorting Buttons
        self.btn_bubble = tk.Button(controls_frame, text="Run Bubble Sort", width=25, command=lambda: self.run_sort("bubble"))
        self.btn_bubble.pack(pady=5)
        
        self.btn_insertion = tk.Button(controls_frame, text="Run Insertion Sort", width=25, command=lambda: self.run_sort("insertion"))
        self.btn_insertion.pack(pady=5)
        
        self.btn_merge = tk.Button(controls_frame, text="Run Merge Sort", width=25, command=lambda: self.run_sort("merge"))
        self.btn_merge.pack(pady=5)
        
        # Progress
        tk.Label(controls_frame, text="Progress:").pack(pady=(10,0))
        self.progress = ttk.Progressbar(controls_frame, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=5)
        
        # Timer
        tk.Label(controls_frame, text="Timer:", font=("Arial", 9, "bold")).pack(pady=(5,0))
        self.timer_label = tk.Label(controls_frame, text="0.000s", font=("Arial", 10), fg="green")
        self.timer_label.pack()

        # Output area
        tk.Label(controls_frame, text="Output:", font=("Arial", 9, "bold")).pack(pady=(5,0))
        self.output_area = scrolledtext.ScrolledText(controls_frame, width=60, height=12)
        self.output_area.pack(pady=3)
        
        # Report area (separate)
        tk.Label(controls_frame, text="Report:", font=("Arial", 9, "bold")).pack(pady=(3,0))
        self.report_area = scrolledtext.ScrolledText(controls_frame, width=60, height=6)
        self.report_area.pack(pady=3)
        
        # Load default dataset on startup
        self.load_default_dataset()

    def import_dataset(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            self._load_dataset_from_path(file_path, f"Loaded: {file_path}", show_alert=True)
    
    def load_default_dataset(self):
        self._load_dataset_from_path("dataset.txt", "Default Dataset")

    def reset_to_default(self):
        if self.sorting:
            messagebox.showwarning("Warning", "Finish the current sort before resetting.")
            return
        if self._load_dataset_from_path("dataset.txt", "Default Dataset", show_alert=True):
            self.progress['value'] = 0
            self.timer_label.config(text="0.000s")

    def _load_dataset_from_path(self, path, label, show_alert=False):
        data = read_dataset(path)
        if data:
            self.dataset_path = path
            self.current_data = data
            self._show_dataset(label, data)
            if show_alert:
                messagebox.showinfo("Success", f"{label} ready!")
            return True
        else:
            messagebox.showerror("Error", f"Could not read dataset from {path}!")
            return False

    def _show_dataset(self, label, data):
        self.output_area.delete(1.0, tk.END)
        contents = ", ".join(map(str, data))
        self.output_area.insert(tk.END, f"{label}\nSize: {len(data)}\nContents:\n{contents}\n" + "-"*30 + "\n")
        self.output_area.see(tk.END)

    def update_progress(self, percent):
        """Non-blocking progress update"""
        self.root.after(0, self._apply_progress, percent)

    def _apply_progress(self, percent):
        self.progress['value'] = percent
    
    def update_timer(self):
        """Real-time timer update independent of sorting progress"""
        if self.sorting:
            elapsed = time.time() - self.sort_start_time
            self.timer_label.config(text=f"{elapsed:.3f}s")
            self.timer_id = self.root.after(10, self.update_timer)  # Update every 10ms for smooth display

    def _stop_timer(self):
        """Stop the real-time timer"""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        actual_duration = time.time() - self.sort_start_time
        self.final_duration = actual_duration
        self.timer_label.config(text=f"{actual_duration:.3f}s")
        self.sorting = False

    def run_sort(self, sort_type):
        if self.sorting:
            messagebox.showwarning("Warning", "A sort is already in progress!")
            return
            
        if not self.dataset_path:
            messagebox.showerror("Error", "No dataset loaded!")
            return
        
        # START TIMER IMMEDIATELY - before anything else
        self.sorting = True
        self.sort_start_time = time.time()
        self.timer_id = self.root.after(10, self.update_timer)
        
        # Prepare data
        data = self.current_data.copy()
        algo_name = sort_type
        
        # Run sort in separate thread IMMEDIATELY - don't wait for UI updates
        sort_thread = threading.Thread(
            target=self._sort_in_thread,
            args=(sort_type, data.copy(), algo_name)
        )
        sort_thread.daemon = True
        sort_thread.start()
        
        # Do UI updates AFTER threading starts (non-blocking)
        self.root.after(0, self._update_ui_for_sort, algo_name)
    
    def _update_ui_for_sort(self, algo_name):
        """Deferred UI updates so they don't block timer"""
        self.final_duration = 0.0
        self.progress['value'] = 0
        self.timer_label.config(text="0.000s")
        self.report_area.delete(1.0, tk.END)
        self.output_area.delete(1.0, tk.END)
        preview = ", ".join(map(str, self.current_data))
        self.output_area.insert(tk.END, f"Dataset Snapshot:\n{preview}\n")
        self.output_area.insert(tk.END, f"\nRunning {algo_name}...\n")
        self.output_area.see(tk.END)
    
    def _sort_in_thread(self, sort_type, data, algo_name):
        finalize_args = None
        try:
            if sort_type == "bubble":
                sorted_data, duration = bubble_sort(data, self.update_progress)
            elif sort_type == "insertion":
                sorted_data, duration = insertion_sort(data, self.update_progress)
            elif sort_type == "merge":
                sorted_data, duration = merge_sort_wrapper(data, self.update_progress)
            else:
                sorted_data, duration = merge_sort_wrapper(data, self.update_progress)
            finalize_args = (algo_name, duration, sorted_data)
        except Exception as exc:
            self.root.after(0, lambda: messagebox.showerror("Error", str(exc)))
        finally:
            self.root.after(0, self._stop_timer)
            if finalize_args:
                self.root.after(0, self._update_report, *finalize_args)
    
    def _update_report(self, algo_name, duration, sorted_data):
        actual_duration = self.final_duration or (time.time() - self.sort_start_time)
        self.report_area.delete(1.0, tk.END)
        self.report_area.insert(tk.END, f"Algorithm: {algo_name.upper()}\n")
        self.report_area.insert(tk.END, f"Time: {actual_duration:.6f}s\n")
        self.report_area.insert(tk.END, f"Algo Timer: {duration:.6f}s\n")
        self.report_area.insert(tk.END, f"Size: {len(sorted_data)}\n")
        self.report_area.see(tk.END)
        
        self.output_area.insert(tk.END, f"\nSorted Result:\n")
        self.output_area.insert(tk.END, str(sorted_data) + "\n")
        self.output_area.see(tk.END)
        
        self.timer_label.config(text=f"{actual_duration:.3f}s")


# --- TERMINAL INTERFACE ---

def terminal_menu():
    while True:
        print("\n=== MilkFish Sort Terminal ===")
        print("1. Bubble Sort")
        print("2. Insertion Sort")
        print("3. Merge Sort")
        print("4. Launch GUI Mode")
        print("5. Exit")
        
        choice = input("Select an option: ")
        
        if choice == '5': break
        if choice == '4':
            root = tk.Tk()
            MilkFishGUI(root)
            root.mainloop()
            continue
            
        data = read_dataset()
        if data is None:
            print("Error: dataset.txt not found.")
            continue
            
        if choice == '1':
            res, t = bubble_sort(data.copy())
            name = "Bubble Sort"
        elif choice == '2':
            res, t = insertion_sort(data.copy())
            name = "Insertion Sort"
        elif choice == '3':
            res, t = merge_sort_wrapper(data.copy())
            name = "Merge Sort"
        else:
            print("Invalid choice.")
            continue
            
        print("\nSorted Data:")
        print(res)
        print("\nReport:")
        print(f"Algorithm: {name}")
        print(f"Time: {t:.6f} seconds")
        print(f"Dataset Size: {len(res)}")

if __name__ == "__main__":
    terminal_menu()
