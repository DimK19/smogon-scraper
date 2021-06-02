## TODO
## 2 Name of app - date
## 1 nice layout - color

import tkinter as tk
import Scraper
import Plotter
import os.path
import json
import webbrowser

repositoryLink = "https://github.com/DimK19/SmogonScraper"

class Util(): ## how they are all connected
    def __init__(self):
        self.scrape = Scraper.Scraper()
        self.plotter = Plotter.Plotter()

    def getDiagram(self, format):
        ## format is a string (currently either "vgc", "ou", "uu", or "ubers")
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
        root.resizable(width = False, height = False) ## does not allow adjusting dimensions of window
        root.geometry("320x200")
        self.topFont = "Arial 15"
        self.f = tk.Frame(root) ## create root frame
        self.f.pack(expand = False, fill = "both") ## don't remember what this does
        self.logo = tk.PhotoImage(file = "./images/GitHub-Mark.png")
        self.util = Util()
        self._createWidgets()

    def _createWidgets(self):
        ## create button frame
        self.buttonFrame = tk.Frame(self.f)
        self.buttonFrame.pack()

        self.vgcButton = tk.Button(self.buttonFrame, text = " VGC Games ", font = self.topFont, command = lambda: self.util.getDiagram("vgc"), width = 10)
        self.vgcButton.pack(fill = 'x')

        self.ouButton = tk.Button(self.buttonFrame, text = " OU Games ", font = self.topFont, command = lambda: self.util.getDiagram("ou"), width = 10)
        self.ouButton.pack(fill = 'x')

        self.uuButton = tk.Button(self.buttonFrame, text = " UU Games ", font = self.topFont, command = lambda: self.util.getDiagram("uu"), width = 10)
        self.uuButton.pack(fill = 'x')

        self.uberButton = tk.Button(self.buttonFrame, text = " Uber Games ", font = self.topFont, command = lambda: self.util.getDiagram("ubers"), width = 10)
        self.uberButton.pack(fill = 'x')

        self.infoButton = tk.Button(self.buttonFrame, text = " Information ", font = self.topFont, command = lambda: self._showInfo(), width = 10)
        self.infoButton.pack(fill = 'x')

    def _showInfo(self):
        hs = tk.Toplevel(width = 300, height = 350)
        hs.title("    About this application    ")
        hs.geometry("310x100") # width and height above simply do not work...

        message = tk.Label(hs, text = "Data courtesy of Smogon. Link to GitHub repository:")
        message.pack()
        link = tk.Label(hs, image = self.logo, cursor = "hand2")
        link.pack()
        link.bind("<Button-1>", lambda e: webbrowser.open_new(repositoryLink))
        # bind to left click

        dismissButton = tk.Button(hs, text = "    Close    ", command = hs.destroy)
        dismissButton.pack(side = "bottom")

def main():
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()

if(__name__ == "__main__"): main()
