import time
import tkinter as tk
from tkinter import messagebox, scrolledtext

# --- SORTING ALGORITHMS ---

def bubble_sort(arr):
    start_time = time.time()
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] < arr[j + 1]: # Descending
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr, time.time() - start_time

def insertion_sort(arr):
    start_time = time.time()
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and key > arr[j]: # Descending
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
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

def merge_sort_wrapper(arr):
    start_time = time.time()
    sorted_arr = merge_sort_logic(arr)
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
        self.root.geometry("500x500")
        
        tk.Label(root, text="MilkFish Sort System", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.btn_bubble = tk.Button(root, text="Run Bubble Sort", width=25, command=lambda: self.run_sort("bubble"))
        self.btn_bubble.pack(pady=5)
        
        self.btn_insertion = tk.Button(root, text="Run Insertion Sort", width=25, command=lambda: self.run_sort("insertion"))
        self.btn_insertion.pack(pady=5)
        
        self.btn_merge = tk.Button(root, text="Run Merge Sort", width=25, command=lambda: self.run_sort("merge"))
        self.btn_merge.pack(pady=5)
        
        self.output_area = scrolledtext.ScrolledText(root, width=55, height=15)
        self.output_area.pack(pady=10)

    def run_sort(self, sort_type):
        data = read_dataset()
        if data is None:
            messagebox.showerror("Error", "dataset.txt not found!")
            return
        
        if sort_type == "bubble":
            sorted_data, duration = bubble_sort(data.copy())
        elif sort_type == "insertion":
            sorted_data, duration = insertion_sort(data.copy())
        else:
            sorted_data, duration = merge_sort_wrapper(data.copy())
            
        self.output_area.delete(1.0, tk.END)
        self.output_area.insert(tk.END, f"Algorithm: {sort_type.upper()}\n")
        self.output_area.insert(tk.END, f"Time Spent: {duration:.6f} seconds\n")
        self.output_area.insert(tk.END, "-"*30 + "\n")
        self.output_area.insert(tk.END, str(sorted_data))

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
            
        print(f"Sorted Data: {res}")
        print(f"\n{name} Results:")
        print(f"Time: {t:.6f} seconds")

if __name__ == "__main__":
    terminal_menu()