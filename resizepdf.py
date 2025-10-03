import fitz  # PyMuPDF
import os
from pathlib import Path
import time

def resize_pdf(input_path, output_dir, output_name, target_width, target_height):
    """
    Resizes a PDF while maintaining high-resolution image quality.
    
    Args:
        input_path (str): Input PDF path
        output_dir (str): Output directory
        output_name (str): Output file name
        target_width (int): Target width in points
        target_height (int): Target height in points
    """
    
    print("\n" + "="*70)
    print("Starting PDF resize process...")
    print("="*70)
    print(f"Input file: {input_path}")
    print(f"Target dimensions: {target_width}x{target_height} points")
    print("-"*70)
    
    # Check if file exists
    if not os.path.exists(input_path):
        print(f"ERROR: File {input_path} does not exist!")
        return False
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = os.path.join(output_dir, output_name)
    
    try:
        # Open input PDF
        print("\nOpening PDF...")
        doc_input = fitz.open(input_path)
        total_pages = len(doc_input)
        print(f"Total pages: {total_pages}")
        
        # Create new PDF
        doc_output = fitz.open()
        
        start_time = time.time()
        
        print("\nProcessing pages:")
        print("-"*70)
        
        for page_num in range(total_pages):
            # Show progress for every page
            elapsed = time.time() - start_time
            progress = (page_num + 1) / total_pages * 100
            eta = elapsed / (page_num + 1) * (total_pages - page_num - 1) if page_num > 0 else 0
            
            # Progress bar
            bar_length = 40
            filled_length = int(bar_length * (page_num + 1) // total_pages)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            
            print(f"\rPage {page_num + 1}/{total_pages} |{bar}| {progress:.1f}% | "
                  f"Elapsed: {elapsed:.1f}s | ETA: {eta:.1f}s", end='', flush=True)
            
            # Get current page
            page = doc_input[page_num]
            
            # Calculate scale factor to maintain proportions
            page_rect = page.rect
            current_width = page_rect.width
            current_height = page_rect.height
            
            scale_x = target_width / current_width
            scale_y = target_height / current_height
            
            # Use smaller scale factor to maintain proportions
            # and avoid cutting content
            scale = min(scale_x, scale_y)
            
            # Calculate new dimensions maintaining proportions
            new_width = current_width * scale
            new_height = current_height * scale
            
            # Create transformation matrix for resizing
            # Use high resolution (300 DPI) to maintain quality
            matrix = fitz.Matrix(scale, scale)
            
            # Render page as high-resolution image
            # Use alpha=False for images without transparency (lighter)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            
            # Create new page in output document
            new_page = doc_output.new_page(width=target_width, height=target_height)
            
            # Calculate position to center the image
            x_offset = (target_width - new_width) / 2
            y_offset = (target_height - new_height) / 2
            
            # Insert image in new page
            img_rect = fitz.Rect(x_offset, y_offset, x_offset + new_width, y_offset + new_height)
            new_page.insert_image(img_rect, pixmap=pix)
            
            # Free pixmap memory
            pix = None
        
        print("\n" + "-"*70)
        
        # Save new PDF
        print("\nSaving resized PDF...")
        doc_output.save(output_path, garbage=4, deflate=True, clean=True)
        
        # Close documents
        doc_input.close()
        doc_output.close()
        
        # Final statistics
        total_time = time.time() - start_time
        input_size = os.path.getsize(input_path) / (1024 * 1024)  # MB
        output_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        
        print("\n" + "="*70)
        print("Process completed successfully!")
        print("="*70)
        print(f"Statistics:")
        print(f"  - Pages processed: {total_pages}")
        print(f"  - Total time: {total_time/60:.2f} minutes")
        print(f"  - Average time per page: {total_time/total_pages:.2f} seconds")
        print(f"  - Original file size: {input_size:.2f} MB")
        print(f"  - Output file size: {output_size:.2f} MB")
        print(f"  - Compression ratio: {(input_size/output_size):.2f}x")
        print(f"  - Output file saved at: {output_path}")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\nERROR during process: {str(e)}")
        return False

def get_valid_path():
    """Get valid file path from user."""
    while True:
        path = input("\nEnter the full path of the PDF file to resize: ").strip()
        # Remove quotes if present
        path = path.strip('"').strip("'")
        # Remove file:/// prefix if present
        if path.startswith('file:///'):
            path = path[8:]
        elif path.startswith('file://'):
            path = path[7:]
        
        if os.path.exists(path):
            if path.lower().endswith('.pdf'):
                return path
            else:
                print("ERROR: File is not a PDF. Please enter a valid PDF file.")
        else:
            print("ERROR: File does not exist. Please enter a valid path.")

def get_valid_dimension(dimension_name):
    """Get valid dimension from user."""
    while True:
        try:
            value = input(f"Enter target {dimension_name} in points (e.g., 1149): ").strip()
            value = int(value)
            if value > 0:
                return value
            else:
                print("ERROR: Dimension must be a positive number.")
        except ValueError:
            print("ERROR: Please enter a valid integer number.")

def get_output_name():
    """Get output file name from user."""
    output_name = input("\nEnter output file name (press Enter for default 'resized_output.pdf'): ").strip()
    
    if not output_name:
        return "resized_output.pdf"
    
    # Add .pdf extension if not present
    if not output_name.lower().endswith('.pdf'):
        output_name += '.pdf'
    
    return output_name

def get_output_directory(default_dir):
    """Get output directory from user."""
    print(f"\nDefault output directory: {default_dir}")
    output_dir = input("Enter output directory (press Enter for default): ").strip()
    
    if not output_dir:
        return default_dir
    
    # Remove quotes if present
    output_dir = output_dir.strip('"').strip("'")
    
    # Create directory if it doesn't exist
    if not os.path.exists(output_dir):
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            print(f"Directory created: {output_dir}")
        except Exception as e:
            print(f"ERROR: Could not create directory: {e}")
            print(f"Using default directory: {default_dir}")
            return default_dir
    
    return output_dir

def main():
    print("\n" + "="*70)
    print("PDF RESIZER - HIGH QUALITY")
    print("="*70)
    
    # Get input from user
    input_path = get_valid_path()
    
    print("\nSpecify output dimensions:")
    target_width = get_valid_dimension("WIDTH")
    target_height = get_valid_dimension("HEIGHT")
    
    # Get output file name
    output_name = get_output_name()
    
    # Setup output directory
    input_dir = os.path.dirname(input_path)
    output_dir = get_output_directory(input_dir)
    
    # Show summary
    print("\n" + "-"*70)
    print("Summary:")
    print(f"  Input file: {input_path}")
    print(f"  Output file: {os.path.join(output_dir, output_name)}")
    print(f"  Dimensions: {target_width}x{target_height} points")
    print("-"*70)
    
    # Confirm before proceeding
    confirm = input("\nPress Enter to proceed or type 'no' to cancel: ").strip().lower()
    if confirm == 'no':
        print("Operation cancelled by user.")
        return
    
    success = resize_pdf(
        input_path=input_path,
        output_dir=output_dir,
        output_name=output_name,
        target_width=target_width,
        target_height=target_height
    )
    
    if success:
        print("Operation completed successfully!")
    else:
        print("Operation failed. Check errors above.")

if __name__ == "__main__":
    main()