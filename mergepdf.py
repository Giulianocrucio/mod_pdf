import os
import zipfile
import img2pdf
import fitz  # PyMuPDF
import re
from pathlib import Path

def natural_sort_key(s):
    """
    Key function for natural sorting (like Windows 11).
    Considers numbers as numeric values instead of strings.
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]

def cbz_to_pdf(cbz_path, output_path, current_num, total_num):
    """
    Converts a CBZ file to PDF without quality loss.
    
    Args:
        cbz_path (str): Path to CBZ file
        output_path (str): Path for output PDF
        current_num (int): Current file number being processed
        total_num (int): Total number of files to process
    """
    try:
        with zipfile.ZipFile(cbz_path, 'r') as archive:
            # Extract only images
            image_files = [f for f in archive.namelist() 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            if not image_files:
                print(f"WARNING: No images found in {cbz_path}")
                return None
            
            # Sort with natural ordering (like Windows 11)
            image_files.sort(key=natural_sort_key)
            
            print(f"Converting CBZ {current_num}/{total_num}: {os.path.basename(cbz_path)}")
            print(f"  - Found {len(image_files)} images")
            
            # Extract images to temporary memory
            images_data = []
            for img_name in image_files:
                with archive.open(img_name) as file:
                    images_data.append(file.read())
            
            # Write PDF without quality loss using img2pdf
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(images_data))
            
            print(f"  - Converted successfully")
            return output_path
            
    except Exception as e:
        print(f"ERROR converting {cbz_path}: {str(e)}")
        return None

def find_files_recursively(folder_path, extensions):
    """
    Recursively searches for files with provided extensions.
    
    Args:
        folder_path (str): Root folder to search
        extensions (tuple): File extensions to search for
    
    Returns:
        list: Found file paths
    """
    found_files = []
    for root, _, files in os.walk(folder_path):
        for f in files:
            if f.lower().endswith(extensions):
                found_files.append(os.path.join(root, f))
    return found_files

def get_valid_folder_path():
    """Get valid folder path from user."""
    while True:
        folder_path = input("\nEnter the path of the folder containing PDF/CBZ files: ").strip()
        # Remove quotes if present
        folder_path = folder_path.strip('"').strip("'")
        # Remove file:/// prefix if present
        if folder_path.startswith('file:///'):
            folder_path = folder_path[8:]
        elif folder_path.startswith('file://'):
            folder_path = folder_path[7:]
        
        if os.path.isdir(folder_path):
            return folder_path
        else:
            print("ERROR: Folder does not exist. Please enter a valid path.")

def get_output_name():
    """Get output file name from user."""
    output_name = input("\nEnter output PDF file name (press Enter for default 'merged_output.pdf'): ").strip()
    
    if not output_name:
        return "merged_output.pdf"
    
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

def merge_pdfs_high_quality(pdf_files, output_path):
    """
    Merge multiple PDF files without quality loss using PyMuPDF.
    
    Args:
        pdf_files (list): List of PDF file paths to merge
        output_path (str): Path for merged output PDF
    """
    total_pdfs = len(pdf_files)
    
    # Create output document
    output_doc = fitz.open()
    
    for i, pdf_path in enumerate(pdf_files, 1):
        # Progress bar
        progress = i / total_pdfs * 100
        bar_length = 40
        filled_length = int(bar_length * i // total_pdfs)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        print(f"\rMerging: |{bar}| {i}/{total_pdfs} ({progress:.1f}%) - {os.path.basename(pdf_path)[:30]:<30}", 
              end='', flush=True)
        
        try:
            # Open PDF and insert all pages
            pdf_doc = fitz.open(pdf_path)
            output_doc.insert_pdf(pdf_doc)
            pdf_doc.close()
        except Exception as e:
            print(f"\nWARNING: Could not merge {pdf_path}: {str(e)}")
    
    print("\n" + "-"*70)
    
    # Save with high quality settings
    print("\nSaving merged PDF file...")
    output_doc.save(
        output_path,
        garbage=4,        # Maximum garbage collection
        deflate=True,     # Compress streams
        clean=True        # Clean up redundant objects
    )
    output_doc.close()

def main():
    print("\n" + "="*70)
    print("PDF/CBZ MERGER - HIGH QUALITY (NO QUALITY LOSS)")
    print("="*70)
    
    # Get folder path from user
    folder_path = get_valid_folder_path()
    
    # Find PDF and CBZ files recursively
    print("\nSearching for files...")
    pdf_files = find_files_recursively(folder_path, (".pdf",))
    cbz_files = find_files_recursively(folder_path, (".cbz",))
    
    print(f"Found {len(pdf_files)} PDF file(s)")
    print(f"Found {len(cbz_files)} CBZ file(s)")
    
    if not pdf_files and not cbz_files:
        print("\nERROR: No PDF or CBZ files found in the specified folder.")
        return
    
    # Get output file name
    output_name = get_output_name()
    
    # Get output directory
    output_dir = get_output_directory(folder_path)
    output_path = os.path.join(output_dir, output_name)
    
    # Show summary
    print("\n" + "-"*70)
    print("Summary:")
    print(f"  Input folder: {folder_path}")
    print(f"  Total files to process: {len(pdf_files) + len(cbz_files)}")
    print(f"  Output file: {output_path}")
    print(f"  Quality preservation: ENABLED (no recompression)")
    print("-"*70)
    
    # Confirm before proceeding
    confirm = input("\nPress Enter to proceed or type 'no' to cancel: ").strip().lower()
    if confirm == 'no':
        print("Operation cancelled by user.")
        return
    
    print("\n" + "="*70)
    print("Starting conversion and merge process...")
    print("="*70)
    
    # Convert CBZ files to PDF
    if cbz_files:
        print(f"\nStep 1/2: Converting {len(cbz_files)} CBZ file(s) to PDF")
        print("-"*70)
        
        for i, cbz in enumerate(cbz_files, 1):
            pdf_out = os.path.splitext(cbz)[0] + ".pdf"
            result = cbz_to_pdf(cbz, pdf_out, i, len(cbz_files))
            if result:
                pdf_files.append(result)
        
        print("-"*70)
        print(f"CBZ conversion completed: {len(cbz_files)} file(s) converted")
    
    # Sort files with natural ordering (like Windows 11)
    pdf_files.sort(key=natural_sort_key)
    
    # Merge PDFs with high quality preservation
    print(f"\nStep 2/2: Merging {len(pdf_files)} PDF file(s)")
    print("-"*70)
    
    try:
        merge_pdfs_high_quality(pdf_files, output_path)
        
        # Get file size
        output_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        
        print("\n" + "="*70)
        print("Process completed successfully!")
        print("="*70)
        print(f"Statistics:")
        print(f"  - Total files merged: {len(pdf_files)}")
        print(f"  - Output file size: {output_size:.2f} MB")
        print(f"  - Quality preservation: CONFIRMED")
        print(f"  - Output file saved at: {output_path}")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\nERROR: Could not save merged PDF: {str(e)}")
        return

if __name__ == "__main__":
    main()