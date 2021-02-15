## TODO 
## 7 Name of app - date
## 8 "Information" button
## 9 nice layout - color

import tkinter as tk
import Plotter

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
        self.plotter = Plotter.Plotter() ## how they are all connected
        self._createWidgets()   
        
    def _createWidgets(self):
        ## create button frame
        self.bf = tk.Frame(self.f)
        self.bf.pack()
        
        self.vgcButton = tk.Button(self.bf, text = " VGC Games ", font = self.topFont, command = lambda: self.plotter.getDiagram("vgc"), width = 10)
        self.vgcButton.pack(side = "left", fill='x')
        
        self.ouButton = tk.Button(self.bf, text = " OU Games ", font = self.topFont, command = lambda: self.plotter.getDiagram("ou"), width = 10)
        self.ouButton.pack(side = "left", fill='x')
        
        self.cf = tk.Frame(self.f)
        self.cf.pack()
        self.canvas = tk.Canvas(self.cf, width = self.boardWidth, height = self.boardHeight)
        self.canvas.pack()

def main():
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()
    
if(__name__ == "__main__"): main()