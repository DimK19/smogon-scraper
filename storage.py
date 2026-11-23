## SQLite storage, plus a JSON export that can be moved to another computer and imported again.

import datetime
import json
import os
import re
import sqlite3
from contextlib import contextmanager

from formats import isKnownFormat

EXPORT_SCHEMA = 1
_MONTH = re.compile(r"^[0-9]{4}-(0[1-9]|1[0-2])$")

class Storage():
    def __init__(self, path):
        self.path = str(path)
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS battles (
                    format TEXT NOT NULL,
                    month TEXT NOT NULL,
                    source TEXT NOT NULL,
                    battles INTEGER NOT NULL CHECK (battles >= 0),
                    PRIMARY KEY (format, month, source)
                ) WITHOUT ROWID;
                CREATE TABLE IF NOT EXISTS scraped_months (
                    format TEXT NOT NULL,
                    month TEXT NOT NULL,
                    PRIMARY KEY (format, month)
                ) WITHOUT ROWID;
            """)

    ## a new connection per use keeps this safe to call from the scraping thread
    @contextmanager
    def _connect(self):
        db = sqlite3.connect(self.path)
        try:
            with db:
                yield db
        finally:
            db.close()

    def scrapedMonths(self, formatName):
        with self._connect() as db:
            rows = db.execute("SELECT month FROM scraped_months WHERE format = ?", (formatName,))
            return {month for (month,) in rows}

    ## a month is saved whole or not at all, so an interrupted scrape resumes from the next missing month
    def saveMonth(self, formatName, month, counts):
        with self._connect() as db:
            self._writeMonth(db, formatName, month, counts)

    @staticmethod
    def _writeMonth(db, formatName, month, counts):
        db.execute("DELETE FROM battles WHERE format = ? AND month = ?", (formatName, month))
        db.executemany(
            "INSERT INTO battles (format, month, source, battles) VALUES (?, ?, ?, ?)",
            [(formatName, month, source, battles) for source, battles in counts.items()]
        )
        db.execute("INSERT OR IGNORE INTO scraped_months (format, month) VALUES (?, ?)", (formatName, month))

    def getRows(self, formatName):
        with self._connect() as db:
            return db.execute(
                "SELECT month, source, battles FROM battles WHERE format = ? ORDER BY month, source",
                (formatName,)
            ).fetchall()

    def exportJson(self, path):
        formats = {}
        with self._connect() as db:
            for formatName, month in db.execute("SELECT format, month FROM scraped_months ORDER BY format, month"):
                formats.setdefault(formatName, {})[month] = {}
            for formatName, month, source, battles in db.execute("SELECT format, month, source, battles FROM battles ORDER BY format, month, source"):
                formats[formatName][month][source] = battles

        document = {
            "schema" : EXPORT_SCHEMA,
            "source" : "https://www.smogon.com/stats/",
            "exportedAt" : datetime.datetime.now(datetime.timezone.utc).isoformat(timespec = "seconds"),
            "formats" : formats,
        }
        ## write to a temporary file first so a failed export never damages an existing one
        temporary = str(path) + ".tmp"
        with open(temporary, 'w', encoding = "utf-8") as f:
            json.dump(document, f, indent = 1)
        os.replace(temporary, path)
        return sum(len(months) for months in formats.values())

    def importJson(self, path):
        formats = readExport(path)
        with self._connect() as db:
            for formatName, months in formats.items():
                for month, counts in months.items():
                    self._writeMonth(db, formatName, month, counts)
        return sum(len(months) for months in formats.values())

## Reads and validates an exported file. Returns {format : {month : {source : battles}}}
def readExport(path):
    with open(path, 'r', encoding = "utf-8") as f:
        document = json.load(f)
    if(not isExport(document)):
        raise ValueError("This is not a Smogon Scraper export file.")

    for formatName, months in document["formats"].items():
        if(not isKnownFormat(formatName) or not isinstance(months, dict)):
            raise ValueError(f"Unknown format in export: {formatName}")
        for month, counts in months.items():
            if(not _MONTH.match(month) or not isinstance(counts, dict)):
                raise ValueError(f"Invalid month in export: {month}")
            for source, battles in counts.items():
                if(type(battles) is not int or battles < 0):
                    raise ValueError(f"Invalid battle count for {source} in {month}")
    return document["formats"]

def isExport(document):
    return (
        isinstance(document, dict)
        and document.get("schema") == EXPORT_SCHEMA
        and isinstance(document.get("formats"), dict)
    )
