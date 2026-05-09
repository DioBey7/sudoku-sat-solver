import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import threading
import os

from sat_solving import SudokuSolverApp

class SudokuGUI:
    """
    Main GUI class for the Sudoku SAT Solver project.
    Handles user interaction, image loading, and solution visualization.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku SAT Solver - Project Assignment")
        self.root.geometry("1100x750")
        self.root.resizable(False, False)

        # UI Styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Initialize the Backend Solver (Manages Logic & API)
        self.app_backend = SudokuSolverApp()
        self.app_backend.initialize()

        # State Variables
        self.current_image_path = None
        self.solution_index = 0
        self.solutions = []
        
        # --- BUILD UI ---
        self.create_widgets()

    def create_widgets(self):
        """Creates and arranges all GUI components."""
        
        # 1. Header Section
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill="x")
        
        title_label = tk.Label(header_frame, text="Sudoku Solver (SAT Encoding)", 
                               font=("Helvetica", 24, "bold"), bg="#2c3e50", fg="white")
        title_label.pack(pady=20)

        # 2. Control Panel (Buttons & Status)
        control_frame = tk.Frame(self.root, bg="#ecf0f1", pady=10)
        control_frame.pack(fill="x")

        # Load Button
        self.btn_load = tk.Button(control_frame, text="📁 Load Image", command=self.load_image,
                                  font=("Arial", 12), bg="#3498db", fg="white", width=15)
        self.btn_load.pack(side="left", padx=20)

        # Solve Button
        self.btn_solve = tk.Button(control_frame, text="⚙️ Solve", command=self.start_solving_thread,
                                   font=("Arial", 12), bg="#27ae60", fg="white", width=15, state="disabled")
        self.btn_solve.pack(side="left", padx=10)

        # Status Label
        self.lbl_status = tk.Label(control_frame, text="Ready", font=("Arial", 12, "italic"), bg="#ecf0f1", fg="#7f8c8d")
        self.lbl_status.pack(side="left", padx=20)

        # Solution Navigation (Previous/Next) - Hidden initially
        self.nav_frame = tk.Frame(control_frame, bg="#ecf0f1")
        self.btn_prev = tk.Button(self.nav_frame, text="< Previous", command=self.prev_solution, state="disabled")
        self.btn_prev.pack(side="left", padx=5)
        
        self.lbl_sol_count = tk.Label(self.nav_frame, text="0 / 0", bg="#ecf0f1")
        self.lbl_sol_count.pack(side="left", padx=5)
        
        self.btn_next = tk.Button(self.nav_frame, text="Next >", command=self.next_solution, state="disabled")
        self.btn_next.pack(side="left", padx=5)
        
        # 3. Main Content Area (Grids)
        main_content = tk.Frame(self.root, padx=20, pady=20)
        main_content.pack(expand=True, fill="both")

        # Left Panel: Input Image
        left_frame = tk.LabelFrame(main_content, text="Input (Image / Detected)", font=("Arial", 12, "bold"))
        left_frame.pack(side="left", expand=True, fill="both", padx=10)
        
        self.canvas_input = tk.Canvas(left_frame, width=400, height=400, bg="#bdc3c7")
        self.canvas_input.pack(pady=20)

        # Right Panel: Output Grid
        right_frame = tk.LabelFrame(main_content, text="SAT Solution", font=("Arial", 12, "bold"))
        right_frame.pack(side="right", expand=True, fill="both", padx=10)

        self.canvas_output = tk.Canvas(right_frame, width=400, height=400, bg="white")
        self.canvas_output.pack(pady=20)
        
        # Initialize with empty grid
        self.draw_empty_grid(self.canvas_output)

    def draw_empty_grid(self, canvas):
        """Draws the lines for an empty 9x9 Sudoku grid."""
        canvas.delete("all")
        w = 400
        step = w / 9
        
        for i in range(10):
            line_width = 3 if i % 3 == 0 else 1
            # Vertical lines
            canvas.create_line(i * step, 0, i * step, w, width=line_width)
            # Horizontal lines
            canvas.create_line(0, i * step, w, i * step, width=line_width)

    def draw_sudoku_grid(self, canvas, matrix, is_original=False):
        """Renders the Sudoku matrix onto the canvas."""
        self.draw_empty_grid(canvas)
        w = 400
        step = w / 9
        
        if not matrix:
            return

        for r in range(9):
            for c in range(9):
                val = matrix[r][c]
                if val != 0:
                    x = c * step + step / 2
                    y = r * step + step / 2
                    
                    # Color coding: Black for original logic, Blue for solved numbers
                    color = "black" 
                    if not is_original and self.app_backend.current_puzzle:
                         # If the cell was empty (0) in the original puzzle, color it blue
                         if self.app_backend.current_puzzle[r][c] == 0:
                             color = "#2980b9"

                    canvas.create_text(x, y, text=str(val), font=("Helvetica", 20, "bold"), fill=color)

    def load_image(self):
        """Handles the image selection dialog and preview."""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if not file_path:
            return

        self.current_image_path = file_path
        
        try:
            # Load and Resize Image for Display
            img = Image.open(file_path)
            img = img.resize((400, 400), Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(img)
            self.canvas_input.create_image(0, 0, anchor="nw", image=self.tk_image)
            
            # Update UI State
            self.lbl_status.config(text="Image loaded. Ready to solve.", fg="blue")
            self.btn_solve.config(state="normal")
            
            # Clear previous results
            self.draw_empty_grid(self.canvas_output)
            self.nav_frame.pack_forget()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def start_solving_thread(self):
        """Starts the solving process in a separate thread to prevent UI freezing."""
        self.btn_solve.config(state="disabled")
        self.btn_load.config(state="disabled")
        self.lbl_status.config(text="Processing with API and solving with SAT... Please wait.", fg="#d35400")
        
        thread = threading.Thread(target=self.process_sudoku)
        thread.start()

    def process_sudoku(self):
        """Orchestrates the API call and SAT solving logic."""
        try:
            # Step 1: Extract Grid from Image (API)
            success_load = self.app_backend.load_puzzle_from_image(self.current_image_path)
            
            if not success_load:
                self.root.after(0, lambda: self.finish_processing(False, "API failed to read the image."))
                return
            
            # Step 2: Solve using SAT
            success_solve = self.app_backend.solve_puzzle()
            
            if success_solve:
                self.solutions = self.app_backend.solutions
                self.root.after(0, lambda: self.finish_processing(True, f"Success! {len(self.solutions)} solution(s) found."))
            else:
                self.root.after(0, lambda: self.finish_processing(False, "No solution found (UNSAT)."))

        except Exception as e:
            self.root.after(0, lambda: self.finish_processing(False, f"Critical Error: {str(e)}"))

    def finish_processing(self, success, message):
        """Updates the UI after the thread finishes."""
        self.btn_solve.config(state="normal")
        self.btn_load.config(state="normal")
        
        if success:
            self.lbl_status.config(text=message, fg="green")
            self.solution_index = 0
            self.show_solution(0)
            
            # Enable navigation if multiple solutions exist
            if len(self.solutions) > 1:
                self.nav_frame.pack(side="left", padx=20)
                self.update_nav_buttons()
        else:
            self.lbl_status.config(text=message, fg="red")
            messagebox.showerror("Operation Failed", message)

    def show_solution(self, index):
        """Displays the solution at the given index."""
        if 0 <= index < len(self.solutions):
            sol_grid = self.solutions[index]
            self.draw_sudoku_grid(self.canvas_output, sol_grid)
            self.lbl_sol_count.config(text=f"{index + 1} / {len(self.solutions)}")

    def next_solution(self):
        """Shows the next solution."""
        if self.solution_index < len(self.solutions) - 1:
            self.solution_index += 1
            self.show_solution(self.solution_index)
            self.update_nav_buttons()

    def prev_solution(self):
        """Shows the previous solution."""
        if self.solution_index > 0:
            self.solution_index -= 1
            self.show_solution(self.solution_index)
            self.update_nav_buttons()

    def update_nav_buttons(self):
        """Enables/Disables navigation buttons based on current index."""
        if self.solution_index == 0:
            self.btn_prev.config(state="disabled")
        else:
            self.btn_prev.config(state="normal")
            
        if self.solution_index == len(self.solutions) - 1:
            self.btn_next.config(state="disabled")
        else:
            self.btn_next.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()