## TODO 
## Flush dictionaries after use
## Keys have not been chosen very wisely

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
        self.formatDict = {}
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
                # the regular expression matches with all vgc formats by smogon naming convention
                formatURL = self.allLinksDict[d] + format.text
                self.formatDict.update({(d, format.text) : formatURL})
                
    def _separateOU(self):
        for d in self.allLinksDict:
            innerReq = requests.get(self.allLinksDict[d])
            innerSoup = BS(innerReq.text, "html.parser")
            for format in innerSoup.find_all('a', href = re.compile(r"^(gen[0-9]*)*ou.*-0.txt")):
                # the regular expression matches with all ou formats by smogon naming convention
                formatURL = self.allLinksDict[d] + format.text
                self.formatDict.update({(d, format.text) : formatURL})       
                
    def _readGameCount(self):
        for k in self.formatDict:
            lastReq = requests.get(self.formatDict[k])
            firstLine = lastReq.text.split('\n')[0]
            games = re.findall(r"[0-9]+", firstLine)
            games = int(games[0])
            self.allGames.update({k[0] + '_' + k[1][:-6] : games}) # json does not accept dictionary with tuple keys
     
    def getRawData(self, format):
        self._collectAllLinks()
        if(format.lower() == "vgc"): self._separateVGC()
        elif(format.lower() == "ou"): self._separateOU()
        else:
            print("Error: Invalid format")
            return
        self._readGameCount()
        return self.allGames
        

# For testing purposes
def main():
    ss = SmogonScraper()
    with open("test.txt", 'w') as f: json.dump(ss.getRawData("ou"), f) 
        
if(__name__ == "__main__"): main()