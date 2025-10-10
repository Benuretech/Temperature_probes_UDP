
import numpy as np
import pyqtgraph as pg

class Temp_Graph:
    def __init__(self, plot_widget: pg.PlotWidget,
                 title="Topics", x_label="Time", x_units="s",
                 y_label="Value", y_units=""):
        self.pw = plot_widget
        self.pw.setBackground('#F0EFEF')
        self.pw.setTitle(title, color="k", size="10pt")

        self.pi = self.pw.plotItem
        self.pi.setLabel('bottom', x_label, units=x_units, **{'font-size': '10pt'})
        self.pi.setLabel('left',   y_label, units=y_units,  **{'font-size': '10pt'})
        self.pi.getAxis('bottom').setPen(pg.mkPen(color='#000000', width=2))
        self.pi.getAxis('left').setPen(pg.mkPen(color='#000000', width=2))

        # Legend for topic names
        self.legend = self.pi.addLegend(offset=(10, 10))

        # Optional grid
        grid = pg.GridItem(pen=pg.mkPen(color='k', width=1))
        self.pw.addItem(grid)

        # Curves per topic
        self.curves = {}       # topic -> PlotDataItem
        self._order = []       # to assign colors consistently

        # Make big plots faster
        pg.setConfigOptions(antialias=False, useOpenGL=False)

    def _ns_to_s_if_needed(self, t_array):
        """Convert ns → s when values look like perf_counter_ns()."""
        t_array = np.asarray(t_array)
        # If median timestamp is >= 1e10, assume ns and convert to s
        if t_array.size and np.median(t_array) >= 1e10:
            return t_array * 1e-9
        return t_array

    def _ensure_curve(self, topic):
        if topic in self.curves:
            return self.curves[topic]
        # Stable color per topic index
        if topic not in self._order:
            self._order.append(topic)
        idx = self._order.index(topic)
        pen = pg.mkPen(pg.intColor(idx), width=2)
        curve = self.pi.plot([], [], pen=pen, name=topic)
        self.curves[topic] = curve
        return curve

    def set_topic_data(self, topic_data: dict):
        """
        Full refresh from a dict: {topic: ndarray(N,2) with [time, value]}.
        - If time looks like ns, auto-convert to seconds.
        - Creates curves for new topics and updates existing ones.
        """
        if not isinstance(topic_data, dict):
            print(f"TopicMultiPlot: expected dict, got {type(topic_data)}")
            return

        seen = set()
        for topic, arr in topic_data.items():
            if arr is None:
                continue
            arr = np.asarray(arr)
            if arr.ndim != 2 or arr.shape[1] != 2:
                print(f"TopicMultiPlot: bad shape for {topic}: {arr.shape}, expect (N,2)")
                continue

            t = self._ns_to_s_if_needed(arr[:, 0])
            y = arr[:, 1].astype(np.float64, copy=False)

            curve = self._ensure_curve(topic)
            # For small N, show markers to help debugging
            if len(t) <= 512:
                curve.setData(t, y, symbol=None if len(t) > 64 else 'o', symbolSize=4)
            else:
                curve.setData(t, y)
            seen.add(topic)

        # (Optional) hide curves for topics no longer present
        for topic, curve in self.curves.items():
            curve.setVisible(topic in seen)

        # Optional: auto-range only once or when you want
        self.pi.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)

    def update_topic(self, topic: str, arr):
        """
        Update or create a single topic with ndarray(N,2).
        Useful for incremental updates when only one topic changed.
        """
        arr = np.asarray(arr)
        if arr.ndim != 2 or arr.shape[1] != 2:
            print(f"TopicMultiPlot.update_topic: bad shape for {topic}: {arr.shape}")
            return
        t = self._ns_to_s_if_needed(arr[:, 0])
        y = arr[:, 1].astype(np.float64, copy=False)
        curve = self._ensure_curve(topic)
        curve.setData(t, y)

    def clear(self):
        for c in self.curves.values():
            self.pi.removeItem(c)
        self.curves.clear()
        self._order.clear()
        self.legend.clear()