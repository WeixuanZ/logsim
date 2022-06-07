"""Components of the GUI.

SPHINX-IGNORE
Classes:
--------
Canvas - Handle all drawing operations.
MenuBar - Menu bar component.
CyclesWidget - Sizer containing 'Cycles' text and number selector.
MonitorWidget - Scrolled window for monitors.
SwitchWidget - Scrollable window for switches.
ButtonsWidget - Widget containing the control buttons.
ConnectionsWidget - Widget containing controls to add and remove connections.
Console - Console component that redirects stdout to gui.
StatusBar - Status bar to display cycle count.
SPHINX-IGNORE
"""
import sys
from typing import Callable, Union

import webbrowser
import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT

from names import Names
from devices import Devices
from monitors import Monitors
from network import Network


class Canvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent:
        parent window.
    id:
        unique id.
    pos:
        position of canvas.
    size:
        size of canvas.
    devices:
        instance of the devices.Devices() class.
    network:
        instance of the network.Network() class.
    monitors:
        instance of the monitors.Monitors() class.

    SPHINX-IGNORE
    Public Methods
    --------------
    init_gl(self):
        Configures the OpenGL context.
    render(self, text):
        Handles all drawing operations.
    on_paint(self, event):
        Handles the paint event.
    on_size(self, event):
        Handles the canvas resize event.
    on_mouse(self, event):
        Handles mouse events.
    render_text(self, text, x_pos, y_pos):
        Handles text drawing operations.
    SPHINX-IGNORE
    """

    def __init__(
        self,
        parent: wx.Frame,
        id: int,
        devices: Devices,
        network: Network,
        monitors: Monitors,
    ):
        """Initialise canvas for displaying monitor signals."""
        super().__init__(
            parent,
            -1,
            attribList=[
                wxcanvas.WX_GL_RGBA,
                wxcanvas.WX_GL_DOUBLEBUFFER,
                wxcanvas.WX_GL_DEPTH_SIZE,
                16,
                0,
            ],
        )
        GLUT.glutInit()
        self.SetSizeHints(500, 500)

        self.init = False
        self.context = wxcanvas.GLContext(self)

        self.pan_x = 0  # Initialise variables for panning
        self.pan_y = 0
        self.zoom = 1  # Initialise variable for zooming
        self.zoom_max = 2
        self.zoom_min = 0.5

        self.scale_x = 50
        self.scale_y = 50

        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.signals = (
            []
        )  # list of lists, where the sublists are [signal_name, value]
        # for single output devices, signal_name is device_name.
        # for double output devices (d-type),
        # signal_name is device_name + '.Q' or '.QBAR'

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

        self.line_colours = [
            [0.85, 0.16, 0.69],  # pink
            [0.07, 0.81, 0.86],  # blue
            [0.90, 0.58, 0],  # orange
            [0.24, 0.89, 0.09],  # green
            [0.56, 0.09, 1],  # purple
        ]

    def init_gl(self):
        """Configure and initialise OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(0.2, 0.2, 0.2, 0.2)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self):
        """Handle all drawing operations."""
        # Initialise
        self.SetCurrent(self.context)
        size = self.GetClientSize()
        # Five preset colours for signal lines
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClearColor(0.2, 0.2, 0.2, 0.2)  # dark gray default background
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # If there are signals to display
        # Only if run/continue have been pressed
        # AND at least 1 monitor has been selected
        if len(self.signals) > 0:
            for i in range(
                len(self.signals[0][-1])
            ):  # Create vertical lines for time steps
                GL.glColor3f(1, 1, 1)  # White text
                # X-axis labels (time)
                self.render_text(
                    str(i), 125 + i * self.scale_x, size.height - 30
                )
                # Generate vertical grid lines
                GL.glColor3f(0.6, 0.6, 0.6)  # light grey grid lines
                GL.glLineWidth(0.25)
                GL.glBegin(GL.GL_LINES)
                GL.glVertex2f(130 + i * self.scale_x, size.height - 40)
                GL.glVertex2f(
                    130 + i * self.scale_x,
                    size.height - len(self.signals) * 115,
                )  # Lines extend depending on number of monitors
                GL.glEnd()
            # Draw signals
            for i, signal in enumerate(self.signals, 1):
                signal_copy = signal[-1].copy()
                signal_copy.insert(0, signal_copy[0])
                # Draw two horizontal gridlines for each signal
                GL.glColor3f(0.6, 0.6, 0.6)
                GL.glLineWidth(0.25)
                GL.glBegin(GL.GL_LINES)
                GL.glVertex2f(
                    130, size.height - 2 * i * self.scale_y
                )  # Horizontal line at value of 0
                GL.glVertex2f(
                    130
                    + len(
                        self.signals[0][-1] * 50
                    ),  # lines extend depending on number of cycles
                    size.height - 2 * i * self.scale_y,
                )
                GL.glVertex2f(
                    130, size.height - 2 * i * self.scale_y + self.scale_y
                )  # Horizontal line at value of 1
                GL.glVertex2f(
                    130 + len(self.signals[0][-1] * 50),
                    size.height - 2 * i * self.scale_y + self.scale_y,
                )
                GL.glEnd()

                # Cycle through five colours for signal lines
                colour_index = i % 5

                GL.glLineWidth(3)
                # Draw signal line
                self.draw_signal(
                    signal_copy,
                    (130, size.height - 2 * i * self.scale_y),
                    colour_index,
                )
                GL.glClearColor(1, 1, 1, 0)
                # Write out name of device (and pin)
                self.render_text(
                    signal[0], 20, size.height - 2 * i * self.scale_y + 20
                )
                # Y-axis labels: 1 and 0, for each monitored device
                self.render_text(
                    "1", 110, size.height - 2 * i * self.scale_y + 46
                )
                self.render_text(
                    "0", 110, size.height - 2 * i * self.scale_y - 3
                )
        # Flush the graphics pipeline
        # and swap the back buffer to the front
        # Necessary!
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True
        self.render()

    def on_size(self, event):
        """Handle canvas resize event.

        Forces reconfiguration of the viewport, modelview and projection
        matrices on the next paint event.
        """
        self.init = False

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(1, 1, 1)  # text is white
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12  # noqa

        for character in text:
            if character == "\n":
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(
                    font, ord(character)
                )  # ord() converts character into Unicode code value

    def on_mouse(self, event):
        """Handle mouse events."""
        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom

        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()

        if event.Dragging():
            # If user drags on canvas, canvas pans.
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False

        if event.GetWheelRotation() < 0:
            # Zoom on wheel rotation
            zoom = self.zoom
            self.zoom = max(
                zoom * 1.0
                + (event.GetWheelRotation() / (20 * event.GetWheelDelta())),
                self.zoom_min,
            )
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False

        if event.GetWheelRotation() > 0:
            # Zoom opposite direction
            self.zoom = min(
                self.zoom
                / (
                    1.0
                    - (event.GetWheelRotation() / (20 * event.GetWheelDelta()))
                ),
                self.zoom_max,
            )
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False

        self.Refresh()  # triggers the paint event

    def draw_signal(self, signal, offset, colour_index):
        """Draw line for a given signal."""
        self.max_X = self.scale_x * (len(signal) - 1)
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(len(signal)):
            sig_val = signal[i]
            # Choose colour
            GL.glColor3f(
                self.line_colours[colour_index][0],
                self.line_colours[colour_index][1],
                self.line_colours[colour_index][2],
            )
            # If the monitor was unmonitored and
            # then monitored later, the singal before
            # being set as a monitor is a different colour.
            # For these periods, the signal value is not 0 or 1.
            if sig_val != 0:
                if sig_val != 1:
                    sig_val = 0.01
                    GL.glColor3f(0.6, 0.6, 0.6)
            if sig_val == 0:
                GL.glVertex2f(offset[0] + i * self.scale_x, offset[1])
            elif sig_val == 1:
                GL.glVertex2f(
                    offset[0] + i * self.scale_x, offset[1] + self.scale_y
                )

            try:
                if signal[i + 1] != 0:
                    if signal[i + 1] != 1:
                        signal[i + 1] = 0.01
                next_val = (signal[i + 1]) * self.scale_y
                GL.glVertex2f(
                    offset[0] + i * self.scale_x, offset[1] + next_val
                )
            except IndexError:
                pass
        GL.glEnd()


