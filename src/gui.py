"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

SPHINX-IGNORE
Classes:
--------
Gui - configures the main window and all the widgets.
SPHINX-IGNORE
"""
from pathlib import Path
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
from exceptions import Errors


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: str
        Title of the window.
    path: Union[None, str]
        The path to the loaded file, is None if no file is loaded
    names: Names
    devices: Devices
    network: Network
    monitors: Monitors

    SPHINX-IGNORE
    Public Methods
    --------------
    handle_file_load(self, path):
        Handle file load, parse and build the network.
    handle_run_btn_click(self, event):
        Handle event when user presses run button.
    handle_cont_btn_click(self, event):
        Handle event when user presses continue button.
    run_network(self, cycles):
        Run the network for the specified number of simulation cycles.
    SPHINX-IGNORE
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
        super().__init__(parent=None, title=title, size=(1200, 820))
        self.devices = devices
        self.names = names
        self.network = network
        self.monitors = monitors
        self.cycles_completed = [0]  # use list to force pass by reference

        # Open maximised
        # self.Maximize(True)

        # Logo/icon
        self.SetIcon(
            wx.Icon(str(Path(__file__).resolve().with_name("logicgate.png")))
        )

        # Sizer containing everything
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.left_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.left_sizer, 3, wx.EXPAND)

        # load console first to show errors during file load
        self.Console = Console(self)

        # Canvas for showing monitor signals
        self.Canvas = Canvas(
            self,
            wx.ID_ANY,
            self.devices,
            self.network,
            self.monitors,
        )

        # Configure sizers for layout
        # Add scrollable canvas to left-hand side
        self.left_sizer.Add(self.Canvas, 4, wx.EXPAND | wx.ALL, 5)
        self.left_sizer.Add(self.Console, 1, wx.EXPAND | wx.ALL, 5)

        # Widgets
        self._build_side_sizer()

        # Show everything.
        self.SetSizeHints(800, 500)
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
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)

        # Components
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
        self.right_sizer.AddSpacer(15)
        self.right_sizer.Add(self.CyclesWidget, 0.5, wx.ALIGN_CENTRE, 130)
        self.right_sizer.AddSpacer(15)

        self.right_sizer.Add(wx.StaticText(self, wx.ID_ANY, "Monitors"), 0)
        self.right_sizer.Add(self.MonitorWidget, 1, wx.EXPAND | wx.ALL, 10)

        self.right_sizer.AddSpacer(15)

        self.right_sizer.Add(wx.StaticText(self, wx.ID_ANY, "Switches"), 0)
        self.right_sizer.Add(self.SwitchWidget, 1, wx.EXPAND | wx.ALL, 10)

        self.right_sizer.AddSpacer(15)

        # Add run + continue buttons at bottom
        self.right_sizer.Add(self.ButtonsWidget, 0.5, wx.ALIGN_CENTRE, 130)
        self.right_sizer.AddSpacer(15)

        self.main_sizer.Add(self.right_sizer, 1, wx.EXPAND | wx.ALL, 5)

    def handle_file_load(self, path: str):
        """Handle file load, parse and build the network."""
        self.names = Names()
        self.devices = Devices(self.names)
        self.network = Network(self.names, self.devices)
        self.monitors = Monitors(self.names, self.devices, self.network)
        self.cycles_completed[0] = 0

        errors = Errors()
        scanner = Scanner(path, self.names, errors)
        parser = Parser(
            self.names,
            self.devices,
            self.network,
            self.monitors,
            scanner,
            errors,
        )
        parser.parse_network()

        # remove the buttons
        self.main_sizer.Hide(self.right_sizer)

        # replace the console with an empty one
        self.left_sizer.Hide(self.Console)
        self.Console.Destroy()
        self.Console = Console(self)
        self.left_sizer.Add(self.Console, 1, wx.EXPAND | wx.ALL, 5)

        # hide the canvas
        self.left_sizer.Hide(self.Canvas)

        print(f"File opened, path: {path}\n")

        if parser.errors.error_counter > 0:
            parser.errors.print_error_messages(self.names, scanner)
            self.Layout()
            return  # only rebuild buttons if new file has no error

        self._build_side_sizer()
        # display the canvas
        self.left_sizer.Show(self.Canvas)
        # clear the canvas
        self.Canvas.signals = []
        self.Canvas.render()
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
            self.Canvas.cycles += cycles
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
        self.Canvas.signals = []
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
            self.Canvas.signals.append([signal_name, value])
        self.Canvas.cycles = cycles
        self.Canvas.render()
        return True
