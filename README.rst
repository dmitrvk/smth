smth: command-line tool for scanning on Linux
#############################################


.. class:: no-web no-pdf

    |build| |coverage| |license| |pypi| |python|

.. class:: no-web no-pdf

    .. image:: https://raw.githubusercontent.com/dmitrvk/smth/master/smth.gif
        :alt: smth demo
        :align: center
        :target: https://raw.githubusercontent.com/dmitrvk/smth/master/smth.gif

.. contents::

.. section-numbering::


Features
========

* Scan books and handwriting in batch mode
* Merge scanned images automatically into a single PDF file
* Add new pages to existing sheets scanned before
* Replace pages by scanning them again
* Upload PDF files to Google Drive (requires `PyDrive`_)


Installation
============

.. code-block:: bash

    pip install smth


Python version 3.8 or greater is required.

Make sure you have *SANE* installed.
In Debian-based distributions you may need to install *libsane-dev* package.

If you want to upload scanned documents to Google Drive, install `PyDrive`_:

.. code-block:: bash

    pip install PyDrive


Usage
=====

Basics
------

1. Create a new *notebook type*.

This is needed to tell the program how to crop and rotate scanned images
properly:

.. code-block:: bash

    $ smth types --create

You will be asked for a type's title, page width and height in millimeters and
whether the pages are paired.

2. Create a new *notebook*.

.. code-block:: bash

    $ smth create

You will be asked for a notebook's title, typy, path to PDF file and the 1st
page number.  All scanned pages will be inserted in the PDF file, so you will
have all pages in one file.

3. Start scanning process.

.. code-block:: bash

    $ smth scan

When you run the command, you should choose the scanner device and the notebook.
Also you should enter the number of pages you want to scan (for new pages)
and/or separate page numbers (for existing pages if you wish to scan them
again).  When scanning starts, all you need is to put new pages on scanner's
glass one after another.

Generated PDF will contain all scanned pages.
Separate *jpg* images will be saved at ``~/.local/share/smth/pages/``.

*smth* remembers all notebooks you scanned before, all notebook types and the
scanner device.  With *smth* you can add new pages to existing notebooks or
replace any page in a notebook by scanning the page again.

Cropping images properly
------------------------

Single pages (portrait)
~~~~~~~~~~~~~~~~~~~~~~~

Always cropped from the top left corner of scanner's output.
If scanner's output is landscape, the image will be rotated 90 counter-clockwise
before cropping.

Single pages (landscape)
~~~~~~~~~~~~~~~~~~~~~~~~

Always cropped from the top left corner of image in landscape orientation.
The image will be rotated 90 clockwise before cropping if it is portrait.

Paired pages
~~~~~~~~~~~~

If scanner's output is portrait, always rotate 90 clockwise.

The only exception is if the page height is larger than the short side of
scanner's glass.  In this case portrait orientation will be kept.

If both pages fits the scanner's glass, then both pages will be cropped at once
from the top left corner.

If the width of two pages is larger then the scanner glass' width,
then left pages will be cropped from the top left corner and
the right pages will be cropped from the top right corner.

Uploading to Google Drive
-------------------------

This feature requires `PyDrive`_ installed.

The *upload* command is used to upload notebooks to Google Drive.
The first time you will be asked to visit a link, grant access to the
application and copy-and-paste the verification code.
After that you can choose a notebook you want to upload.

**'smth' folder will be created in the root folder on your Google Drive.
All files will be uploaded in that folder.**

After successful uploading you may want to share the file with others.
You can do this with your web browser or a mobile app,
but also you can run the *share* command, choose a notebook you want to
share and copy the link.  The PDF file on Google Drive will become available for
reading to anyone with the link.

Commands
--------

create
~~~~~~

Creates a new notebook with specified title, type, path to PDF and the 1st page
number.

delete
~~~~~~

Deletes a notebook.

list
~~~~

Shows a list of available notebooks.

open
~~~~

Opens notebook's PDF file in the default PDF viewer.

scan
~~~~

Scans notebook: adds new pages and/or replaces existing ones.

Optional arguments:
* ``--set-device`` - reset the device which is used to
prefrorm scanning and choose another one.

If *smth* is run without arguments, this command will be run by default.

share
~~~~~

Makes a notebook's PDF file on Google Drive available for anyone with a link and
show the link.

types
~~~~~

Creates, deletes or shows a list of notebook types.

A *type* of a notebook specifies its pages size and whether pages are paired.
This information is essential for *smth* when it crops and rotates scanned
images and inserts pages into a PDF file.

::

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

Without arguments, the command shows a list of available notebook types.

Optional arguments:
* ``--create`` - create a new notebook type.
* ``--delete`` - delete a notebook type.

The type of A4 format in the portrait orientation is created by default.

update
~~~~~~

Changes notebook's title or path to PDF file.

upload
~~~~~~

Uploads a notebook's PDF file to 'smth' folder on Google Drive.


Configuration
=============

Configuration file
------------------

Configuration is stored in ``~/.config/smth/smth.conf``.  The file looks as the
following:

::
    [scanner]
    device = <device>
    delay = 0
    mode = Gray
    resolution = 150
    ask_upload = True


Options
-------

device
~~~~~~

Device name which *sane* uses for scanning.

When running ``scan`` command, the value of this parameter is used by default.
You can change it manually or run ``scan`` command with ``--set-device`` option:

.. code-block:: bash

    $ smth scan --set-device

delay
~~~~~

Time in seconds which should pass before scanning of the next page starts.

Set this option to a higher value if you need extra time to put next sheet on
scanner's glass.

mode
~~~~

Selects the scan mode (e.g., *Gray* or *Color*)

resolution
~~~~~~~~~~

Sets the resolution of the scanned images (e.g., 75, 150, 300 etc.).

ask_upload
~~~~~~~~~~

If *True* (and `PyDrive`_ is installed),
you will be asked whether you want to upload a
notebook to Google Drive when scanning is completed.

Set the parameter to *False* to disable this behavior.


Contributing
============

See `CONTRIBUTING.rst <https://github.com/dmitrvk/smth/blob/master/CONTRIBUTING.rst>`_.


Licensing
=========

This project is licensed under the `GNU General Public License v3.0`_.


.. _GNU General Public License v3.0: https://github.com/dmitrvk/smth/blob/master/LICENSE

.. _PyDrive: https://github.com/gsuitedevs/PyDrive

.. |build| image:: https://img.shields.io/github/workflow/status/dmitrvk/smth/build?color=0366d6&style=flat-square
    :target: https://github.com/dmitrvk/smth/actions
    :alt: Build status

.. |coverage| image:: https://img.shields.io/codecov/c/github/dmitrvk/smth?color=0366d6&style=flat-square&token=NH8F6U8988
    :target: https://codecov.io/gh/dmitrvk/smth
    :alt: Test coverage

.. |license| image:: https://img.shields.io/pypi/l/smth?color=0366d6&style=flat-square
    :target: https://github.com/dmitrvk/smth/blob/master/LICENSE
    :alt: GNU General Public License v3.0

.. |pypi| image:: https://img.shields.io/pypi/v/smth?color=0366d6&style=flat-square
    :target: https://pypi.org/project/smth
    :alt: Latest version released on PyPi

.. |python| image:: https://img.shields.io/pypi/pyversions/smth?color=0366d6&style=flat-square
    :target: https://pypi.org/project/smth
    :alt: Python version
