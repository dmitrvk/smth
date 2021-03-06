# License: GNU GPL Version 3

"""Command-line tool for scanning books and handwriting in batch mode on Linux.

Features:
    * Scan sheets in batch mode
    * Merge scanned images automatically into a single PDF file
    * Add new pages to existing sheets scanned before
    * Replace pages by scanning them again
    * Upload PDF files to Google Drive (requires PyDrive)

The program uses SANE library to interact with scanner devices.
"""

__version__ = '0.8.0'
