## TODO 
## 2 Flush dictionaries after use
## 4 Keys have not been chosen very wisely
## 5 Battle spot / stadium doubles format
## 3 Try-catch for files and internet access https://stackoverflow.com/questions/16511337/correct-way-to-try-except-using-python-requests-module
## 6 https://stackoverflow.com/questions/10606133/sending-user-agent-using-requests-library-in-python

import requests
import re
import json
from bs4 import BeautifulSoup as BS

class Scraper():

    sourceURL = "https://www.smogon.com/stats/"

    def __init__(self):     
        self.req = requests.get(Scraper.sourceURL)
        self.soup = BS(self.req.text, "html.parser")
        self.allLinksDict = {}
        self.formatDict = {}
        self.allGames = {}

    ## after this method returns, allLinksDict contains the links for all the previously unrecorded months
    def _collectAllLinks(self, lastRecordedDate = None):
        startDate = None
        ## lrd is in the format "YYYY-MM"
        ## "calculate" next month:
        if(lastRecordedDate):
            if(lastRecordedDate[-2:] == "12"): ## if last month is December
                startDate = str(int(lastRecordedDate[:4]) + 1) + "-01"
            else: startDate = lastRecordedDate[:5] + str(int(lastRecordedDate[-2:]) + 1)
       
        found = False ## eewww
        for link in self.soup.find_all('a'):
            if(link.text == "../"): continue
            flag = True ## eeeeeeewwwww
            if(startDate and not found):
                if(link.text != startDate + '/'):
                    flag = False
            if(not flag): continue
            if(link.text[-3] == 'H'): continue ## very dumb, prevents double counting of some months that are divided in halves
            found = True
            date = link.text.rstrip('/')
            monthURL = self.sourceURL + link.get("href")
            self.allLinksDict.update({date : monthURL})
        
    ## for each month, get the links for the vgc formats only    
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
    
    ## for each format link, opens the txt and reads the first line, which contains 
    ## some text and a single number, the total amount of games played that month
    def _readGameCount(self):
        for k in self.formatDict:
            lastReq = requests.get(self.formatDict[k])
            firstLine = lastReq.text.split('\n')[0]
            games = re.findall(r"[0-9]+", firstLine)
            games = int(games[0])
            self.allGames.update({k[0] + '_' + k[1][:-6] : games}) # json does not accept dictionary with tuple keys
     
    def getRawData(self, format, lastRecordedDate = None):
        self._collectAllLinks(lastRecordedDate)
        if(format.lower() == "vgc"): self._separateVGC()
        elif(format.lower() == "ou"): self._separateOU()
        else:
            print("Error: Invalid format")
            return
        self._readGameCount()
                
        return self.allGames
        

# For testing purposes
def main():
    scrape = Scraper()
    with open("test.txt", 'w') as f: json.dump(scrape.getRawData("ou", "2020-11"), f) 
        
if(__name__ == "__main__"): main()