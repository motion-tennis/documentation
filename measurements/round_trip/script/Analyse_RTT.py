"""Round-trip delay analysis (R-RT05).

Reads every CSV measurement set in ../data, builds a time histogram of the
valid round-trip delays (log-scaled counts) and exports one PNG per data set
to ../results using the same base name as the CSV file.

Additionally exports two LaTeX longtblr tables (one row per data set) to
../results: rtt_completeness.tex and rtt_statistics.tex.

Expected CSV columns: sequence, setup, status, rtt_ns, rtt_us,
ignored_packets. The delay is taken from rtt_ns and converted to ms.
Files without the required columns (old format) are skipped.
Status handling: "ok" = received, "timeout" = timeout, any other status =
aborted measurement. Only "ok" rows contribute to the delay statistics.
"""

import csv
import math
import statistics
from collections import Counter
from pathlib import Path


import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"

BIN_WIDTH_MS = 0.25
NS_PER_MS = 1e6
REQUIRED_COLUMNS = {"status", "rtt_ns"}
# Files in the data folder that are not analysed (old format / test run)
IGNORED_FILES = {"messung.csv", "test.csv"}
# Data set listed first in the tables, remaining ones follow alphabetically
BASELINE_NAME = "normal"
DPI = 200
SHOW_PLOTS = True  # open the figures in the GUI (e.g. Spyder) after saving

# Colour palette
BAR_COLOR = "#2F5D8C"
EDGE_COLOR = "#FFFFFF"
MEDIAN_COLOR = "#E08A1E"
P95_COLOR = "#B23A48"
TEXT_COLOR = "#222222"
GRID_COLOR = "#D9D9D9"


def load_measurement(csv_path):
    """Return (valid delays in ms, status counts) of one CSV file.

    Returns None if the file does not have the required columns.
    """
    values = []
    statuses = Counter()
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not REQUIRED_COLUMNS.issubset(reader.fieldnames or []):
            return None
        for row in reader:
            status = row["status"].strip().lower()
            statuses[status] += 1
            if status != "ok":
                continue
            try:
                values.append(int(row["rtt_ns"]) / NS_PER_MS)
            except ValueError:
                continue
    return values, statuses


def percentile(sorted_values, fraction):
    """Linear-interpolated percentile of an already sorted list."""
    position = (len(sorted_values) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def build_bin_edges(values):
    """Fixed-width bin edges covering the full data range."""
    start = math.floor(min(values) / BIN_WIDTH_MS) * BIN_WIDTH_MS
    stop = (math.floor(max(values) / BIN_WIDTH_MS) + 1) * BIN_WIDTH_MS
    count = int(round((stop - start) / BIN_WIDTH_MS))
    return [start + i * BIN_WIDTH_MS for i in range(count + 1)]


def plot_histogram(values, title, output_path):
    """Create the log-count delay histogram and save it as PNG."""
    ordered = sorted(values)
    median = statistics.median(ordered)
    p95 = percentile(ordered, 0.95)

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial"],
        "axes.edgecolor": "#444444",
        "axes.labelcolor": TEXT_COLOR,
        "xtick.color": TEXT_COLOR,
        "ytick.color": TEXT_COLOR,
    })

    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.hist(
        ordered,
        bins=build_bin_edges(ordered),
        log=True,
        color=BAR_COLOR,
        edgecolor=EDGE_COLOR,
        linewidth=0.6,
        zorder=3,
    )

    ax.axvline(median, color=MEDIAN_COLOR, linestyle="--", linewidth=1.6,
               zorder=4, label=f"Median: {median:.2f} ms")
    ax.axvline(p95, color=P95_COLOR, linestyle="--", linewidth=1.6,
               zorder=4, label=f"95th percentile: {p95:.2f} ms")

    ax.set_xlabel("Delay (ms)", fontsize=12, labelpad=8)
    ax.set_ylabel("Count (log scale)", fontsize=12, labelpad=8)
    ax.set_title("Round-Trip Delay Histogram", fontsize=14,
                 fontweight="bold", color=TEXT_COLOR, pad=30)
    # Subtitle: name of the measurement data set
    ax.text(0.5, 1.025, f"Filename: {title}", transform=ax.transAxes, ha="center",
            va="bottom", fontsize=11, color="#666666")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0.8)

    ax.grid(True, which="major", axis="y", color=GRID_COLOR, linewidth=0.8,
            zorder=0)
    ax.grid(True, which="minor", axis="y", color=GRID_COLOR, linewidth=0.4,
            alpha=0.6, zorder=0)
    ax.set_axisbelow(True)
    # Ticks point inwards; top and right frame lines stay visible
    ax.tick_params(which="both", direction="in", top=True, right=True)

    legend = ax.legend(loc="upper right", frameon=True, fontsize=10)
    legend.get_frame().set_edgecolor(GRID_COLOR)

    stats_text = (
        f"n = {len(ordered)}\n"
        f"min = {ordered[0]:.2f} ms\n"
        f"mean = {statistics.fmean(ordered):.2f} ms\n"
        f"max = {ordered[-1]:.2f} ms\n"
        f"bin width = {BIN_WIDTH_MS:g} ms"
    )
    ax.text(0.985, 0.70, stats_text, transform=ax.transAxes, ha="right",
            va="top", fontsize=10, color=TEXT_COLOR, linespacing=1.5,
            bbox={"boxstyle": "round,pad=0.5", "facecolor": "#F5F7FA",
                  "edgecolor": GRID_COLOR})

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=DPI, facecolor="white")
    if not SHOW_PLOTS:
        plt.close(fig)


