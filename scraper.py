## Try-catch for requests https://stackoverflow.com/questions/16511337/correct-way-to-try-except-using-python-requests-module
## For user agent:
## https://stackoverflow.com/questions/10606133/sending-user-agent-using-requests-library-in-python
## https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent
## Older stats:
## https://www.smogon.com/forums/categories/simulator-archive.424/
## https://www.smogon.com/forums/threads/official-smogon-university-simulator-statistics-%E2%80%94-january-2013.3478571/

## TODO
## add support for other formats

import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup as BS
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from formats import isCandidate, isKnownFormat

class ScrapeError(Exception):
    pass

class Scraper():

    sourceURL = "https://www.smogon.com/stats/"
    headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"}
    timeout = (10, 30) ## seconds to connect, seconds to read
    workers = 2 ## parallel downloads, deliberately low to be polite to the site

    def __init__(self):
        self._local = threading.local()
        self._monthFiles = {} ## published months do not change, so each listing is only fetched once

    ## one reusable connection per thread, which is about 3 times faster than reconnecting for every file
    def _session(self):
        if(not hasattr(self._local, "session")):
            session = requests.Session()
            session.headers.update(Scraper.headers)
            retries = Retry(total = 3, backoff_factor = 1, status_forcelist = (429, 500, 502, 503, 504), raise_on_status = False)
            session.mount("https://", HTTPAdapter(max_retries = retries))
            self._local.session = session
        return self._local.session

    def _get(self, url):
        try:
            response = self._session().get(url, timeout = Scraper.timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ScrapeError(f"Could not download {url}: {e}") from e
        return response

    ## only plain yyyy-mm folders: the -H1, -H2 and -DLC folders are parts of a month that is already published whole
    def _getMonths(self):
        soup = BS(self._get(Scraper.sourceURL).text, "html.parser")
        return [link.get("href").rstrip('/') for link in soup.find_all('a', href = re.compile(r"^[0-9]{4}-[0-9]{2}/$"))]

    ## names of all the rating-0 files in a month, without the "-0.txt" ending
    def _getSources(self, month):
        if(month not in self._monthFiles):
            soup = BS(self._get(f"{Scraper.sourceURL}{month}/").text, "html.parser")
            self._monthFiles[month] = [link.get("href")[:-len("-0.txt")] for link in soup.find_all('a', href = re.compile(r"-0\.txt$"))]
        return self._monthFiles[month]

    ## opens the txt and reads the first line, which contains
    ## some text and a single number, the total amount of games played that month
    def _readFormatFile(self, formatURL):
        firstLine = self._get(formatURL).text.split('\n', 1)[0]
        games = re.match(r"\s*Total battles:\s*([0-9]+)", firstLine)
        if(not games):
            raise ScrapeError(f"Unexpected content in {formatURL}")
        return int(games.group(1))

    ## runs inside one worker, so the number of simultaneous requests never exceeds Scraper.workers
    def _getGameCounts(self, month, formatName):
        sources = [source for source in self._getSources(month) if isCandidate(formatName, source)]
        return {source : self._readFormatFile(f"{Scraper.sourceURL}{month}/{source}-0.txt") for source in sources}

    ## Downloads every published month not in knownMonths.
    ## onMonth(month, counts) is called as soon as a month is complete, so progress survives interruptions.
    ## Returns (data, failedMonths). A failed month is not saved, so it is tried again next time.
    def getData(self, formatName, knownMonths = (), onMonth = None, onProgress = None):
        if(not isKnownFormat(formatName)):
            raise ValueError(f"Invalid format: {formatName}")

        months = [month for month in self._getMonths() if month not in knownMonths]
        data, failedMonths = {}, []
        with ThreadPoolExecutor(max_workers = Scraper.workers) as pool:
            futures = {pool.submit(self._getGameCounts, month, formatName) : month for month in months}
            try:
                for done, future in enumerate(as_completed(futures), start = 1):
                    month = futures[future]
                    try:
                        data[month] = future.result()
                    except ScrapeError:
                        failedMonths.append(month)
                    else:
                        if(onMonth):
                            onMonth(month, data[month])
                    if(onProgress):
                        onProgress(done, len(months), month)
            except BaseException:
                ## e.g. the disk is full: stop instead of downloading months that cannot be saved
                for future in futures:
                    future.cancel()
                raise
        return dict(sorted(data.items())), sorted(failedMonths)


## For testing purposes
def main():
    data, failedMonths = Scraper().getData("bdspdoubles")
    print(data)
    print("Failed months:", failedMonths)

if(__name__ == "__main__"): main()
