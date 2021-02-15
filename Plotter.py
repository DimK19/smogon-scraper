## TODO
## 1 Keep track of last update date, so thst you dont pull all the data with every refresh each time ALMOST DONE

import Scraper
import matplotlib.pyplot as plt
import json
import os.path

class Plotter():
    def __init__(self):
        self.scrape = Scraper.Scraper()
    
    ## format is a string (currently either "vgc" or "ou")
    def getDiagram(self, format):
        self.filename = format + "_smogon_data.json"
        try:
            ## this is where you should have append
            if(os.path.isfile(self.filename)):
                ## get last entry to find last recorded date
                tempo = {}
                with open(self.filename, 'r') as f: tempo = json.load(f)
                lrd = list(tempo.keys())[-1][:7]
                tempo.update(self.scrape.getRawData(format, lrd))
                with open(self.filename, 'w') as f: json.dump(tempo, f)
            else:
                with open(self.filename, 'w') as f: json.dump(self.scrape.getRawData(format), f)
            
            ## Finally get the latest scraped data
            with open(self.filename, 'r') as f: data = json.load(f)
        except FileNotFoundError as e:
            print(e)
            return

        byDateOnly  = {} # ignore different sub-formats
        for i in data:
            # i.split('_')[0][:7] this disgusting expression extracts solely the date from the key string
            if(i.split('_')[0][:7] not in byDateOnly): byDateOnly.update({i.split('_')[0][:7] : data[i]})
            else: byDateOnly[i.split('_')[0][:7]] += data[i]
            
        plt.bar(*zip(*byDateOnly.items()))
        # *zip(*dict.items()) consists of two tuples, one containing the unpacked keys of the dictionary
        # and one containing the corresponding unpacked values
        plt.xticks(rotation = 90) # Rotate horizontal axis labels by 90 degrees
        plt.tick_params(labelsize = 7) # not good
        plt.show()

## Testing
def main():
    Plotter().getDiagram("vgc")
    

if(__name__  == "__main__"): main()