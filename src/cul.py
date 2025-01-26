import io, os, sys
from src.redac import Telegram
import logging
_LOGGER = logging.getLogger(__name__)


class CulDevice:
    def __init__(self, device):
        self._device = device

    def __enter__(self):
        self._tty = io.TextIOWrapper(
            io.FileIO(
                os.open(
                    self._device,
                    os.O_NOCTTY | os.O_RDWR),
                "r+")
            )
        self._tty.write("X21\n\r")
        self._tty.flush()
        self._tty.write("rrr\n\r")
        self._tty.flush()
        self.mode = self._tty.readline().strip()
        _LOGGER.info(f"Switched to: {self.mode}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._tty.write("rrx\n\r")
        self._tty.flush()
        self._tty.close()

    def receiveMessages(self):
        for line in iter(self._tty.readline, None):
            line = line.strip()
            if len(line) > 0 and line[0] == 'r':
                data = bytes.fromhex(line[1:])
                yield Telegram.TelegramFactory(data)