import sqlite3
import logging
_LOGGER = logging.getLogger(__name__)


class Database:
    def __init__(self, file):
        self._file = file

    def __enter__(self):
        self._con = sqlite3.connect(self._file)
        self._cur = self._con.cursor()
        self._cur.execute("CREATE TABLE IF NOT EXISTS telegrams (timestamp TIMESTAMP, length INT, framecounter INT, control INT, type INT, id INT, metertime TIMESTAMP, rssi REAL, lqi INT, data BLOB)")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cur.close()
        self._con.close()

    def commit(self, telegram):
        self._cur.execute("INSERT INTO telegrams (timestamp, length, framecounter, control, type, id, metertime, rssi, lqi, data) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [telegram.timestamp, telegram.length, telegram.frameCounter, telegram.control, telegram.type, telegram.id, telegram.metertime, telegram.rssi, telegram.lqi, sqlite3.Binary(telegram.data)])
        self._con.commit()