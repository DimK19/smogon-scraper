import requests
import re
import json
from bs4 import BeautifulSoup as BS

class SmogonScraper():
    def __init__(self):
        self.sourceURL = "https://www.smogon.com/stats/"
        self.req = requests.get(self.sourceURL)
        self.soup = BS(self.req.text, "html.parser")
        self.allLinksDict = {}
        self.vgcDict = {}
        self.allGames = {}

    def _collectAllLinks(self):
        for link in self.soup.find_all('a'):
            if(link.text == "../"): continue
            date = link.text.rstrip('/')
            monthURL = self.sourceURL + link.get("href")
            self.allLinksDict.update({date : monthURL})
        
    def _separateVGC(self):
        for d in self.allLinksDict:
            innerReq = requests.get(self.allLinksDict[d])
            innerSoup = BS(innerReq.text, "html.parser")
            for format in innerSoup.find_all('a', href = re.compile(r"^.*vgc[0-9]{4}.*-0.txt")):
                formatURL = self.allLinksDict[d] + format.text
                self.vgcDict.update({(d, format.text) : formatURL})
                
    def _readGameCount(self):
        for k in self.vgcDict:
            lastReq = requests.get(self.vgcDict[k])
            firstLine = lastReq.text.split('\n')[0]
            games = re.findall(r"[0-9]+", firstLine)
            games = int(games[0])
            self.allGames.update({k[0] + '_' + k[1][:-6] : games}) # json does not accept dictionary with tuple keys
     
    def getRawData(self):
        self._collectAllLinks()
        self._separateVGC()
        self._readGameCount()
        return self.allGames

def main():
    ss = SmogonScraper()
    ss.getRawData()
        
if(__name__ == "__main__"): main()