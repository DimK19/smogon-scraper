## TODO
## 2 Name of app - date
## 1 nice layout - color

import queue
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox

from formats import GUI_FORMATS, formatTitle
from plotter import Plotter
from scraper import Scraper, ScrapeError
from storage import Storage

repositoryLink = "https://github.com/DimK19/smogon-scraper"
BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "smogon_data.db"

class Util(): ## how they are all connected
    def __init__(self, databasePath = DATABASE):
        self.storage = Storage(databasePath)
        self.scrape = Scraper()
        self.plotter = Plotter()

    ## downloads only the months missing from the database, and saves each one as soon as it is complete
    def updateFormat(self, formatName, onProgress = None):
        known = self.storage.scrapedMonths(formatName)
        save = lambda month, counts: self.storage.saveMonth(formatName, month, counts)
        _, failedMonths = self.scrape.getData(formatName, known, save, onProgress)
        return failedMonths

    def getDiagram(self, formatName):
        return self.plotter.fromDatabase(self.storage, formatName)

class GUI():
    def __init__(self, root):
        self.root = root
        root.title("Smogon Scraper")
        root.resizable(width = False, height = False) ## does not allow adjusting dimensions of window
        self.topFont = "Arial 15"
        self.f = tk.Frame(root, padx = 12, pady = 10) ## create root frame
        self.f.pack(expand = False, fill = "both")
        self.logo = tk.PhotoImage(file = str(BASE_DIR / "images" / "GitHub-Mark.png"))
        self.util = Util()
        self.events = queue.Queue() ## the only way the background thread talks to the window
        self.actionButtons = []
        self._createWidgets()
        self.root.after(100, self._pollEvents)

    def _createWidgets(self):
        ## create button frame
        self.buttonFrame = tk.Frame(self.f)
        self.buttonFrame.pack()

        for formatName in GUI_FORMATS:
            self._addButton(f" {formatTitle(formatName)} Games ", lambda name = formatName: self._showFormat(name))
        self._addButton(" Plot JSON ", self._plotJson)
        self._addButton(" Export JSON ", self._exportJson)
        self._addButton(" Import JSON ", self._importJson)

        self.infoButton = tk.Button(self.buttonFrame, text = " Information ", font = self.topFont, command = self._showInfo, width = 12)
        self.infoButton.pack(fill = 'x')

        self.status = tk.Label(self.f, text = "Ready", wraplength = 240, fg = "#52514e")
        self.status.pack(pady = (8, 0))

    def _addButton(self, text, command):
        button = tk.Button(self.buttonFrame, text = text, font = self.topFont, command = command, width = 12)
        button.pack(fill = 'x')
        self.actionButtons.append(button)

    def _setBusy(self, isBusy):
        for button in self.actionButtons:
            button.config(state = "disabled" if isBusy else "normal")

    ## runs slow work without freezing the window. onDone(result, error) runs back on the main thread.
    def _runInBackground(self, work, onDone):
        self._setBusy(True)
        def runner():
            try:
                self.events.put(("done", onDone, work(), None))
            except Exception as e:
                self.events.put(("done", onDone, None, e))
        threading.Thread(target = runner, daemon = True).start()

    def _pollEvents(self):
        try:
            while(True):
                event = self.events.get_nowait()
                if(event[0] == "status"):
                    self.status.config(text = event[1])
                else:
                    _, onDone, result, error = event
                    self._setBusy(False)
                    onDone(result, error)
        except queue.Empty:
            pass
        self.root.after(100, self._pollEvents)

    def _showFormat(self, formatName):
        title = formatTitle(formatName)
        self.status.config(text = f"Checking for new {title} data...")

        def progress(done, total, month):
            self.events.put(("status", f"{title}: {done} of {total} months downloaded"))

        def finished(failedMonths, error):
            ## stored data is still shown when the site cannot be reached
            if(error is not None and not isinstance(error, ScrapeError)):
                self._showError(error)
                return
            if(error is not None):
                messagebox.showwarning("Could not update", f"Showing saved data only.\n\n{error}")
            elif(failedMonths):
                messagebox.showwarning("Some months failed", f"These will be tried again next time: {', '.join(failedMonths)}")
            self._openDiagram(lambda: self.util.getDiagram(formatName), title)

        self._runInBackground(lambda: self.util.updateFormat(formatName, progress), finished)

    def _openDiagram(self, buildFigure, title):
        try:
            self.util.plotter.show(buildFigure(), self.root, f"{title} battles")
            self.status.config(text = "Ready")
        except (ValueError, OSError) as e:
            self._showError(e)

    def _showError(self, error):
        self.status.config(text = "Ready")
        messagebox.showerror("Error", str(error))

    def _plotJson(self):
        path = filedialog.askopenfilename(title = "Plot a JSON file", filetypes = [("JSON files", "*.json")])
        if(not path):
            return
        try:
            names = list(self.util.plotter.loadJson(path))
        except (ValueError, OSError) as e:
            self._showError(e)
            return
        if(not names):
            self._showError(ValueError("This file contains no data to plot."))
        elif(len(names) == 1):
            self._openDiagram(lambda: self.util.plotter.fromJson(path, names[0]), formatTitle(names[0]))
        else:
            self._chooseFormat(path, names)

    ## an export can hold several formats, so ask which one to plot
    def _chooseFormat(self, path, names):
        chooser = tk.Toplevel(self.root, padx = 16, pady = 12)
        chooser.title("Choose a format")
        tk.Label(chooser, text = "Format to plot:").pack(pady = (0, 6))
        for name in names:
            def choose(selected = name):
                chooser.destroy()
                self._openDiagram(lambda: self.util.plotter.fromJson(path, selected), formatTitle(selected))
            tk.Button(chooser, text = formatTitle(name), width = 14, command = choose).pack(fill = 'x')

    def _exportJson(self):
        path = filedialog.asksaveasfilename(title = "Export data", defaultextension = ".json", initialfile = "smogon_data_export.json", filetypes = [("JSON files", "*.json")])
        if(not path):
            return
        def finished(count, error):
            if(error is not None):
                self._showError(error)
            else:
                self.status.config(text = f"Exported {count} format-months")
        self._runInBackground(lambda: self.util.storage.exportJson(path), finished)

    def _importJson(self):
        path = filedialog.askopenfilename(title = "Import an export file", filetypes = [("JSON files", "*.json")])
        if(not path):
            return
        def finished(count, error):
            if(error is not None):
                self._showError(error)
            else:
                self.status.config(text = f"Imported {count} format-months")
        self._runInBackground(lambda: self.util.storage.importJson(path), finished)

    def _showInfo(self):
        hs = tk.Toplevel(width = 220, height = 180)
        hs.title("About this program")
        hs.geometry("280x150") # width and height above simply do not work...

        message = tk.Label(hs, text = "Data courtesy of Pokemon Showdown and Smogon. Link to GitHub repository:", wraplength = 200)
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
