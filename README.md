<h1 align="center"><img alt="smth" src="https://raw.githubusercontent.com/dmitrvk/smth/master/logo.svg" width="137"/></h1>

<h3 align="center">Command-line tool for scanning books and handwriting in batch mode on Linux</h3>

<p align="center">
  <a href="https://github.com/dmitrvk/smth/actions">
    <img alt="build" src="https://img.shields.io/github/workflow/status/dmitrvk/smth/build?color=0366d6&style=flat-square"/>
  </a>
  <a href="https://codecov.io/gh/dmitrvk/smth">
    <img alt="codecov" src="https://img.shields.io/codecov/c/github/dmitrvk/smth?color=0366d6&style=flat-square&token=NH8F6U8988"/>
  </a>
  <a href="https://github.com/dmitrvk/smth/blob/master/LICENSE">
    <img alt="license" src="https://img.shields.io/pypi/l/smth?color=0366d6&style=flat-square"/>
  </a>
  <a href="https://pypi.org/project/smth">
    <img alt="pypi" src="https://img.shields.io/pypi/v/smth?color=0366d6&style=flat-square"/>
  </a>
  <a href="https://pypi.org/project/smth">
    <img alt="python" src="https://img.shields.io/pypi/pyversions/smth?color=0366d6&style=flat-square"/>
  </a>
</p>

<p align="center">
  <a href="#features">Features</a> &middot;
  <a href="#installation">Installation</a> &middot;
  <a href="#usage">Usage</a> &middot;
  <a href="#configuration">Configuration</a>
</p>

<p align="center"><img src="https://raw.githubusercontent.com/dmitrvk/smth/master/smth.gif"></p>

## Features

* Scan sheets in batch mode
* Merge scanned images automatically into a single PDF file
* Add new pages to existing sheets scanned before
* Replace pages by scanning them again
* Upload PDF files to Google Drive (requires [PyDrive])

## Installation

```
pip install smth
```

Or install from source:

```bash
git clone https://github.com/dmitrvk/smth
cd smth
sudo python setup.py install
```

If you got an error with missing `sane/sane.h`,
make sure you have *sane* installed.
For Debian-based distributions, you may need to install `libsane-dev` package.

If you want to upload scanned documents to Google Drive, install [PyDrive]:

```
pip install PyDrive
```

## Usage

Assume you have some handwriting, e.g. lecture notes you want to scan.

1. Create a new *notebook type*.

This is needed to tell the program how to crop and rotate scanned images
properly:

```
$ smth types --create
? Enter title:  A5
? Enter page width in millimeters:  148
? Enter page height in millimeters:  210
? Are pages paired? (default - no)  No
Created type 'A5' 148x210mm.
```

2. Create a new *notebook*.

```
$ smth create
? Enter title:  lectures
? Choose type  A5
? Enter path to PDF:  ~/scans
? Enter 1st page number:  1
Create notebook 'lecture' of type 'A5' at '/home/user/scans/lecture.pdf'
```

All scanned pages will be inserted in the PDF file, so you will have all pages
in one file.

3. Start scanning process.

```
$ smth scan
? Choose notebook  lectures
? How many new pages? (leave empty if none)  3
Searching for available devices...
? Choose device  pixma:04A9176D_3EBCC9
```

Scanning process will start immediately.
All you need is to put new pages on scanner's glass one after another.

Generated PDF will contain all scanned pages.
Separate *jpg* images will be saved at `~/.local/share/smth/pages/`.

*smth* remembers all notebooks you scanned before, all notebook types and the
scanner device.  With *smth* you can add new pages to existing notebooks or
replace any page in a notebook by scanning the page again.

### Crop images properly

#### Single pages (portrait)

Always cropped from the top left corner of scanner's output.
If scanner's output is landscape, the image will be rotated 90 counter-clockwise
before cropping.

#### Single pages (landscape)

Always cropped from the top left corner of image in landscape orientation.
The image will be rotated 90 clockwise before cropping if it is portrait.

#### Paired pages

If scanner's output is portrait, always rotate 90 clockwise.

The only exception is if the page height is larger than the short side of
scanner's glass.  In this case portrait orientation will be kept.

If both pages fits the scanner's glass, then both pages will be cropped at once
from the top left corner.

If the width of two pages is larger then the scanner glass' width,
then left pages will be cropped from the top left corner and
the right pages will be cropped from the top right corner.

### Uploading to Google Drive

*smth is still in active development.  Use this at your own risk.*

This feature requires [PyDrive] installed.

The `upload` command is used to upload notebooks to Google Drive.
The first time you will be asked to visit a link, grant access to the
application and copy-and-paste the verification code.
After that you can choose a notebook you want to upload.

**'smth' folder will be created in the root folder on your Google Drive.
All files will be uploaded in that folder.**

After successful uploading you may want to share the file with others.
You can do this with your web browser or a mobile app,
but also you can run the `share` command, choose a notebook you want to
share and copy the link.  The PDF file on Google Drive will become available for
reading to anyone with the link.

### Commands

#### create

Create a new notebook with specified title, type, path to PDF and the 1st page
number.

#### delete

Delete a notebook.

#### list

Show a list of available notebooks.

#### open

Open notebook's PDF file in the default PDF viewer.

#### scan

Scan notebook: add new pages and/or replace existing ones.

Optional arguments:
* `--set-device` - reset the device which is used to
prefrorm scanning and choose another one.

If *smth* is run without arguments, this command will be run by default.

#### share

Make a notebook's PDF file on Google Drive available for anyone with a link and
show the link.

#### types

Manage types of notebooks.

A *type* of a notebook specifies its pages size and whether pages are paired.
This information is essential for *smth* when it crops and rotates scanned
images and inserts pages into a PDF file.

```
         w
     ---------          Notebook that consists of single pages.
     ---------
   h ---------
     ---------
     ---------          w - page width in millimeters,
     ---------          h - page height in millimeters

        w
     -------^-------   Notebook with paired pages.
     -------^-------
   h -------^-------
     -------^-------   w - page width in millimeters,
     -------^-------   h - page height in millimeters
```

If run without arguments, show the list of available notebook types.

Optional arguments:
* `--create` - create a new notebook type.
* `--delete` - delete a notebook type.

The type of A4 format in portrait orientation is created by default.

#### update

Change notebook's title or path to PDF file.

#### upload

Upload a notebook's PDF file to 'smth' folder on Google Drive.

## Configuration

Configuration is stored in `~/.config/smth/smth.conf`:

```
[scanner]
device = <device>
delay = 0
mode = Gray
resolution = 150
ask_upload = True
```

#### device

Device name which *sane* uses for scanning.

When running `scan` command, the value of this parameter is used by default.
You can change it manually or run `scan` command with `--set-device` option:

```
$ smth scan --set-device
```

#### delay

Time in seconds which should pass before scanning of the next page starts.

Set this option to a higher value if you need extra time to put next sheet on
scanner's glass.

#### mode

Selects the scan mode (e.g., Gray or Color)

#### resolution

Sets the resolution of the scanned images (e.g., 75, 150, 300 etc.).

#### ask_upload

If `True` (and [PyDrive] is installed),
you will be asked whether you want to upload a
notebook to Google Drive when scanning is completed.

Set the parameter to `False` to disable this behavior.

## Licensing

This project is licensed under the
[GNU General Public License v3.0](LICENSE).

[PyDrive]: https://github.com/gsuitedevs/PyDrive
