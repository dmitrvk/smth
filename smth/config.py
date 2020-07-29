import configparser
import logging

from smth import const

log = logging.getLogger(__name__)


class Config:
    """App configuration."""

    def __init__(self):
        self.config = configparser.ConfigParser()

        # Default configuration
        self.default_config = configparser.ConfigParser()
        self.default_config['scanner'] = {}
        self.default_config['scanner']['device'] = ''
        self.default_config['scanner']['delay'] = '0'
        self.default_config['scanner']['mode'] = 'Gray'
        self.default_config['scanner']['resolution'] = '150'
        self.default_config['scanner']['ask_upload'] = 'True'

        if const.CONFIG_PATH.exists():
            try:
                self.config.read(str(const.CONFIG_PATH))
            except configparser.Error as exception:
                log.exception(exception)
                raise Error(f'Cannot load config: {exception}')

            if not self.config.sections():
                message = f"Cannot load config from '{str(const.CONFIG_PATH)}'"
                log.error(message)
                raise Error(message)

            log.debug('Loaded config from %s', {str(const.CONFIG_PATH)})
        else:
            const.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            self.config = self.default_config
            self._write_config()

            log.debug('Created default config at %s', {str(const.CONFIG_PATH)})

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
    def scanner_mode(self) -> str:
        """Gray or color. Gray if not set."""
        return self.config.get('scanner', 'mode', fallback='Gray')

    @scanner_mode.setter
    def scanner_mode(self, mode: str) -> None:
        self.config.set('scanner', 'mode', mode)
        self._write_config()

    @property
    def scanner_resolution(self) -> int:
        """Scanner resolution (PPI). Use 150 by default."""
        try:
            return self.config.getint('scanner', 'resolution', fallback=150)
        except ValueError as exception:
            raise Error(str(exception))

    @scanner_resolution.setter
    def scanner_resolution(self, resolution: int) -> None:
        self.config.set('scanner', 'resolution', str(resolution))
        self._write_config()

    @property
    def scanner_ask_upload(self) -> str:
        """Defines whether to ask for uploading to cloud when scan finishes."""
        try:
            return self.config.getboolean(
                'scanner', 'ask_upload', fallback=True)
        except ValueError as exception:
            raise Error(str(exception))

    @scanner_ask_upload.setter
    def scanner_ask_upload(self, ask_upload: bool) -> None:
        self.config.set('scanner', 'ask_upload', str(ask_upload))
        self._write_config()

    def _write_config(self):
        try:
            with open(str(const.CONFIG_PATH), 'w') as config_file:
                self.config.write(config_file)
        except (OSError, configparser.Error) as exception:
            raise Error(f'Cannot write config: {exception}')


class Error(Exception):
    pass