class MenuBar(wx.MenuBar):
    """Menu bar component.

    Handles file load and help.

    Parameters
    ----------
    parent: wx.Frame
        parent window
    file_opened: bool
        whether there is a file loaded, if not a file dialogue will appear
    on_file: Callback
        function to load new logic description files

    SPHINX-IGNORE
    Public Methods
    --------------
    on_menu(self, event):
        Handle menu events.
    open_file_dialog(self):
        Open the file dialog.
    handle_file_open(self):
        Call callback function if file selected.
    SPHINX-IGNORE
    """

    OpenID = 998
    HelpID = 110

    def __init__(self, parent: wx.Frame, file_opened: bool, on_file: Callable):
        """Initialize the widget."""
        self.on_file = on_file

        super().__init__()
        fileMenu = wx.Menu()
        fileMenu.Append(self.OpenID, _("&Open"))
        fileMenu.Append(self.HelpID, _("&Help"))
        self.Append(fileMenu, "&File")
        self.Bind(wx.EVT_MENU, self.on_menu)  # Menu functionality

        parent.SetMenuBar(self)

        if not file_opened:
            self.handle_file_open()

    def on_menu(self, event) -> None:
        """Handle menu events.

        If Open button is selected, file dialog opens to select
        a .txt description file.
        If Help button is selected, web browser is opened to GitHub readme.
        """
        if event.GetId() == self.OpenID:
            self.handle_file_open()

        if event.GetId() == self.HelpID:
            webbrowser.open("https://github.com/WeixuanZ/logsim#readme")

    def open_file_dialog(self) -> Union[None, str]:
        """Open the file dialog.

        Returns
        -------
        path: Union[None, str]
            Returns None if user cancels
        """
        openFileDialog = wx.FileDialog(
            self,
            message=_("Open Logic Description File"),
            style=wx.FD_OPEN + wx.FD_FILE_MUST_EXIST,
        )
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            print(_("Cancelled loading new file"))
            return  # User closed file dialog

        return openFileDialog.GetPath()

    def handle_file_open(self) -> None:
        """Call callback function if file selected."""
        path = self.open_file_dialog()
        if path is None:
            return

        self.on_file(path)


