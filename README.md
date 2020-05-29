# smth

![build](https://github.com/dmitrvk/smth/workflows/build/badge.svg)

*smth* is a command-line tool which allows you to scan in batch mode on Linux.

## Features

* Scan sheets in batch mode
* Merge scanned images automatically into a single PDF file
* Add new pages to existing sheets scanned before

## Installation

From source:

```bash
git clone https://github.com/dmitrvk/smth
cd smth
pip install .
```

If you got an error with missing `sane/sane.h`,
make sure you have *sane* installed in your system.
For Debian-based distributions, you may need to install `libsane-dev` package.

## Usage

Assume you have some handwriting on A4 sheets, e.g. lecture notes.
To scan them, first, create a new *notebook*:

```
$ smth create
[?] Enter title: lectures
[?] Choose type: A4
 > A4

[?] Enter path to PDF: ~/lectures.pdf
[?] Enter 1st page number: 1
Create notebook 'lectures' of type 'A4' at '/home/dmitryk/lectures.pdf'
```

Now you can start scanning process (don't forget to connect the scanner):

```
$ smth scan
Searching for available devices...
[?] Choose device: pixma:04A9176D_3EBCC9
   v4l:/dev/video0
 > pixma:04A9176D_3EBCC9

[?] Choose notebook: lectures
 > lectures

[?] How many new pages? (leave empty if none): 3
Scanning page 1...
Scanning page 2...
Scanning page 3...
PDF saved at '/home/user/lectures.pdf'.
Done.
```
Generated PDF will contain all scanned pages.
Separate *jpg* images are stored in `~/.local/share/smth/pages/`.

> Though the type of the notebook is set to 'A4', smth does not crop or rotate scanned images to make them fit the 'A4' format.  It just merges pages into a PDF file as they are.  Custom page sizes will be implemented in future versions.

When you scan new pages of the same notebook,
*smth* automatically inserts them at the end of PDF file:

```
smth scan
Searching for available devices...
[?] Choose device: pixma:04A9176D_3EBCC9
   v4l:/dev/video0
 > pixma:04A9176D_3EBCC9

[?] Choose notebook: lectures
 > lectures

[?] How many new pages? (leave empty if none): 2
Scanning page 4...
Scanning page 5...
PDF saved at '/home/dmitryk/lectures.pdf'.
Done.
```

## Licensing

This project is licensed under the
[GNU General Public License v3.0](LICENSE).

