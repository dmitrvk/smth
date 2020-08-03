# License: GNU GPL Version 3

"""Command-line tool for scanning books and handwriting in batch mode on Linux.

Features:
    * Scan sheets in batch mode
    * Merge scanned images automatically into a single PDF file
    * Add new pages to existing sheets scanned before
    * Replace pages by scanning them again
    * Upload PDF files to Google Drive (requires PyDrive)

The progran uses the SANE library to interact with scanner devices.
"""