class CyclesWidget(wx.BoxSizer):
    """Sizer containing 'Cycles' text and number selector.

    Parameters
    ----------
    parent:
        parent window

    SPHINX-IGNORE
    Public Methods
    --------------
    GetValue(self):
        Get the current cycle selector value.
    SPHINX-IGNORE
    """

    def __init__(self, parent: wx.Window):
        """Initialize the widget."""
        super().__init__(wx.HORIZONTAL)

        # Number selected to specify #cycles
        self.cycles = wx.SpinCtrl(
            parent, wx.ID_ANY, "10", size=(60, 30), min=1, name="#cycles"
        )
        # Text 'Cycles'
        self.cycles_text = wx.StaticText(parent, wx.ID_ANY, _("Cycles"))

        # Add text and cycle number selector to sizer.
        self.Add(self.cycles_text, 1, wx.ALIGN_CENTER_VERTICAL)
        self.Add(self.cycles, 1, wx.ALIGN_CENTER_VERTICAL)

    def GetValue(self):
        """Get the current cycle selector value."""
        return self.cycles.GetValue()


class MonitorWidget(wx.ScrolledWindow):
    """Scrolled window for monitors.

    All devices are listed, with a button
    for each to toggle monitoring.

    Parameters
    ----------
    parent:
        parent window
    cycles_completed:
        list containing number of cycles completed
    names:
        instance of the names.Names() class.
    devices:
        instance of the devices.Devices() class.
    network:
        instance of the network.Network() class.
    monitors:
        instance of the monitors.Monitors() class.

    SPHINX-IGNORE
    Public Methods
    --------------
    on_monitor_button(self, event):
        Handle toggle monitor state of output.
    monitor_command(self, device_id, port):
        Set the specified monitor.
    zap_command(self, device_id, pin):
        Remove the specified monitor.
    SPHINX-IGNORE
    """

    def __init__(
        self,
        parent,
        cycles_completed: list,
        names: Names,
        devices: Devices,
        network: Network,
        monitors: Monitors,
    ):
        """Initialize the widget."""
        self.devices = devices
        self.names = names
        self.network = network
        self.monitors = monitors
        self.cycles_completed = cycles_completed

        super().__init__(
            parent,
            -1,
            style=wx.SUNKEN_BORDER | wx.HSCROLL | wx.VSCROLL,
        )
        monitors_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(monitors_sizer)
        self.SetScrollRate(10, 10)
        self.SetAutoLayout(True)

        self.SetSizeHints((50, 100))

        name_sizer = wx.BoxSizer(wx.VERTICAL)
        btn_sizer = wx.BoxSizer(wx.VERTICAL)
        monitors_sizer.Add(name_sizer, 1, wx.EXPAND)
        monitors_sizer.Add(btn_sizer, 0.5, wx.EXPAND)

        self.monitor_dict = {}
        self.monitor_buttons = []
        self.initial_monitors_lst = []
        self.initial_monitor_pins = []

        for i in range(len(self.monitors.monitors_dictionary)):
            self.initial_monitors_lst.append(
                list(self.monitors.monitors_dictionary.keys())[i][0]
            )
            pin = list(self.monitors.monitors_dictionary.keys())[i][1]
            if pin is not None:
                self.initial_monitor_pins.append(pin)

        # Loop over devices, creating button for each
        i = 0
        for device in self.devices.devices_list:
            if device.device_kind == self.devices.D_TYPE:
                for pin in list(device.outputs.keys()):
                    if device.device_id in self.initial_monitors_lst:
                        if pin in self.initial_monitor_pins:
                            label = _("Remove")
                            value = True
                        else:
                            label = _("Add")
                            value = False
                    else:
                        label = _("Add")
                        value = False

                    self.monitor_buttons.append(
                        wx.ToggleButton(self, wx.ID_ANY, label=label)
                    )
                    if self.names.get_name_string(pin) == "Q":
                        info = self.devices.Q_ID
                    else:
                        info = self.devices.QBAR_ID
                    self.monitor_dict[self.monitor_buttons[i].GetId()] = [
                        device,
                        info,
                    ]
                    self.monitor_buttons[i].Bind(
                        wx.EVT_TOGGLEBUTTON, self.on_monitor_button
                    )
                    self.monitor_buttons[i].SetValue(value)
                    i += 1
            else:
                if device.device_id in self.initial_monitors_lst:
                    label = _("Remove")
                    value = True
                else:
                    label = _("Add")
                    value = False
                self.monitor_buttons.append(
                    wx.ToggleButton(self, wx.ID_ANY, label=label)
                )
                self.monitor_dict[self.monitor_buttons[i].GetId()] = [
                    device,
                    None,
                ]
                self.monitor_buttons[i].SetValue(value)
                self.monitor_buttons[i].Bind(
                    wx.EVT_TOGGLEBUTTON, self.on_monitor_button
                )
                i += 1

        # Iterate over list of buttons, adding each
        # to scrollable sizer for monitors.
        for i, monitor_button in enumerate(self.monitor_buttons):
            button_id = monitor_button.GetId()
            device = self.monitor_dict[button_id][0]
            device_info = self.monitor_dict[button_id][1]
            device_id = device.device_id
            if device_info is None:
                device_name = self.names.get_name_string(device_id)
            elif device_info is self.devices.Q_ID:
                device_name = self.names.get_name_string(device_id) + ".Q"
            elif device_info is self.devices.QBAR_ID:
                device_name = self.names.get_name_string(device_id) + " .QBAR"
            device_name = (
                device_name
                + " <"
                + self.names.get_name_string(device.device_kind)
                + ">"
            )
            device_text = wx.StaticText(self, wx.ID_ANY, device_name)

            name_sizer.Add(device_text, 1, wx.EXPAND | wx.ALL, 10)
            btn_sizer.Add(monitor_button, 1, wx.EXPAND | wx.ALL, 10)

        # Create a list of ids for each monitor button
        # so that we can find out which button was pressed
        # and edit the corresponding device (to be monitored or not)
        self.monitor_buttons_id = []
        for i in self.monitor_buttons:
            self.monitor_buttons_id.append(i.GetId())

    def on_monitor_button(self, event):
        """Handle toggle monitor state of output.

        If output is being monitored, button says 'Remove'.
        If output is not being monitored, button says 'Add'.
        """
        obj = event.GetEventObject()
        button_id = obj.GetId()
        device = self.monitor_dict[button_id]
        device_id = device[0].device_id
        pin = device[1]
        if obj.GetValue():
            # monitor device
            self.monitor_command(device_id, pin)
            obj.SetLabel(_("Remove"))
        else:
            # stop monitoring device
            self.zap_command(device_id, pin)
            obj.SetLabel(_("Add"))

    def monitor_command(self, device_id, port):
        """Set the specified monitor."""
        if self.monitors is not None:
            monitor_error = self.monitors.make_monitor(
                device_id, port, self.cycles_completed[0]
            )
            if monitor_error == self.monitors.NO_ERROR:
                print(
                    _("Successfully made {} a monitor.").format(
                        self.names.get_name_string(device_id)
                    )
                )
            else:
                print(_("Error! Could not make monitor."))

    def zap_command(self, device_id, pin):
        """Remove the specified monitor."""
        if self.monitors is not None:
            if self.monitors.remove_monitor(device_id, pin):
                print(
                    "Successfully zapped monitor "
                    + self.names.get_name_string(device_id)
                    + "."
                )
            else:
                print(_("Error! Could not zap monitor."))