LATEX_SPECIAL = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

COMPLETENESS_HEADER = ["Data set", "Sent", "Received", "Timeouts", "Aborted",
                       "No valid response"]
STATISTICS_HEADER = ["Data set", "Min [ms]", "Mean [ms]", "Median [ms]",
                     "p95 [ms]", "Max [ms]"]


def latex_escape(text):
    """Escape characters that are special in LaTeX."""
    return "".join(LATEX_SPECIAL.get(char, char) for char in text)


def completeness_row(name, statuses):
    """Counts of one data set; 'no valid response' includes aborted runs."""
    sent = sum(statuses.values())
    received = statuses["ok"]
    timeouts = statuses["timeout"]
    aborted = sent - received - timeouts
    missing = sent - received
    share = 100.0 * missing / sent if sent else 0.0
    return [latex_escape(name), str(sent), str(received), str(timeouts),
            str(aborted), f"{missing}/{sent} ({share:.2f}\\,\\%)"]


def statistics_row(name, values):
    """Delay statistics (ms) of one data set."""
    ordered = sorted(values)
    cells = [ordered[0], statistics.fmean(ordered), statistics.median(ordered),
             percentile(ordered, 0.95), ordered[-1]]
    return [latex_escape(name)] + [f"{value:.3f}" for value in cells]


def write_longtblr(output_path, caption, label, header, rows):
    """Write one tabularray longtblr table as a stand-alone .tex fragment."""
    colspec = (r"Q[l,m,font=\bfseries] "
               + " ".join(["X[c,m]"] * (len(header) - 1)))
    lines = [
        "% Generated by Analyse_RTT.py - do not edit manually.",
        "% Requires tabularray and the colours rowlight, rowdark, techred.",
        r"\begin{longtblr}[caption = {" + caption + r"}, label = {" + label
        + r"}]{",
        r"  width = \textwidth,",
        "  colspec = {" + colspec + "},",
        "  rowhead = 1,",
        "  row{even} = {bg=rowlight},",
        "  row{odd} = {bg=rowdark},",
        r"  row{1} = {bg=techred, fg=white, font=\bfseries},",
        "}",
    ]
    for line in [header] + rows:
        lines.append("  " + " & ".join(line) + r" \\")
    lines.append(r"\end{longtblr}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    csv_files = sorted(
        (path for path in DATA_DIR.glob("*.csv")
         if path.name not in IGNORED_FILES),
        key=lambda path: (path.stem != BASELINE_NAME, path.stem),
    )
    if not csv_files:
        print(f"No CSV files found in {DATA_DIR}")
        return

    completeness_rows = []
    statistics_rows = []
    for csv_path in csv_files:
        measurement = load_measurement(csv_path)
        if measurement is None:
            print(f"Skipping {csv_path.name}: unexpected CSV format")
            continue
        values, statuses = measurement
        if not values:
            print(f"Skipping {csv_path.name}: no valid samples")
            continue
        output_path = RESULTS_DIR / f"{csv_path.stem}.png"
        plot_histogram(values, csv_path.name, output_path)
        completeness_rows.append(completeness_row(csv_path.stem, statuses))
        statistics_rows.append(statistics_row(csv_path.stem, values))
        print(f"{csv_path.name}: {len(values)} samples -> {output_path}")

    if completeness_rows:
        write_longtblr(RESULTS_DIR / "rtt_completeness.tex",
                       "Round-trip measurement completeness",
                       "tab:rtt-completeness", COMPLETENESS_HEADER,
                       completeness_rows)
        write_longtblr(RESULTS_DIR / "rtt_statistics.tex",
                       "Round-trip delay statistics",
                       "tab:rtt-statistics", STATISTICS_HEADER,
                       statistics_rows)

    if SHOW_PLOTS:
        plt.show()


if __name__ == "__main__":
    main()
