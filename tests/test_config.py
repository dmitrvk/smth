import logging
from unittest import mock

from pyfakefs import fake_filesystem_unittest

from smth import config, const


class ConfigTestCase(fake_filesystem_unittest.TestCase):
    """Test app configuration."""

    def setUp(self):
        self.setUpPyfakefs(modules_to_reload=[config, const])
        self.fs.create_file(str(const.CONFIG_PATH))

        logging.disable()

    def test_read_existing_config(self):
        config_file_contents = '''[scanner]
            device = scanner
            delay = 3'''

        with open(str(const.CONFIG_PATH), 'w') as config_file:
            config_file.write(config_file_contents)

        conf = config.Config()

        self.assertEqual(conf.scanner_device, 'scanner')
        self.assertEqual(conf.scanner_delay, 3)

    def test_read_config_error(self):
        bad_config = '''badsection]
            badconfig!'''

        with open(str(const.CONFIG_PATH), 'w') as config_file:
            config_file.write(bad_config)

        self.assertRaises(config.Error, config.Config)

        # Empty config
        with open(str(const.CONFIG_PATH), 'w') as config_file:
            config_file.write('')

        self.assertRaises(config.Error, config.Config)

    def test_scanner_device(self):
        config_file_contents = '''[scanner]
            device = scanner'''

        with open(str(const.CONFIG_PATH), 'w') as config_file:
            config_file.write(config_file_contents)

        conf = config.Config()

        self.assertEqual(conf.scanner_device, 'scanner')

        conf.scanner_device = 'newscanner'
        self.assertEqual(conf.scanner_device, 'newscanner')

        with open(str(const.CONFIG_PATH), 'r') as config_file:
            self.assertIn('device = newscanner', config_file.read())

    def test_scanner_delay(self):
        config_file_contents = '''[scanner]
            delay = 1'''

        with open(str(const.CONFIG_PATH), 'w') as config_file:
            config_file.write(config_file_contents)

        conf = config.Config()

        self.assertEqual(conf.scanner_delay, 1)

        conf.scanner_delay = 3
        self.assertEqual(conf.scanner_delay, 3)

        with open(str(const.CONFIG_PATH), 'r') as config_file:
            self.assertIn('delay = 3', config_file.read())

    def test_scanner_resolution(self):
        config_file_contents = '''[scanner]
            resolution = 150'''

        with open(str(const.CONFIG_PATH), 'w') as config_file:
            config_file.write(config_file_contents)

        conf = config.Config()

        self.assertEqual(conf.scanner_resolution, 150)

        conf.scanner_resolution = 300
        self.assertEqual(conf.scanner_resolution, 300)

        with open(str(const.CONFIG_PATH), 'r') as config_file:
            self.assertIn('resolution = 300', config_file.read())

    def test_scanner_mode(self):
        config_file_contents = '''[scanner]
            mode = Gray'''

        with open(str(const.CONFIG_PATH), 'w') as config_file:
            config_file.write(config_file_contents)

        conf = config.Config()

        self.assertEqual(conf.scanner_mode, 'Gray')

        conf.scanner_mode = 'Color'
        self.assertEqual(conf.scanner_mode, 'Color')

        with open(str(const.CONFIG_PATH), 'r') as config_file:
            self.assertIn('mode = Color', config_file.read())

    def test_scanner_ask_upload(self):
        config_file_contents = '''[scanner]
            ask_upload = True'''

        with open(str(const.CONFIG_PATH), 'w') as config_file:
            config_file.write(config_file_contents)

        conf = config.Config()

        self.assertEqual(conf.scanner_ask_upload, True)

        conf.scanner_ask_upload = False
        self.assertEqual(conf.scanner_ask_upload, False)

        with open(str(const.CONFIG_PATH), 'r') as config_file:
            self.assertIn('ask_upload = False', config_file.read())

    def test_os_error_when_writing(self):
        with mock.patch('configparser.ConfigParser') as ConfigParser:
            ConfigParser.return_value = mock.MagicMock(**{
                'write.side_effect': OSError,
            })

            conf = config.Config()

            with self.assertRaises(config.Error):
                conf.scanner_device = 'device'
