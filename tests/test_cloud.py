import pathlib
from unittest import mock

from pyfakefs import fake_filesystem_unittest

from smth import cloud, config


class CloudTestCase(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs(modules_to_reload=[cloud])
        self.fs.create_dir(str(config.Config.CONFIG_PATH.parent))

        self.callback = mock.MagicMock()
        self.cloud = cloud.Cloud(self.callback)

        self.path = pathlib.Path('/test/path.pdf')

        self.gauth = mock.MagicMock()
        gauth_patcher = mock.patch('pydrive.auth.GoogleAuth')
        gauth_patcher.start().return_value = self.gauth
        self.addCleanup(gauth_patcher.stop)

        self.drive = mock.MagicMock()
        drive_patcher = mock.patch('pydrive.drive.GoogleDrive')
        drive_patcher.start().return_value = self.drive
        self.addCleanup(drive_patcher.stop)
