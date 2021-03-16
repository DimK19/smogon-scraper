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
        self.buttonFrame = tk.Frame(self.f)
        self.buttonFrame.pack()
        
        self.vgcButton = tk.Button(self.buttonFrame, text = " VGC Games ", font = self.topFont, command = lambda: self.plotter.getDiagram("vgc"), width = 10)
        self.vgcButton.pack(side = "top", fill='x')
        
        self.ouButton = tk.Button(self.buttonFrame, text = " OU Games ", font = self.topFont, command = lambda: self.plotter.getDiagram("ou"), width = 10)
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