class SwitchWidget(wx.ScrolledWindow):
    """Scrollable window for switches.

    Parameters
    ----------
    parent:
        parent window.
    names:
        instance of the names.Names() class.
    devices:
        instance of the devices.Devices() class.

    SPHINX-IGNORE
    Public Methods
    --------------
    on_toggle_button(self, event):
        Handle event when user presses a button to toggle switch value.
    SPHINX-IGNORE
    """

    def __init__(self, parent: wx.Window, names: Names, devices: Devices):
        """Initialize the widget."""
        super().__init__(
            parent,
            -1,
            style=wx.SUNKEN_BORDER | wx.HSCROLL | wx.VSCROLL,
        )
        self.names = names
        self.devices = devices

        switches_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(switches_sizer)
        self.SetScrollRate(10, 10)
        self.SetAutoLayout(True)
        self.SetSizeHints((50, 100))

        name_sizer = wx.BoxSizer(wx.VERTICAL)
        btn_sizer = wx.BoxSizer(wx.VERTICAL)
        switches_sizer.Add(name_sizer, 1, wx.EXPAND)
        switches_sizer.Add(btn_sizer, 0.5, wx.EXPAND)

        switches_id_val = list(
            map(
                lambda device: (device.device_id, device.switch_state),
                filter(
                    lambda device: device.device_kind == self.devices.SWITCH,
                    self.devices.devices_list,
                ),
            )
        )

        self.switch_btn_id_to_device_id = dict()
        # Iterate over switches, creating button for each and appending to list
        for i, switch in enumerate(switches_id_val):
            if switch[1]:  # Initial value + label of switch
                # depends on initial state of switch
                label = _("On")
                value = True
            else:
                label = _("Off")
                value = False
            switch_button = wx.ToggleButton(self, wx.ID_ANY, label=label)
            switch_button.SetValue(value)
            switch_button.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle_button)

            switch_text = wx.StaticText(
                self, wx.ID_ANY, names.get_name_string(switches_id_val[i][0])
            )

            name_sizer.Add(switch_text, 1, wx.EXPAND | wx.ALL, 10)
            btn_sizer.Add(switch_button, 1, wx.EXPAND | wx.ALL, 10)

            self.switch_btn_id_to_device_id[switch_button.GetId()] = switch[0]

    def on_toggle_button(self, event):
        """Handle event when user presses a button to toggle switch value.

        Text on button changes between On/Off depending on state.
        """
        obj = event.GetEventObject()
        button_id = obj.GetId()
        switch_id = self.switch_btn_id_to_device_id[button_id]
        if obj.GetValue():
            switch_state = 1
            label = _("On")
            obj.SetLabel(label)
        else:
            switch_state = 0
            label = _("Off")
            obj.SetLabel(label)
        if self.devices.set_switch(switch_id, switch_state):
            print(
                _("Successfully set {} {}.").format(
                    self.names.get_name_string(switch_id), label.lower()
                )
            )
        else:
            print(_("Error! Invalid switch."))


