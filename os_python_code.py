import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Module 2: Simulation Engine
class SimulationEngine:
    def __init__(self, disk_size=200):
        self.disk_size = disk_size
        self.seek_time_per_unit = 1  

    def fcfs(self, queue, head):
        sequence = [head] + queue
        total_movement = sum(abs(sequence[i] - sequence[i-1]) for i in range(1, len(sequence)))
        avg_seek_time = total_movement / len(queue) if queue else 0
        total_time = total_movement * self.seek_time_per_unit
        throughput = len(queue) / total_time if total_time > 0 else 0
        return sequence, total_movement, avg_seek_time, throughput

    def sstf(self, queue, head):
        sequence = [head]
        total_movement = 0
        remaining = queue.copy()
        current = head
        while remaining:
            closest = min(remaining, key=lambda x: abs(x - current))
            sequence.append(closest)
            total_movement += abs(current - closest)
            current = closest
            remaining.remove(closest)
        avg_seek_time = total_movement / len(queue) if queue else 0
        total_time = total_movement * self.seek_time_per_unit
        throughput = len(queue) / total_time if total_time > 0 else 0
        return sequence, total_movement, avg_seek_time, throughput

    def scan(self, queue, head, direction="right"):
        sequence = [head]
        total_movement = 0
        remaining = sorted(queue)
        current = head
        if direction == "right":
            right = [x for x in remaining if x >= current]
            left = [x for x in remaining if x < current]
            sequence.extend(right)
            if right:
                sequence.append(self.disk_size - 1)
            else:
                sequence.append(self.disk_size - 1)
            sequence.extend(reversed(left))
        else:
            left = [x for x in remaining if x <= current]
            right = [x for x in remaining if x > current]
            sequence.extend(reversed(left))
            if left:
                sequence.append(0)
            else:
                sequence.append(0)
            sequence.extend(right)
        # Calculate total movement from sequence
        total_movement = sum(abs(sequence[i] - sequence[i-1]) for i in range(1, len(sequence)))
        avg_seek_time = total_movement / len(queue) if queue else 0
        total_time = total_movement * self.seek_time_per_unit
        throughput = len(queue) / total_time if total_time > 0 else 0
        return sequence, total_movement, avg_seek_time, throughput

    def c_scan(self, queue, head, direction="right"):
        sequence = [head]
        total_movement = 0
        remaining = sorted(queue)
        current = head
        if direction == "right":
            right = [x for x in remaining if x >= current]
            left = [x for x in remaining if x < current]
            sequence.extend(right)
            if right or not left:  # Include disk end unless only left requests
                sequence.append(self.disk_size - 1)
            sequence.append(0)
            sequence.extend(left)
        else:
            left = [x for x in remaining if x <= current]
            right = [x for x in remaining if x > current]
            sequence.extend(reversed(left))
            if left or not right:  # Include disk start unless only right requests
                sequence.append(0)
            sequence.append(self.disk_size - 1)
            sequence.extend(reversed(right))
        # Calculate total movement from sequence
        total_movement = sum(abs(sequence[i] - sequence[i-1]) for i in range(1, len(sequence)))
        avg_seek_time = total_movement / len(queue) if queue else 0
        total_time = total_movement * self.seek_time_per_unit
        throughput = len(queue) / total_time if total_time > 0 else 0
        return sequence, total_movement, avg_seek_time, throughput

# Module 3: Data Visualization
class DataVisualization:
    def __init__(self, figure):
        self.figure = figure
        self.ax = None

    def plot_head_movement(self, results):
        """Plot line chart for head movement (steps) across algorithms."""
        if self.ax is None:
            self.ax = self.figure.add_subplot(111)
        self.ax.clear()
        for algo, (sequence, _, _, _) in results.items():
            self.ax.plot(range(len(sequence)), sequence, marker='o', label=algo)
        self.ax.set_title("Disk Head Movement (Steps)")
        self.ax.set_xlabel("Step")
        self.ax.set_ylabel("Cylinder")
        self.ax.grid(True)
        self.ax.legend()

    def plot_avg_seek_time(self, results):
        """Plot bar chart for average seek time across algorithms."""
        if self.ax is None:
            self.ax = self.figure.add_subplot(111)
        self.ax.clear()
        algos = list(results.keys())
        seek_times = [results[algo][2] for algo in algos]
        self.ax.bar(algos, seek_times, color='skyblue')
        self.ax.set_title("Average Seek Time")
        self.ax.set_xlabel("Algorithm")
        self.ax.set_ylabel("Avg Seek Time (units)")
        self.ax.grid(True, axis='y')

    def plot_throughput(self, results):
        """Plot bar chart for system throughput across algorithms."""
        if self.ax is None:
            self.ax = self.figure.add_subplot(111)
        self.ax.clear()
        algos = list(results.keys())
        throughputs = [results[algo][3] for algo in algos]
        self.ax.bar(algos, throughputs, color='lightgreen')
        self.ax.set_title("System Throughput")
        self.ax.set_xlabel("Algorithm")
        self.ax.set_ylabel("Requests per ms")
        self.ax.grid(True, axis='y')

