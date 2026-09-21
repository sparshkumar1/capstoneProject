"""Shared plotting style for the manuscript figures (descriptive re-plots of frozen files only).

Palette: Okabe-Ito subset (#0072B2 blue, #D55E00 vermillion, #009E73 green) plus neutrals.
It was checked with the dataviz validate_palette script (no FAIL; CVD separation is in the legal
6-8 band only with secondary encoding). Every series therefore also has its own marker shape and a
direct or legend label, so figures stay readable in grayscale print.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, VERM, GREEN = "#0072B2", "#D55E00", "#009E73"
INK, MUTED, GRID = "#1a1a1a", "#595959", "#d9d9d9"
COL_W, DBL_W = 3.5, 7.16  # IEEE single / double column width in inches


def setup():
    plt.rcParams.update({
        "font.family": "serif", "font.size": 7, "axes.titlesize": 7.5, "axes.labelsize": 7,
        "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "legend.fontsize": 6.2,
        "axes.edgecolor": MUTED, "axes.linewidth": 0.6, "axes.labelcolor": INK,
        "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
        "axes.spines.top": False, "axes.spines.right": False,
        "grid.color": GRID, "grid.linewidth": 0.5, "figure.dpi": 150, "savefig.dpi": 300,
        "pdf.fonttype": 42,
    })


def save(fig, name, outdir):
    for ext in ("pdf", "png"):
        fig.savefig(f"{outdir}/{name}.{ext}", bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
