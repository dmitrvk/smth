<h1 align="center">smth</h1>

<h3 align="center">Command-line tool for scanning in batch mode on Linux.</h3>

<p align="center">
  <a href="https://github.com/dmitrvk/smth/actions">
    <img alt="build" src="https://github.com/dmitrvk/smth/workflows/build/badge.svg"/>
  </a>
  <a href="https://codecov.io/gh/dmitrvk/smth">
    <img alt="codecov" src="https://codecov.io/gh/dmitrvk/smth/branch/master/graph/badge.svg?token=NH8F6U8988"/>
  </a>
  <a href="https://github.com/dmitrvk/smth/blob/master/LICENSE">
    <img alt="license" src="https://img.shields.io/pypi/l/smth"/>
  </a>
  <a href="https://pypi.org/project/smth">
    <img alt="pypi" src="https://img.shields.io/pypi/v/smth"/>
  </a>
  <a href="https://pypi.org/project/smth">
    <img alt="python" src="https://img.shields.io/pypi/pyversions/smth"/>
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

## Installation

```
pip install smth
```

Or install from source:

```bash
git clone https://github.com/dmitrvk/smth
cd smth
pip install .
```

If you got an error with missing `sane/sane.h`,
make sure you have *sane* installed.
For Debian-based distributions, you may need to install `libsane-dev` package.

## Usage

Assume you have some handwriting on A4 sheets, e.g. lecture notes.
To scan them, first, create a new *notebook*:

```
$ smth create
```

Now you can start scanning process (don't forget to connect the scanner):

```
$ smth scan
```

First time you will be asked for scanner device you want to use.
It takes some time for *sane* to load the list of devices,
but next time the device you choose will be used by default.
See instructions below on how you can change the default device.

Generated PDF will contain all scanned pages.
Separate *jpg* images are stored in `~/.local/share/smth/pages/`.

> Though the type of the notebook is set to 'A4', smth does not crop or rotate scanned images to make them fit the 'A4' format.  It just merges pages into a PDF file as they are.  Custom page sizes will be implemented in future versions.

When you scan new pages of the same notebook,
*smth* automatically inserts them at the end of PDF file.

## Configuration

Configuration is stored in `~/.config/smth/smth.conf`:

```
[scanner]
device = <device>
delay = 0
```

`<device>` is a device name which *sane* uses for scanning.
When running `scan` command, the value of this parameter is used by default.
You can change it manually or run `scan` command with `--set-device` option:

```
$ smth scan --set-device
```

To identify your scanner's name, run `scanimage -L`.

`delay` option specifies time in seconds which should pass before scanning
of the next page starts.  Set this option to higher value if you need extra
time to put next sheet on scanner's glass.

## Licensing

This project is licensed under the
[GNU General Public License v3.0](LICENSE).