# Module 1: Graphical User Interface
class SimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Disk Scheduling Simulator")
        self.sim_engine = SimulationEngine()
        self.figure = plt.figure(figsize=(6, 4))
        self.vis = DataVisualization(self.figure)

        # GUI Layout
        tk.Label(root, text="Disk Queue (e.g., 82,170,43):").pack(pady=5)
        self.queue_entry = tk.Entry(root, width=50)
        self.queue_entry.pack()

        tk.Label(root, text="Initial Head Position (0-199):").pack(pady=5)
        self.head_entry = tk.Entry(root, width=10)
        self.head_entry.pack()

        tk.Label(root, text="Disk Size (default 200):").pack(pady=5)
        self.disk_size_entry = tk.Entry(root, width=10)
        self.disk_size_entry.insert(0, "200")
        self.disk_size_entry.pack()

        tk.Label(root, text="Select Algorithms:").pack(pady=5)
        self.algorithms = {
            "FCFS": tk.BooleanVar(),
            "SSTF": tk.BooleanVar(),
            "SCAN": tk.BooleanVar(),
            "C-SCAN": tk.BooleanVar()
        }
        for algo, var in self.algorithms.items():
            tk.Checkbutton(root, text=algo, variable=var).pack(anchor="w")

        tk.Label(root, text="Direction (SCAN/C-SCAN):").pack(pady=5)
        self.direction = tk.StringVar(value="right")
        tk.Radiobutton(root, text="Right", variable=self.direction, value="right").pack(anchor="w")
        tk.Radiobutton(root, text="Left", variable=self.direction, value="left").pack(anchor="w")

        tk.Label(root, text="Select Visualization:").pack(pady=5)
        self.vis_type = tk.StringVar(value="steps")
        self.vis_checkboxes = {
            "Steps": tk.BooleanVar(),
            "Average Seek Time": tk.BooleanVar(),
            "Throughput": tk.BooleanVar()
        }
        def update_vis_selection(selected):
            # Ensure only one checkbox is selected
            for vis, var in self.vis_checkboxes.items():
                if vis != selected:
                    var.set(False)
            self.vis_type.set(selected.lower().replace(" ", "_"))

        for vis, var in self.vis_checkboxes.items():
            tk.Checkbutton(
                root, text=vis, variable=var,
                command=lambda v=vis: update_vis_selection(v)
            ).pack(anchor="w")

        tk.Button(root, text="Run Simulation", command=self.run_simulation).pack(pady=10)

        # Result Display
        self.result_text = tk.Text(root, height=10, width=50)
        self.result_text.pack(pady=5)

        # Visualization Canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack(pady=10)

    def run_simulation(self):
        try:
            # Parse inputs
            queue = [int(x.strip()) for x in self.queue_entry.get().split(",")]
            head = int(self.head_entry.get())
            disk_size = int(self.disk_size_entry.get())

            if not (0 <= head < disk_size) or any(x < 0 or x >= disk_size for x in queue):
                messagebox.showerror("Error", f"Head and queue must be between 0 and {disk_size-1}.")
                return

            selected_algorithms = [algo for algo, var in self.algorithms.items() if var.get()]
            if not selected_algorithms:
                messagebox.showerror("Error", "Please select at least one algorithm.")
                return

            # Check if a visualization is selected
            if not any(var.get() for var in self.vis_checkboxes.values()):
                messagebox.showerror("Error", "Please select a visualization type.")
                return

            # Update simulation engine disk size
            self.sim_engine.disk_size = disk_size

            # Run simulations
            results = {}
            for algo in selected_algorithms:
                if algo == "FCFS":
                    sequence, total_movement, avg_seek_time, throughput = self.sim_engine.fcfs(queue, head)
                elif algo == "SSTF":
                    sequence, total_movement, avg_seek_time, throughput = self.sim_engine.sstf(queue, head)
                elif algo == "SCAN":
                    sequence, total_movement, avg_seek_time, throughput = self.sim_engine.scan(queue, head, self.direction.get())
                elif algo == "C-SCAN":
                    sequence, total_movement, avg_seek_time, throughput = self.sim_engine.c_scan(queue, head, self.direction.get())
                results[algo] = (sequence, total_movement, avg_seek_time, throughput)

            # Display results
            self.result_text.delete(1.0, tk.END)
            for algo, (sequence, total_movement, avg_seek_time, throughput) in results.items():
                self.result_text.insert(tk.END, f"{algo}:\n")
                self.result_text.insert(tk.END, f"  Sequence: {sequence}\n")
                self.result_text.insert(tk.END, f"  Total Head Movement: {total_movement}\n")
                self.result_text.insert(tk.END, f"  Avg Seek Time: {avg_seek_time:.2f} units\n")
                self.result_text.insert(tk.END, f"  Throughput: {throughput:.2f} requests/ms\n\n")

            # Generate visualization
            vis_type = self.vis_type.get()
            if vis_type == "steps":
                self.vis.plot_head_movement(results)
            elif vis_type == "average_seek_time":
                self.vis.plot_avg_seek_time(results)
            elif vis_type == "throughput":
                self.vis.plot_throughput(results)
            self.canvas.draw()

        except ValueError:
            messagebox.showerror("Error", "Invalid input! Ensure queue, head, and disk size are valid numbers.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimulatorGUI(root)
    root.mainloop()
