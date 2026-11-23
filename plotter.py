import bisect
import json
import math
import statistics
import sys
from datetime import date
from pathlib import Path

from matplotlib.colors import to_rgba
from matplotlib.dates import DateFormatter, YearLocator, date2num
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from numpy.polynomial import Chebyshev

from formats import formatTitle, groupSeries
from storage import isExport, readExport

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
COLORS = ("#2a78d6", "#1baf7a") ## one per chart line, always in this order
POLYNOMIAL_COLOR = "#eb6834"
POLYNOMIAL_DASH = (0, (6, 4))
MARKERS = ('o', '^') ## so the lines do not depend on colour alone
TREND_WINDOW = 7
POLYNOMIAL_DEGREE = 9

## All calendar months between the first and last, so a missing month shows as a gap rather than being skipped
def monthRange(series):
    present = sorted({month for byMonth in series.values() for month in byMonth})
    year, month = map(int, present[0].split('-'))
    months = []
    while(f"{year}-{month:02d}" <= present[-1]):
        months.append(f"{year}-{month:02d}")
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return months

## Centred median, drawn on top of the real monthly points. The points keep every release spike.
def rollingMedian(values, window = TREND_WINDOW):
    half = window // 2
    trend = []
    for i, value in enumerate(values):
        nearby = [v for v in values[max(0, i - half) : i + half + 1] if v is not None]
        trend.append(None if value is None else statistics.median(nearby))
    return trend