class ButtonsWidget(wx.BoxSizer):
    """Widget containing the control buttons.

    Parameters
    ----------
    parent:
        parent window.
    on_run:
        function to handle event of pressing run button.
    on_continue:
        function to handle event of pressing continue button.
    """

    def __init__(
        self, parent: wx.Window, on_run: Callable, on_continue: Callable
    ):
        """Initialize the widget."""
        super().__init__(wx.HORIZONTAL)

        # Run button
        self.run_button = wx.Button(
            parent, wx.ID_ANY, _("Run"), size=(100, 30)
        )
        # Continue button
        self.cont_button = wx.Button(
            parent, wx.ID_ANY, _("Continue"), size=(100, 30)
        )

        # Bind events to widgets
        self.run_button.Bind(wx.EVT_BUTTON, on_run)
        self.cont_button.Bind(wx.EVT_BUTTON, on_continue)

        self.Add(self.run_button, 1, wx.LEFT, 10)
        self.Add(self.cont_button, 1, wx.LEFT, 10)


class ConnectionsWidget(wx.BoxSizer):
    """Widget containing controls to add and remove connections.

    Parameters
    ----------
    parent:
        parent window.
    names:
        instance of the names.Names() class.
    devices:
        instance of the devices.Devices() class.
    network:
        instance of the network.Network() class.

    SPHINX-IGNORE
    Public Methods
    --------------
    on_connect_button(self, event):
        Handle event of user pressing connect button.
    on_disconnect_button(self, event):
        Handle event of user pressing disconnect button.
    break_connection(self, device1_id, pin1_id, device2_id, pin2_id):
        Break an existing connection.
    add_connection(self, device1_id, pin1_id, device2_id, pin2_id):
        Add a connection between input of device1 and output of device2.
    on_input_dropdown(self, event):
        Refresh dropdown for input pin on selection of input device.
    SPHINX-IGNORE
    """

    def __init__(
        self,
        parent: wx.Window,
        names: Names,
        devices: Devices,
        network: Network,
    ):
        """Initialise widget."""
        super().__init__(wx.VERTICAL)

        self.names = names
        self.devices = devices
        self.network = network

        self.dropdown_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.input_choices = {}
        self.output_choices = {}
        for device in self.devices.devices_list:
            if (
                device.device_kind != self.devices.SWITCH
                and device.device_kind != self.devices.CLOCK
            ):
                self.input_choices[
                    self.names.get_name_string(device.device_id)
                ] = device
            if device.device_kind == self.devices.D_TYPE:
                d_type_name = self.names.get_name_string(device.device_id)
                self.output_choices[d_type_name + ".Q"] = device
                self.output_choices[d_type_name + ".QBAR"] = device
            else:
                self.output_choices[
                    self.names.get_name_string(device.device_id)
                ] = device

        self.input = wx.ComboBox(
            parent,
            wx.ID_ANY,
            value=_("Device"),
            choices=list(self.input_choices.keys()),
        )
        self.input.SetSizeHints((20, 30))
        self.input.Bind(wx.EVT_COMBOBOX, self.on_input_dropdown)

        self.input_pin = wx.ComboBox(
            parent,
            wx.ID_ANY,
            value=_("Input Pin"),
            choices=[],
        )
        self.input_pin.SetSizeHints((20, 30))
        self.output = wx.ComboBox(
            parent,
            wx.ID_ANY,
            value=_("Output Pin"),
            choices=list(self.output_choices.keys()),
        )
        self.output.SetSizeHints((20, 30))
        self.connect_button = wx.Button(
            parent, wx.ID_ANY, label=_("Connect"), size=(100, 30)
        )
        self.disconnect_button = wx.Button(
            parent, wx.ID_ANY, label=_("Disconnect"), size=(100, 30)
        )

        self.connect_button.Bind(wx.EVT_BUTTON, self.on_connect_button)
        self.disconnect_button.Bind(wx.EVT_BUTTON, self.on_disconnect_button)

        self.dropdown_sizer.Add(self.output, 1, wx.LEFT, 5)
        self.dropdown_sizer.Add(
            wx.StaticText(parent, wx.ID_ANY, "-"), 0, wx.ALL, 5
        )
        self.dropdown_sizer.Add(self.input, 1, wx.LEFT, 5)
        self.dropdown_sizer.Add(self.input_pin, 1, wx.LEFT, 5)

        self.buttons_sizer.Add(self.connect_button, 1, wx.LEFT, 10)
        self.buttons_sizer.Add(self.disconnect_button, 1, wx.LEFT, 10)

        self.Add(self.dropdown_sizer, 1, wx.EXPAND | wx.ALL, 5)
        self.Add(self.buttons_sizer, 1, wx.ALIGN_CENTRE, 5)

    def on_connect_button(self, event):
        """Handle event of user pressing connect button.

        If all three dropdowns are not selected, error is shown.

        If all three dropdowns are selected, attempt to create
        the given connection.
        """
        input_name = self.input.GetStringSelection()
        input_pin_name = self.input_pin.GetStringSelection()
        output_name = self.output.GetStringSelection()
        if input_name and input_pin_name and output_name:
            input_device = self.input_choices[input_name]
            output_device = self.output_choices[output_name]

            device1_id = input_device.device_id
            device2_id = output_device.device_id
            pin1_id = self.names.query(input_pin_name)
            if "." in output_name:
                # it's Q or QBAR of DTYPE
                parts = output_name.split(".")
                pin2_id = self.names.query(parts[1])
            else:
                pin2_id = None
            self.add_connection(device1_id, pin1_id, device2_id, pin2_id)
        else:
            print(
                _(
                    "Have not selected sufficient devices to create a"
                    "connection."
                )
            )

    def on_disconnect_button(self, event):
        """Handle event of user pressing disconnect button.

        If all three dropdowns are not selected, error is shown.

        If all three dropdowns are selected, attempt to destroy
        the given connection.
        """
        input_name = self.input.GetStringSelection()
        input_pin_name = self.input_pin.GetStringSelection()
        output_name = self.output.GetStringSelection()
        if input_name and input_pin_name and output_name:
            input_device = self.input_choices[input_name]
            output_device = self.output_choices[output_name]

            device1_id = input_device.device_id
            device2_id = output_device.device_id
            pin1_id = self.names.query(input_pin_name)
            if "." in output_name:
                # it's Q or QBAR of DTYPE
                parts = output_name.split(".")
                pin2_id = self.names.query(parts[1])
            else:
                pin2_id = None
            self.break_connection(device1_id, pin1_id, device2_id, pin2_id)
        else:
            print(
                _(
                    "Have not selected sufficient devices to destroy a"
                    "connection."
                )
            )

    def break_connection(self, device1_id, pin1_id, device2_id, pin2_id):
        """Break an existing connection."""
        first_device = self.devices.get_device(device1_id)

        if first_device.inputs[pin1_id] is None:
            print(_("Connection you want to break doesn't exist."))
            return
        else:
            second_device_id, second_port_id = first_device.inputs[pin1_id]
            if second_device_id != device2_id or second_port_id != pin2_id:
                print(_("Connection you want to break doesn't exist."))
                return

        connection = (
            self.names.get_name_string(device1_id)
            + "."
            + self.names.get_name_string(pin1_id)
        )
        connection += "-" + self.names.get_name_string(device2_id)
        if pin2_id is not None:
            connection += "." + self.names.get_name_string(pin2_id)

        first_device.inputs[pin1_id] = None
        print(
            _(
                "Successfully broke connection {}. "
                "Ensure circuit is fully connected before running."
            ).format(connection)
        )

    def add_connection(self, device1_id, pin1_id, device2_id, pin2_id):
        """Add a connection between input of device1 and output of device2."""
        # get previous connection
        first_device = self.devices.get_device(device1_id)

        if first_device.inputs[pin1_id] is not None:
            device, pin = first_device.inputs[pin1_id]
            self.break_connection(device1_id, pin1_id, device, pin)

        error = self.network.make_connection(
            device1_id, pin1_id, device2_id, pin2_id
        )
        if error == self.network.NO_ERROR:
            print(_("Successfully made a connection."))
        else:
            print(_("Error! Couldn't make a connection."))

    def on_input_dropdown(self, event):
        """Refresh dropdown for input pin on selection of input device."""
        self.input_pin.Clear()
        device_name = self.input.GetStringSelection()
        device_id = self.names.query(device_name)
        device = self.devices.get_device(device_id)
        inputs = device.inputs.keys()
        for input in inputs:
            self.input_pin.Append(self.names.get_name_string(input))


