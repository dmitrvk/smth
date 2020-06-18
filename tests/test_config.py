import logging
from unittest import mock

from pyfakefs import fake_filesystem_unittest

from smth import config


class ConfigTestCase(fake_filesystem_unittest.TestCase):
    """Test app configuration."""

    def setUp(self):
        self.setUpPyfakefs(modules_to_reload=[config])
        self.fs.create_file(str(config.Config.CONFIG_PATH))

        logging.disable()

    def test_read_existing_config(self):
        config_file_contents = '''[scanner]
            device = scanner
            delay = 3'''

        with open(str(config.Config.CONFIG_PATH), 'w') as config_file:
            config_file.write(config_file_contents)

        conf = config.Config()

        self.assertEqual(conf.scanner_device, 'scanner')
        self.assertEqual(conf.scanner_delay, 3)

    def test_read_config_error(self):
        bad_config = '''badsection]
            badconfig!'''

        with open(str(config.Config.CONFIG_PATH), 'w') as config_file:
            config_file.write(bad_config)

        self.assertRaises(config.Error, config.Config)

        # Empty config
        with open(str(config.Config.CONFIG_PATH), 'w') as config_file:
            config_file.write('')

        self.assertRaises(config.Error, config.Config)

    def test_scanner_device(self):
        config_file_contents = '''[scanner]
            device = scanner'''

        with open(str(config.Config.CONFIG_PATH), 'w') as config_file:
            config_file.write(config_file_contents)

        conf = config.Config()

        self.assertEqual(conf.scanner_device, 'scanner')

        conf.scanner_device = 'newscanner'
        self.assertEqual(conf.scanner_device, 'newscanner')

        with open(str(config.Config.CONFIG_PATH), 'r') as config_file:
            self.assertIn('device = newscanner', config_file.read())

    def test_scanner_delay(self):
        config_file_contents = '''[scanner]
            delay = 1'''

        with open(str(config.Config.CONFIG_PATH), 'w') as config_file:
            config_file.write(config_file_contents)

        conf = config.Config()

        self.assertEqual(conf.scanner_delay, 1)

        conf.scanner_delay = 3
        self.assertEqual(conf.scanner_delay, 3)

        with open(str(config.Config.CONFIG_PATH), 'r') as config_file:
            self.assertIn('delay = 3', config_file.read())

    def test_os_error_when_writing(self):
        with mock.patch('configparser.ConfigParser') as ConfigParser:
            ConfigParser.return_value = mock.MagicMock(**{
                'write.side_effect': OSError,
            })

            conf = config.Config()

            with self.assertRaises(config.Error):
                conf.scanner_device = 'device'
