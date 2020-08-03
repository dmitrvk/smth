# License: GNU GPL Version 3

"""The package provides Cloud class to interact with Google Drive.

PDF files can be uploaded to Google Drive and shared via a link.

Cloud object provides two callbacks for uploading and sharing files
correspondingly.  Both are used to subscribe to Cloud's events."""

from .callback import Callback, SharingCallback, UploadingCallback
from .cloud import Cloud

__all__ = ['Callback', 'Cloud', 'UploadingCallback', 'SharingCallback']
