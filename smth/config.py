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
        self.default_config = configparser.ConfigParser()
        self.default_config['scanner'] = {}
        self.default_config['scanner']['device'] = ''
        self.default_config['scanner']['delay'] = '0'
        self.default_config['scanner']['format'] = 'jpeg'
        self.default_config['scanner']['mode'] = 'gray'
        self.default_config['scanner']['resolution'] = '150'

        if self.CONFIG_PATH.exists():
            try:
                self.config.read(str(self.CONFIG_PATH))
            except configparser.Error as exception:
                log.exception(exception)
                raise Error(f'Cannot load config: {exception}')

            if not self.config.sections():
                message = f"Cannot load config from '{str(self.CONFIG_PATH)}'"
                log.error(message)
                raise Error(message)

            log.debug('Loaded config from %s', {str(self.CONFIG_PATH)})
        else:
            self.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            self.config = self.default_config
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

    @property
    def scanner_format(self) -> str:
        """File format of scanner's output images. Use JPEG by default."""
        return self.config.get('scanner', 'format', fallback='jpeg')

    @scanner_format.setter
    def scanner_format(self, format: str) -> None:
        self.config.set('scanner', 'format', str(format))
        self._write_config()

    @property
    def scanner_mode(self) -> str:
        """Gray or color. Gray if not set."""
        return self.config.get('scanner', 'mode', fallback='gray')

    @scanner_mode.setter
    def scanner_mode(self, mode: str) -> None:
        self.config.set('scanner', 'mode', mode.lower())
        self._write_config()

    @property
    def scanner_resolution(self) -> int:
        """Scanner resolution (PPI). Use 150 by default."""
        return self.config.getint('scanner', 'resolution', fallback=150)

    @scanner_resolution.setter
    def scanner_resolution(self, resolution: int) -> None:
        self.config.set('scanner', 'resolution', str(resolution))
        self._write_config()

    def _write_config(self):
        try:
            with open(str(self.CONFIG_PATH), 'w') as config_file:
                self.config.write(config_file)
        except (OSError, configparser.Error) as exception:
            raise Error(f'Cannot write config: {exception}')


class Error(Exception):
    pass
