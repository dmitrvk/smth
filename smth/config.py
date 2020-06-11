import configparser
import logging
import pathlib

log = logging.getLogger(__name__)


class Config:
    """App configuration."""

    CONFIG_PATH = pathlib.Path('~/.config/smth/smth.conf').expanduser()

    def __init__(self):
        self.config = configparser.ConfigParser()

        # Default configuration
        self.config = configparser.ConfigParser()
        self.config['scanner'] = {}
        self.config['scanner']['device'] = ''
        self.config['scanner']['delay'] = '0'

        if self.CONFIG_PATH.exists():
            try:
                self.config.read(str(self.CONFIG_PATH))
                log.debug('Loaded config from %s', {str(self.CONFIG_PATH)})
            except configparser.Error as exception:
                log.exception(exception)
                self._write_config()
        else:
            self.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            self._write_config()

            log.debug('Created default config at %s', {str(self.CONFIG_PATH)})

    @property
    def scanner_device(self) -> str:
        """Name of the device which is used to perform scanning."""
        return self.config.get('scanner', 'device', fallback='')

    @scanner_device.setter
    def scanner_device(self, device) -> None:
        self.config.set('scanner', 'device', device)
        self._write_config()

    @property
    def scanner_delay(self) -> int:
        """Time in seconds between consecutive scans."""
        return self.config.getint('scanner', 'delay', fallback=0)

    @scanner_delay.setter
    def scanner_delay(self, delay: int) -> None:
        self.config.set('scanner', 'delay', str(delay))
        self._write_config()

    def _write_config(self):
        with open(str(self.CONFIG_PATH), 'w') as config_file:
            self.config.write(config_file)
