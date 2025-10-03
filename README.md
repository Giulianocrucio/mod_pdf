# PDF Merger and Resizer

This repository contains two Python scripts designed to handle PDF processing tasks without file size limitations and with no image quality loss.

## Features

* **Merge PDFs and CBZ Files**

  * Combines multiple PDF and CBZ files into a single high-quality PDF.
  * Maintains original resolution and avoids recompression.
  * Handles files of any size, with natural file ordering.
  * *Note*: During merging, the script scans the input folder and all its subfolders to locate PDF files.

* **Resize PDFs**

  * Resizes PDF pages to user-defined dimensions.
  * Preserves image quality by rendering pages at high resolution.
  * Centers content within target dimensions without cropping.

## Requirements

* Python 3.x
* Dependencies: `PyMuPDF (fitz)`, `img2pdf`

## Usage

Run the scripts from the command line and follow the interactive prompts:

* `python mergepdf.py` → Merge PDFs/CBZ into one PDF.
* `python resizepdf.py` → Resize an existing PDF to custom dimensions.

Both scripts ensure unlimited file size handling and quality preservation.
