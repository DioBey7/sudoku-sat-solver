"""This module processes images of Sudoku puzzles to extract and validate the Sudoku grid. It uses Google's Generative AI API 
to analyze the images and retrieve the grid data. The module includes functions for validating the structure and values of the Sudoku grid,
as well as handling API interactions and errors."""

import google.generativeai as genai
from google.api_core import exceptions
import PIL.Image as Image
import json
import os
import time
import re

API_KEY = "AIzaSyAHWRVD-JmqPTyeG9_C8aQAkvEmMiiF-Pg"
genai.configure(api_key=API_KEY)

# Validating the structure of the Sudoku grid (9x9)
def validate_structure(grid):
    if not isinstance(grid, list):
        return False
    
    if len(grid) != 9:
        return False
    
    for row in grid:
        if not isinstance(row, list):
            return False
        if len(row) != 9:
            return False
            
    return True

# Validating the values within the Sudoku grid (0-9)
def validate_values(grid):
    cleaned_matrix = []
    
    for row_idx, row in enumerate(grid):
        cleaned_row = []
        for col_idx, cell in enumerate(row):
            try:
                str_val = str(cell).strip()
                
                if not str_val or str_val in [".", "?", "*", "X", "", "_"]: # Common placeholders for empty cells
                    cleaned_row.append(0)
                    continue
                
                val = int(str_val)
                
                if 0 <= val <= 9:
                    cleaned_row.append(val)
                else:
                    print(f"Validation Error: Cell ({row_idx+1},{col_idx+1}) contains invalid number '{val}'.") # Indices are 1-based for user clarity
                    return None
            except (ValueError, TypeError):
                cleaned_row.append(0)
                
        cleaned_matrix.append(cleaned_row)
    
    return cleaned_matrix

# Extract JSON array from text response using regex
def extract_json_array(text):
    try:
        match = re.search(r'\[\s*\[.*\]\s*\]', text, re.DOTALL)
        if match:
            return match.group(0)
        return text
    except Exception:
        return text
    
# Main function to get Sudoku grid from image using Generative AI API
def get_sudoku_grid(image_path, max_retries=3):
    if not os.path.exists(image_path):
        print(f"Error: File not found -> {image_path}")
        return None
        
    image = Image.open(image_path)
    model = genai.GenerativeModel("gemini-2.5-flash") # Ideal for image analysis (according to the debuggings and tests we have done)
    
    # I defined a very strict prompt to avoid any misinterpretation by the model because of the complexity of the task and API limitations.
    prompt = """
    Analyze the image and return the 9x9 Sudoku grid as a raw JSON list of lists.
    STRICT RULES:
    1. Transcribe EXACTLY what you see. Do not solve the puzzle.
    2. Use 0 for empty cells.
    3. If a cell has a multi-digit number (e.g. 17), write it as 17. DO NOT split it into separate cells.
    4. If the grid is cut off or missing blocks, return only the visible rows/cols. DO NOT autocomplete with zeros.
    5. No markdown, no explanations.
    6. Do not dislocate numbers from their original cells.
    7. Return ONLY the JSON array, nothing else.
    """

    for attempt in range(max_retries):
        try:
            response = model.generate_content([prompt, image])
            raw_text = response.text.strip()
            
            json_text = extract_json_array(raw_text)
            if "```" in json_text:
                json_text = json_text.replace("```json", "").replace("```", "").strip()
            
            grid = json.loads(json_text)

            if not validate_structure(grid):
                print(f"Structural Error in {os.path.basename(image_path)}: Input is not a valid 9x9 grid (Missing blocks/rows detected).")
                return None
            
            final_grid = validate_values(grid)
            
            if final_grid is None:
                print(f"Value Error in {os.path.basename(image_path)}: Grid contains numbers outside 1-9 range.")
                return None
                
            return final_grid
        
        # Handling API quota limits and other exceptions, using delays for retries to reduce rapid failures and API overload.
        except exceptions.ResourceExhausted:
            print(f"Quota limit hit. Waiting 60s... (Attempt {attempt + 1}/{max_retries})")
            time.sleep(60)
            continue
            
        except json.JSONDecodeError:
            print("JSON Parsing error, retrying...")
            continue

        except Exception as e:
            print(f"Critical API Error: {e}")
            time.sleep(2)
            return None
    
    print("Operation failed after max retries.")
    return None

# Main part of the code to batch processing of images in a specified folder for Sudoku grid extraction and validation    
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_folder = os.path.join(current_dir, "sudoku_examples")
    
    if os.path.exists(base_folder):
        files = [f for f in os.listdir(base_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))] #.jpg , .png , .jpeg supported for publishing purposes
        print(f"Found {len(files)} images. Starting batch validation...\n")

        for i, filename in enumerate(files):
            full_path = os.path.join(base_folder, filename)
            print(f"Processing: {filename}")
            
            result = get_sudoku_grid(full_path)

            if result:
                print("VALID SUDOKU DETECTED:")
                for row in result:
                    print(row)
            else:
                print("INVALID SUDOKU (Correctly identified as error).") #invalid situations showed as a error message
            
            print("-" * 40)
            
            if i < len(files) - 1:
                time.sleep(10)
    else:
        print(f"Directory not found: {base_folder}")