from sat_solving import SudokuSolverApp
import sys


def main():
    """
    Main function - the entry point of the program.
    """
    print("\n" + "="*60)
    print("       SUDOKU SAT SOLVER")
    print("="*60)
    
    # Create the application instance (API key should be configured elsewhere)
    app = SudokuSolverApp()
    
    # Present input options to the user
    print("\nChoose input method:")
    print("  1. Load Sudoku from image")
    print("  2. Use test matrix (fast test)")
    print("  3. Run both (comparison)")
    
    choice = input("\nYour choice (1/2/3): ").strip()
    
    success = False
    
    if choice == "1":
        # Solve from image input
        image_path = input("Enter image path: ").strip()
        
        # Use default path if left empty
        if not image_path:
            image_path = "sudoku_examples/sudoku2.png"
            print(f"Using default path: {image_path}")
        
        success = app.run_from_image(image_path)
        
    elif choice == "2":
        # Solve with a predefined test matrix
        print("\nUsing test matrix...")
        # NOTE: This test matrix contains values > 9 (e.g., 33) and repeats (e.g., 1, 1 
        # in the second row, which should lead to an UNSAT result or error handling).
        test_puzzle = [
            [9, 0, 0, 2, 4, 8, 0, 1, 0],
[0, 4, 5, 3, 0, 0, 8, 0, 9],
[0, 2, 0, 0, 1, 0, 0, 6, 0],
[8, 5, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 8, 3, 2, 0, 0, 4],
[0, 0, 0, 0, 0, 0, 2, 0, 1],
[0, 0, 0, 5, 0, 4, 0, 9, 8],
[0, 0, 0, 0, 2, 0, 0, 0, 0],
[0, 0, 0, 0, 8, 0, 0, 4, 2]
        ]
        success = app.run_from_matrix(test_puzzle)

    else:
        print("✗ Invalid choice!")
        success = False  

    # Final result display
    print("\n" + "="*60)
    if success:
        print("       ✓ PROGRAM COMPLETED SUCCESSFULLY")
    else:
        print("       ✗ PROGRAM FAILED")
    print("="*60 + "\n")
    
    # Exit code (0 for success, 1 for failure)
    sys.exit()


if __name__ == "__main__":
    main()