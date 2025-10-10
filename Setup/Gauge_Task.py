"""
Visual gauge generator for limit checking and status display.
Creates color-coded horizontal gauge charts with boundary indicators using matplotlib.
Provides visual feedback for measurement values against defined operational limits.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import io


class Gauge_Task:
    def __init__(self):
        self.task_dict = {}

    def create_image(self, limits):
        memfile = io.BytesIO()
        length = 5
        height = 1

        fig, ax = plt.subplots(figsize=(length, height))
        fig.subplots_adjust(bottom=0.5)

        cmap = mpl.colors.ListedColormap(["yellow", "lime", "yellow"]).with_extremes(over="red", under="red")

        Val = limits["val"]
        LL = limits["lim"]["LL"]
        L = limits["lim"]["L"]
        H = limits["lim"]["H"]
        HH = limits["lim"]["HH"]

        bounds = [LL, L, H, HH]
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

        cbar = plt.colorbar(
            mpl.cm.ScalarMappable(cmap=cmap, norm=norm),
            cax=ax,
            drawedges=True,
            boundaries=[40] + bounds + [60],
            extend="both",
            extendfrac="auto",
            extendrect="True",
            ticks=bounds,
            spacing="proportional",
            orientation="horizontal",
        )

        if Val < LL:
            cbar.outline.set_visible(False)
            ax.annotate(
                Val,
                xy=(-4 * length, 0),
                xycoords="axes points",
                xytext=(-4 * length, height * 14),
                textcoords="axes points",
                va="bottom",
                ha="center",
                bbox=dict(boxstyle="round", fc="w"),
                arrowprops=dict(
                    arrowstyle="wedge",
                    color="k",
                ),
            )

        elif Val > HH:
            cbar.outline.set_visible(False)
            ax.annotate(
                Val,
                xy=(length * 42, 0),
                xycoords="axes points",
                xytext=(length * 42, height * 14),
                textcoords="axes points",
                va="bottom",
                ha="center",
                bbox=dict(boxstyle="round", fc="w"),
                arrowprops=dict(
                    arrowstyle="wedge",
                    color="k",
                ),
            )

        else:
            cbar.outline.set_visible(False)
            ax.annotate(
                Val,
                xy=(Val, 0),
                xycoords="data",
                xytext=(Val, 0.5),
                textcoords="data",
                va="bottom",
                ha="center",
                bbox=dict(boxstyle="round", fc="w"),
                arrowprops=dict(
                    arrowstyle="wedge",
                    color="k",
                ),
            )
        plt.savefig(memfile, bbox_inches="tight")
        memfile.seek(0)
        return memfile
