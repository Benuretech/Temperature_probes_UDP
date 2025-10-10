"""
Custom ViewBox for pyqtgraph with an additional reset view option.
"""

import pyqtgraph as pg
from PyQt6 import QtGui

class CustomViewBox(pg.ViewBox):
    """The CustomViewBox class enhances the standard pyqtgraph ViewBox by adding a "Reset View" entry to its right-click context menu.
    When a user right-clicks on a plot that uses this CustomViewBox and selects "Reset View",
    a reset_view method (defined in an associated graph object) is called, allowing the plot's view to be reset to a default state."""
    def __init__(self, graph, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph = graph  # Reference to the main graph
        self.action_reset = None  # Track if "Reset View" action has been added

    """This method overrides the default context menu behavior of the ViewBox.
    It checks if the "Reset View" action is already in the menu and adds it if not."""
    def raiseContextMenu(self, ev):
        # Get the default context menu
        menu = self.menu

        # Check if the "Reset View" action is already in the menu
        if self.action_reset is None:
            # Add custom "Reset View" option to the default menu
            self.action_reset = QtGui.QAction("Reset View", menu)
            self.action_reset.triggered.connect(self.graph.reset_view)
            menu.addAction(self.action_reset)

        # Convert the event position to a QPoint
        pos = ev.screenPos().toPoint()  # Convert QPointF to QPoint

        # Show the combined menu with both default and custom actions
        menu.exec_(pos)