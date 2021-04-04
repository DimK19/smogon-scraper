## TODO 
## 7 Name of app - date
## 8 "Information" button
## 9 nice layout - color

import tkinter as tk
import Scraper
import Plotter
import os.path
import json

class Util(): ## how they are all connected
    def __init__(self):
        self.scrape = Scraper.Scraper()
        self.plotter = Plotter.Plotter() 
    
    def getDiagram(self, format):
        ## format is a string (currently either "vgc" or "ou")
        filename = format.lower() + "_smogon_data.json"
        try:
            if(os.path.isfile(filename)):
                tempo = {}
                with open(filename, 'r') as f: tempo = json.load(f)
                lastRecordedMonth = list(tempo.keys())[-1][:7]
                tempo.update(self.scrape.getData(format, lastRecordedMonth))
                with open(filename, 'w') as f: json.dump(tempo, f)
            else:
                with open(filename, 'w') as f: json.dump(self.scrape.getData(format), f)
            
            ## Finally get the latest scraped data 
            with open(filename, 'r') as f: data = json.load(f)
        except FileNotFoundError as e:
            raise(e)
        
        self.plotter.plot(data)

class GUI():
    def __init__(self, root):
        self.root = root
        root.title("Smogon Scraper Application")
        root.resizable(width = "false", height = "false") ## ??
        self.boardWidth = 320
        self.boardHeight = 200
        self.topFont = "Arial 15"
        self.f = tk.Frame(root) ## create root frame
        self.f.pack(expand = True, fill = "both") ## don't remember what this does
        self.util = Util()
        self._createWidgets()   
        
    def _createWidgets(self):
        ## create button frame
        self.buttonFrame = tk.Frame(self.f)
        self.buttonFrame.pack()
        
        self.vgcButton = tk.Button(self.buttonFrame, text = " VGC Games ", font = self.topFont, command = lambda: self.util.getDiagram("vgc"), width = 10)
        self.vgcButton.pack(side = "top", fill='x')
        
        self.ouButton = tk.Button(self.buttonFrame, text = " OU Games ", font = self.topFont, command = lambda: self.util.getDiagram("ou"), width = 10)
        self.ouButton.pack(side = "top", fill='x')
        
        self.infoButton = tk.Button(self.buttonFrame, text = " Information ", font = self.topFont, command = lambda: self._showInfo(), width = 10)
        self.infoButton.pack(side = "bottom", fill='x')
        
        self.canvasFrame = tk.Frame(self.f)
        self.canvasFrame.pack()
        self.canvas = tk.Canvas(self.canvasFrame, width = self.boardWidth, height = self.boardHeight)
        self.canvas.pack()
      
    def _showInfo(self):
        pass

def main():
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()
    
if(__name__ == "__main__"): main()
