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

        # Provide two possible values for each parameter
        self.conf = {
            'device': ('scanner', 'new_scanner'),
            'delay': (1, 3),
            'resolution': (150, 300),
            'mode': ('Gray', 'Color'),
            'ask_upload': (True, False),
        }

    def test_read_scanner_config(self):
        for param in self.conf:
            value = self.conf[param][0]

            file_contents = f'[scanner]\n {param} = {value}'
            self._write_config_file(file_contents)

            conf = config.Config()

            self.assertEqual(getattr(conf, f'scanner_{param}'), value)

    def test_write_scanner_config(self):
        for param in self.conf:
            value = self.conf[param][0]
            new_value = self.conf[param][1]

            file_contents = f'[scanner]\n {param} = {value}'
            self._write_config_file(file_contents)

            conf = config.Config()
            setattr(conf, f'scanner_{param}', new_value)

            self._assert_config_file_contains(f'{param} = {new_value}')

    def test_scanner_config_value_error(self):
        wrong_conf = {
            'resolution': 'not integer',
            'ask_upload': 'not boolean',
        }

        for param in wrong_conf:
            value = wrong_conf[param][0]

            file_contents = f'[scanner]\n {param} = {value}'
            self._write_config_file(file_contents)

            conf = config.Config()

            with self.assertRaises(config.Error):
                getattr(conf, f'scanner_{param}')

    def test_read_empty_config(self):
        with open(str(const.CONFIG_PATH), 'w') as config_file:
            config_file.write('')

        self.assertRaises(config.Error, config.Config)

    def test_read_bad_config(self):
        bad_config = '''badsection]
            badconfig!'''

        with open(str(const.CONFIG_PATH), 'w') as config_file:
            config_file.write(bad_config)

        self.assertRaises(config.Error, config.Config)

    def test_os_error_when_writing(self):
        with mock.patch('configparser.ConfigParser') as parser_class:
            parser_class.return_value = mock.MagicMock(**{
                'write.side_effect': OSError,
            })

            conf = config.Config()

            with self.assertRaises(config.Error):
                conf.scanner_device = 'device'

    def _write_config_file(self, file_contents: str) -> None:  # pylint: disable=no-self-use  # noqa: E501
        with open(str(const.CONFIG_PATH), 'w') as config_file:
            config_file.write(file_contents)

    def _assert_config_file_contains(self, string: str) -> None:
        with open(str(const.CONFIG_PATH), 'r') as config_file:
            self.assertIn(string, config_file.read())