class Console(wx.TextCtrl):
    """Console component.

    The console redirects from stdout.

    Parameters
    ----------
    parent:
        parent window.

    SPHINX-IGNORE
    Public Methods
    --------------
    write(self, string):
        Write string to console.
    SPHINX-IGNORE
    """

    def __init__(self, parent: wx.Window):
        """Initialize the component.

        Redirection only happens after initialization, so load this component
        before code that throws errors.
        """
        super().__init__(
            parent,
            -1,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL,
        )
        self.SetFont(
            wx.Font(
                12,
                family=wx.FONTFAMILY_TELETYPE,
                style=wx.NORMAL,
                weight=wx.NORMAL,
            )
        )
        sys.stdout = self

    def write(self, string):
        """Write string to console."""
        self.WriteText(string)


class StatusBar(wx.StatusBar):
    """Status bar to display cycle count.

    Parameters
    ----------
    parent:
        parent window.

    SPHINX-IGNORE
    Public Methods
    --------------
    push_cycle_count(self, cycle_completed: int):
        Push the current cycle count to status bar.
    SPHINX-IGNORE
    """

    def __init__(self, parent):
        """Initialize the component."""
        super().__init__(parent)
        self.SetFieldsCount(2)
        self.SetStatusWidths((-4, -1))

    def push_cycle_count(self, cycle_completed: int):
        """Push the current cycle count to status bar."""
        self.SetStatusText(_("Cycles completed: ") + str(cycle_completed), i=1)