## Least-squares polynomial through the known months. It is only drawn where the series has data,
## and very short series get a lower degree so the curve does not swing wildly.
def polynomialTrend(values, degree = POLYNOMIAL_DEGREE):
    known = [i for i, value in enumerate(values) if value is not None]
    if(len(known) < 2):
        return [None] * len(values)
    curve = Chebyshev.fit(known, [values[i] for i in known], min(degree, max(len(known) // 4, 1)))
    return [max(0.0, float(curve(i))) if known[0] <= i <= known[-1] else None for i in range(len(values))]

def compactNumber(value, _position = None):
    if(value >= 1_000_000):
        return f"{value / 1_000_000:.1f}".rstrip('0').rstrip('.') + 'M'
    if(value >= 1_000):
        return f"{value / 1_000:.0f}K"
    return f"{value:.0f}"

def _withGaps(values):
    return [math.nan if v is None else v for v in values]

class Plotter():
    def fromDatabase(self, storage, formatName):
        return self.build(groupSeries(formatName, storage.getRows(formatName)), formatTitle(formatName))

    ## Returns {name : series}. Accepts exports from this program and the older {month : battles} files.
    def loadJson(self, path):
        with open(path, 'r', encoding = "utf-8") as f:
            document = json.load(f)
        if(isExport(document)):
            result = {}
            for formatName, months in readExport(path).items():
                rows = [(month, source, battles) for month, counts in months.items() for source, battles in counts.items()]
                series = groupSeries(formatName, rows)
                if(series):
                    result[formatName] = series
            return result
        if(isinstance(document, dict) and document and all(type(v) is int for v in document.values())):
            name = Path(path).stem.replace("_smogon_data", "")
            return {name : {"All ladders" : document}}
        raise ValueError("This file does not contain Smogon Scraper data.")

    def fromJson(self, path, name = None):
        loaded = self.loadJson(path)
        if(not loaded):
            raise ValueError("This file contains no data to plot.")
        name = name or next(iter(loaded))
        return self.build(loaded[name], formatTitle(name))

    ## series is {lineName : {month : battles}}. Returns a Figure that is not tied to any window.
    def build(self, series, title):
        if(not series):
            raise ValueError(f"No data to plot for {title}.")

        months = monthRange(series)
        x = [date(int(m[:4]), int(m[5:]), 1) for m in months]
        figure = Figure(figsize = (11, 6), dpi = 100, facecolor = SURFACE, layout = "constrained")
        axes = figure.add_subplot(facecolor = SURFACE)
        isSingleLine = len(series) == 1
        lines, handles, labels = [], [], []

        for i, (name, byMonth) in enumerate(series.items()):
            values = [byMonth.get(month) for month in months]
            trend = rollingMedian(values)
            curve = polynomialTrend(values)
            lines.append((name, values, trend, curve))
            dotColor = MUTED if isSingleLine else COLORS[i]
            ## the real monthly values, including release spikes
            axes.plot(
                x, _withGaps(values), color = to_rgba(dotColor, 0.35), linewidth = 1,
                marker = MARKERS[i], markersize = 3.5, markerfacecolor = to_rgba(dotColor, 0.8),
                markeredgecolor = "none", zorder = 2
            )
            axes.plot(x, _withGaps(curve), color = POLYNOMIAL_COLOR, linewidth = 2, linestyle = POLYNOMIAL_DASH, zorder = 3)
            axes.plot(x, _withGaps(trend), color = COLORS[i], linewidth = 2, solid_capstyle = "round", solid_joinstyle = "round", zorder = 4)
            if(isSingleLine):
                handles += [
                    Line2D([], [], color = to_rgba(MUTED, 0.35), marker = 'o', markerfacecolor = MUTED, markeredgecolor = "none", markersize = 5),
                    Line2D([], [], color = COLORS[i], linewidth = 2),
                ]
                labels += [f"{name}, monthly", f"{TREND_WINDOW}-month median"]
            else:
                handles.append(Line2D([], [], color = COLORS[i], linewidth = 2, marker = MARKERS[i], markersize = 5, markeredgecolor = "none"))
                labels.append(name)

        handles.append(Line2D([], [], color = POLYNOMIAL_COLOR, linewidth = 2, linestyle = POLYNOMIAL_DASH))
        labels.append("Polynomial trend")

        axes.set_title(f"{title} battles per month", loc = "left", fontsize = 15, color = INK, pad = 26)
        axes.text(0, 1.015, f"Dots are monthly battles, solid lines are the {TREND_WINDOW}-month median, dashed lines are a polynomial fit", transform = axes.transAxes, fontsize = 10, color = SECONDARY)
        axes.legend(handles, labels, loc = "upper left", frameon = False, fontsize = 10, labelcolor = SECONDARY, ncols = 3)

        axes.set_ylim(bottom = 0)
        axes.margins(x = 0.01)
        axes.yaxis.set_major_formatter(FuncFormatter(compactNumber))
        axes.xaxis.set_major_locator(YearLocator(base = 1 if len(months) <= 72 else 2))
        axes.xaxis.set_major_formatter(DateFormatter("%Y"))
        axes.grid(axis = 'y', color = GRID, linewidth = 1)
        axes.set_axisbelow(True)
        axes.tick_params(colors = MUTED, labelsize = 10, length = 0)
        for side in ("top", "right", "left"):
            axes.spines[side].set_visible(False)
        axes.spines["bottom"].set_color(AXIS)

        self._addHover(figure, axes, x, months, lines)
        return figure

    ## crosshair and tooltip showing the exact numbers for the month under the mouse
    def _addHover(self, figure, axes, x, months, lines):
        positions = date2num(x).tolist()
        crosshair = axes.axvline(positions[0], color = AXIS, linewidth = 1, visible = False, zorder = 1)
        note = axes.annotate(
            "", xy = (positions[0], 1), xycoords = axes.get_xaxis_transform(), xytext = (10, -8), textcoords = "offset points",
            va = "top", fontsize = 9, color = INK, visible = False, zorder = 5,
            bbox = {"boxstyle" : "round,pad=0.5", "facecolor" : SURFACE, "edgecolor" : AXIS}
        )
        ## otherwise the whole chart would shift around as the tooltip moves
        crosshair.set_in_layout(False)
        note.set_in_layout(False)

        def onMove(event):
            if(event.inaxes is not axes or event.xdata is None):
                if(note.get_visible()):
                    note.set_visible(False)
                    crosshair.set_visible(False)
                    figure.canvas.draw_idle()
                return
            right = bisect.bisect_left(positions, event.xdata)
            candidates = [i for i in (right - 1, right) if 0 <= i < len(positions)]
            i = min(candidates, key = lambda c: abs(positions[c] - event.xdata))
            text = [months[i]]
            for name, values, trend, curve in lines:
                text.append(f"{name}: no data" if values[i] is None else f"{name}: {values[i]:,} (median {trend[i]:,.0f}, polynomial {curve[i]:,.0f})")
            crosshair.set_xdata([positions[i], positions[i]])
            note.xy = (positions[i], 1)
            isRightSide = i > len(months) * 0.6
            note.set_position((-10 if isRightSide else 10, -8))
            note.set_ha("right" if isRightSide else "left")
            note.set_text("\n".join(text))
            note.set_visible(True)
            crosshair.set_visible(True)
            figure.canvas.draw_idle()

        figure.canvas.mpl_connect("motion_notify_event", onMove)

    ## opens the figure in its own window, so several charts can stay open without drawing over each other
    def show(self, figure, parent, title = "Smogon Scraper"):
        import tkinter as tk
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

        window = tk.Toplevel(parent)
        window.title(title)
        canvas = FigureCanvasTkAgg(figure, master = window)
        NavigationToolbar2Tk(canvas, window)
        canvas.get_tk_widget().pack(side = "top", fill = "both", expand = True)
        canvas.draw()
        return window

## Testing: python plotter.py some_export.json
def main():
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    plotter = Plotter()
    window = plotter.show(plotter.fromJson(sys.argv[1]), root)
    window.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()

if(__name__  == "__main__"): main()
