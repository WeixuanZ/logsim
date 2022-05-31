"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
Gui - configures the main window and all the widgets.
"""
from typing import Union
import wx

from gui_components import (
    Canvas,
    MenuBar,
    CyclesWidget,
    MonitorWidget,
    SwitchWidget,
    ButtonsWidget,
    Console,
    StatusBar,
)

from names import Names
from devices import Devices
from monitors import Monitors
from network import Network
from scanner import Scanner
from parse import Parser


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title:
        title of the window.

    Methods
    -------
    handle_file_load(self, path):
        Handle file load, parse and build the network.
    handle_run_btn_click(self, event):
        Handle event when user presses run button.
    handle_cont_btn_click(self, event):
        Handle event when user presses continue button.
    run_network(self, cycles):
        Run the network for the specified number of simulation cycles.
    """

    def __init__(
        self,
        title: str,
        path: Union[None, str],
        names: Names,
        devices: Devices,
        network: Network,
        monitors: Monitors,
    ):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(1200, 800))
        self.devices = devices
        self.names = names
        self.network = network
        self.monitors = monitors
        self.cycles_completed = [0]  # use list to force pass by reference

        # Logo/icon
        self.SetIcon(wx.Icon("./src/logicgate.png"))

        # Sizer containing everything
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Canvas for showing monitor signals
        self.canvas = Canvas(
            self,
            wx.ID_ANY,
            (10, 10),
            wx.Size(300, 300),
            self.devices,
            self.network,
            self.monitors,
        )
        self.canvas.SetSizeHints(500, 500)

        # Configure sizers for layout
        # Add scrollable canvas to left-hand side
        self.main_sizer.Add(self.canvas, 2, wx.EXPAND | wx.ALL, 5)
        # main_sizer.Add(self.scrollable_canvas, 1, wx.EXPAND + wx.TOP, 10)

        # Widgets
        self._build_side_sizer()

        # Show everything.
        self.SetSizeHints(200, 200)
        self.SetSizer(self.main_sizer)

        # Menu bar and status bar
        self.StatusBar = StatusBar(self)
        if path is not None:
            self.StatusBar.PushStatusText(path)
        # important: load menu bar last, after side sizer
        self.MenuBar = MenuBar(
            self, file_opened=path is not None, on_file=self.handle_file_load
        )

    def _build_side_sizer(self):
        """Build right-hand plane, containing all controls."""
        self.side_sizer = wx.BoxSizer(wx.VERTICAL)

        # Components
        # load console first to show errors during file load
        self.Console = Console(self)
        self.CyclesWidget = CyclesWidget(self)
        self.MonitorWidget = MonitorWidget(
            self,
            self.cycles_completed,
            self.names,
            self.devices,
            self.network,
            self.monitors,
        )
        self.SwitchWidget = SwitchWidget(self, self.names, self.devices)
        self.ButtonsWidget = ButtonsWidget(
            self,
            on_run=self.handle_run_btn_click,
            on_continue=self.handle_cont_btn_click,
        )

        # Add vertical space at top of right-hand side
        self.side_sizer.AddSpacer(15)
        self.side_sizer.Add(self.CyclesWidget, 1, wx.ALIGN_CENTRE, 130)
        self.side_sizer.Add(
            wx.StaticText(self, wx.ID_ANY, "Monitors"), 1, wx.LEFT, 10
        )
        self.side_sizer.AddSpacer(-25)
        self.side_sizer.Add(self.MonitorWidget, 1, wx.EXPAND | wx.ALL, 10)

        # Vertical space between elements
        self.side_sizer.AddSpacer(15)
        self.side_sizer.Add(
            wx.StaticText(self, wx.ID_ANY, "Switches"), 1, wx.LEFT, 10
        )
        self.side_sizer.AddSpacer(-25)
        self.side_sizer.Add(self.SwitchWidget, 1, wx.EXPAND | wx.ALL, 10)

        # Add vertical space
        self.side_sizer.AddSpacer(15)
        # Add run + continue buttons at bottom
        self.side_sizer.Add(self.ButtonsWidget, 1, wx.ALIGN_CENTRE, 130)

        self.side_sizer.AddSpacer(15)
        self.side_sizer.Add(
            wx.StaticText(self, wx.ID_ANY, "Console"), 1, wx.LEFT, 10
        )
        self.side_sizer.AddSpacer(-25)
        self.side_sizer.Add(self.Console, 1, wx.EXPAND | wx.ALL, 10)

        self.main_sizer.Add(self.side_sizer, 1, wx.ALL, 5)

    def handle_file_load(self, path: str):
        """Handle file load, parse and build the network."""
        self.names = Names()
        self.devices = Devices(self.names)
        self.network = Network(self.names, self.devices)
        self.monitors = Monitors(self.names, self.devices, self.network)
        self.cycles_completed[0] = 0

        scanner = Scanner(path, self.names)
        parser = Parser(
            self.names, self.devices, self.network, self.monitors, scanner
        )
        parser.parse_network()
        if parser.errors.error_counter > 0:
            parser.errors.print_error_messages()
            return  # only rebuild buttons if new file has no error

        self.main_sizer.Hide(self.side_sizer)
        self._build_side_sizer()
        self.Layout()

        self.StatusBar.PushStatusText(path)

    def handle_run_btn_click(self, event):
        """Handle event when user presses run button."""
        cycles = self.CyclesWidget.GetValue()

        self.monitors.reset_monitors()
        print("".join(["Running for ", str(cycles), " cycles"]))
        self.devices.cold_startup()
        if self.run_network(cycles):
            self.cycles_completed[0] = cycles
            self.StatusBar.push_cycle_count(self.cycles_completed[0])

    def handle_cont_btn_click(self, event):
        """Handle event when user presses continue button."""
        cycles = self.CyclesWidget.GetValue()
        if self.run_network(cycles):
            self.cycles_completed[0] += cycles
            self.canvas.cycles += cycles
            self.StatusBar.push_cycle_count(self.cycles_completed[0])
        print(
            " ".join(
                [
                    "Continuing for",
                    str(cycles),
                    "cycles.",
                    "Total:",
                    str(self.cycles_completed[0]),
                ]
            )
        )

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        self.canvas.signals = []
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print("Error! Network oscillating.")
                return False
        # self.monitors.display_signals()
        for (
            device_id,
            pin_id,
        ), value in self.monitors.monitors_dictionary.items():
            signal_name = self.devices.get_signal_name(device_id, pin_id)
            self.canvas.signals.append([signal_name, value])
        self.canvas.cycles = cycles
        self.canvas.render()
        return True
