"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
Gui - configures the main window and all the widgets.
"""
import wx

from gui_components import (
    Canvas,
    MenuBar,
    CyclesWidget,
    MonitorWidget,
    SwitchWidget,
    ButtonsWidget,
    Console,
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
    TODO
    """

    def __init__(
        self,
        title: str,
        file_opened: bool,
        names: Names,
        devices: Devices,
        network: Network,
        monitors: Monitors,
    ):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(1000, 800))
        # wx.Font.AddPrivateFont('./fonts/Geomanist-Regular.ttf')
        # self.SetBackgroundColour((20, 17, 17))
        # self.header_font = wx.Font(25, wx.)
        self.devices = devices
        self.names = names
        self.network = network
        self.monitors = monitors
        self.cycles_completed = [0]  # use list to force pass by reference

        # Components
        # load console first to show errors using file load
        self.Console = Console(self)
        self.MenuBar = MenuBar(
            self, file_opened=file_opened, on_file=self.handle_file_load
        )
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

        # Configure widgets
        self.scrollable_canvas = wx.ScrolledCanvas(self, wx.ID_ANY)
        # Scrollable canvas to display monitored signals
        self.scrollable_canvas.SetSizeHints(500, 500)
        self.scrollable_canvas.ShowScrollbars(
            wx.SHOW_SB_DEFAULT, wx.SHOW_SB_DEFAULT
        )
        self.scrollable_canvas.SetScrollbars(20, 20, 15, 10)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)  # Sizer containing everything
        # Right-hand plane, containing all controls
        side_sizer = wx.BoxSizer(wx.VERTICAL)

        self.canvas = Canvas(
            self.scrollable_canvas,
            wx.ID_ANY,
            (10, 10),
            wx.Size(300, 200),
            self.devices,
            self.network,
            self.monitors,
        )
        self.canvas.SetSizeHints(500, 500)

        # Add scrollable canvas to left hand side
        main_sizer.Add(self.scrollable_canvas, 1, wx.EXPAND + wx.TOP, 10)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        # Add vertical space at top of right hand side
        side_sizer.AddSpacer(30)
        side_sizer.Add(self.CyclesWidget, 1, wx.ALIGN_CENTRE, 130)
        side_sizer.Add(self.MonitorWidget, 1, wx.EXPAND | wx.ALL, 10)

        # Vertical space between elements
        side_sizer.AddSpacer(35)
        side_sizer.Add(self.SwitchWidget, 1, wx.EXPAND | wx.ALL, 10)

        # Add vertical space
        side_sizer.AddSpacer(35)
        # Add run + continue buttons at bottom
        side_sizer.Add(self.ButtonsWidget, 1, wx.ALIGN_CENTRE, 130)

        side_sizer.AddSpacer(35)
        side_sizer.Add(self.Console, 1, wx.EXPAND | wx.ALL, 10)

        # Show everything.
        self.SetSizeHints(200, 200)
        self.SetSizer(main_sizer)

    def handle_file_load(self, path: str):
        """Handle file load, parse and build the network."""
        self.names = Names()
        self.devices = Devices(self.names)
        self.network = Network(self.names, self.devices)
        self.monitors = Monitors(self.names, self.devices, self.network)

        scanner = Scanner(path, self.names)
        parser = Parser(
            self.names, self.devices, self.network, self.monitors, scanner
        )
        parser.parse_network()
        if parser.errors.error_counter > 0:
            parser.errors.print_error_messages()

    def handle_run_btn_click(self, event):
        """Handle event when user presses run button."""
        cycles = self.CyclesWidget.GetValue()

        self.monitors.reset_monitors()
        print("".join(["Running for ", str(cycles), " cycles"]))
        self.devices.cold_startup()
        if self.run_network(cycles):
            self.cycles_completed[0] = cycles

    def handle_cont_btn_click(self, event):
        """Handle event when user presses continue button."""
        cycles = self.CyclesWidget.GetValue()
        if self.run_network(cycles):
            self.cycles_completed[0] += cycles
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
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print("Error! Network oscillating.")
                return False
        # TODO display signals
        self.monitors.display_signals()
        return True
