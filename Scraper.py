## Try-catch for requests https://stackoverflow.com/questions/16511337/correct-way-to-try-except-using-python-requests-module
## For user agent:
## https://stackoverflow.com/questions/10606133/sending-user-agent-using-requests-library-in-python
## https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent

## TODO
## add ubers, uu, dou
## 2017-01 pre-bank and post-bank ou

import requests
import re
import json
from bs4 import BeautifulSoup as BS
import datetime

class Scraper():

    sourceURL = "https://www.smogon.com/stats/"
    headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"}

    def __init__(self):             
        try:
            req = requests.get(Scraper.sourceURL, headers = Scraper.headers)
        except requests.exceptions.RequestException as e: 
            raise SystemExit(e)
        self.soup = BS(req.text, "html.parser")
        self.allGames = {}

    def _collectAllLinks(self, format, lastRecordedDate = None):
        self.allGames.clear()
        startDate = None
        ## lrd is in the format "YYYY-MM"
        ## "calculate" next month:
        if(lastRecordedDate):
            if(lastRecordedDate[-2:] == "12"): ## if last month is December
                startDate = str(int(lastRecordedDate[:4]) + 1) + "-01"
            else: startDate = lastRecordedDate[:5] + str(int(lastRecordedDate[-2:]) + 1)
        
        for link in self.soup.find_all('a'):
            if(link.text == "../" or link.text[7] != '/'): continue
            # prevents double counting of some months that are divided in halves
            month = link.text.rstrip('/') # remove trailing '/'
            
            if(startDate):
                if(datetime.datetime.strptime(month, "%Y-%m").date() < datetime.datetime.strptime(startDate, "%Y-%m").date()): continue
                ## reduces the amount of times that getGameCount is called, thus reducing requests
                
            monthURL = Scraper.sourceURL + link.get("href")
            gamesPlayed = self._getGameCount(monthURL, format)
            self.allGames.update({month : gamesPlayed})
            ## print(month, ' ', gamesPlayed) # debug
           
    ## for each month link, selects the pre-determined format
    def _getGameCount(self, monthURL, format):
        regex = ""
        ans = 0
        if(format == "vgc"): regex = r"^.*vgc[0-9]{4}.*-0.txt$|^(.*)battle(spot|stadium)doubles(.*)-0.txt$"
        ## the regular expression matches with all vgc formats by smogon naming convention, and all "battlespot/stadiumdoubles".
        ## Notice that there must not be whitespace around the disjunction operator (or any other)
        elif(format == "ou" or format == "uu" or format == "ubers"): regex = r"^(gen[0-9]*)*" + format + ".*-0.txt"
        # this one matches with all ou / uu / uber formats by smogon naming convention
        
        try:
            innerReq = requests.get(monthURL, headers = Scraper.headers)
        except requests.exceptions.RequestException as e: 
            raise SystemExit(e)
        
        innerSoup = BS(innerReq.text, "html.parser")
        for format in innerSoup.find_all('a', href = re.compile(regex)):
            formatURL = monthURL + format.text
            ans += self._readFormatFile(formatURL)       
        
        return ans
        
    ## opens the txt and reads the first line, which contains 
    ## some text and a single number, the total amount of games played that month
    def _readFormatFile(self, formatURL):       
        try:
            lastReq = requests.get(formatURL, headers = Scraper.headers)
        except requests.exceptions.RequestException as e: 
            raise SystemExit(e)
        firstLine = lastReq.text.split('\n')[0]
        games = re.findall(r"[0-9]+", firstLine) ## only accept numbers
        games = int(games[0])
        return games
     
    def getData(self, format, lastRecordedDate = None):   
        if(format.lower() not in ["vgc", "ou", "uu", "ubers"]):
            print("Error: Invalid format")
            return
        
        self._collectAllLinks(format, lastRecordedDate)
        return self.allGames
        

# For testing purposes
def main():
    scrape = Scraper()
    # with open("test.txt", 'w') as f: json.dump(scrape.getData("ou", "2020-11"), f) 
    with open("test2.txt", 'w') as f: json.dump(scrape.getData("vgc"), f) 
        
if(__name__ == "__main__"): main()
