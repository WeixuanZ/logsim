"""TODO.

Canvas - handles all canvas drawing operations.
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
    devices:
        instance of the devices.Devices() class.
    monitors:
        instance of the monitors.Monitors() class.

    Methods
    -------
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
    """

    def __init__(self, parent, id, pos, size, devices, network, monitors):
        """TODO."""
        super().__init__(
            parent,
            -1,
            pos=pos,
            size=size,
            attribList=[
                wxcanvas.WX_GL_RGBA,
                wxcanvas.WX_GL_DOUBLEBUFFER,
                wxcanvas.WX_GL_DEPTH_SIZE,
                16,
                0,
            ],
        )
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        self.pan_x = 0  # Initialise variables for panning
        self.pan_y = 0
        self.zoom = 1  # Initialise variable for zooming

        self.scale_x = 50
        self.scale_y = 50

        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.signals = []

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        # self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1, 1, 1, 1)
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
        self.SetCurrent(self.context)
        size = self.GetClientSize()
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        if len(self.signals) > 0:
            for i in range(len(self.signals[0][-1])):
                GL.glColor3f(0, 0, 0)
                self.render_text(
                    str(i), 100 + i * self.scale_x, self.size.height - 30
                )
                GL.glColor3f(0.8, 0.8, 0.8)
                GL.glLineWidth(1)
                GL.glBegin(GL.GL_LINES)
                GL.glVertex2f(100 + i * self.scale_x, self.size.height - 40)
                GL.glVertex2f(100 + i * self.scale_x, 0)
                GL.glEnd()
            # Draw signals
            num = 1
            for signal in self.signals:
                GL.glColor3f(signal[1][0], signal[1][1], signal[1][2])
                GL.glLineWidth(3)
                self.draw_signal(
                    signal[-1], (100, size.height - 2 * num * self.scale_y)
                )
                GL.glClearColor(1, 1, 1, 0)
                self.render_text(
                    signal[0], 50, size.height - 2 * num * self.scale_y
                )
                num += 1
        else:
            GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
            GL.glBegin(GL.GL_LINE_STRIP)
            for i in range(10):
                x = (i * 20) + 10
                x_next = (i * 20) + 30
                if i % 2 == 0:
                    y = 75
                else:
                    y = 100
                GL.glVertex2f(x, y)
                GL.glVertex2f(x_next, y)
            GL.glEnd()
        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
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
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
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

    # def on_mouse(self, event):
    # """Handle mouse events."""

    def draw_signal(self, signal, offset):
        """Draw line for a given signal."""
        self.max_X = self.scale_x * (len(signal) - 1)
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(len(signal)):
            sig_val = signal[i]
            if sig_val == 1:
                GL.glVertex2f(offset[0] + i * self.scale_x, offset[1])
            else:
                GL.glVertex2f(
                    offset[0] + i * self.scale_x, offset[1] + self.scale_y
                )

            try:
                next_val = (1 - signal[i + 1]) * self.scale_y
                GL.glVertex2f(
                    offset[0] + i * self.scale_x, offset[1] + next_val
                )
            except IndexError:
                pass
        GL.glEnd()


class MenuBar(wx.MenuBar):
    """Menu bar component.

    Handles file load and help.
    """

    OpenID = 998
    HelpID = 110

    def __init__(self, parent: wx.Frame, file_opened: bool, on_file: Callable):
        """Initialize the widget."""
        self.on_file = on_file

        super().__init__()
        fileMenu = wx.Menu()
        fileMenu.Append(self.OpenID, "&Open")
        fileMenu.Append(self.HelpID, "&Help")
        self.Append(fileMenu, "&File")

        self.Bind(wx.EVT_MENU, self.on_menu)  # Menu functionality

        parent.SetMenuBar(self)

        if not file_opened:
            self.handle_file_open()

    def on_menu(self, event) -> None:
        """Handle menu events.

        If Open button is selected, file dialog opens
        to select a .txt description file.
        If Help button is selected, web browser is
        opened to GitHub readme.
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
            message="Open Logic Description File",
            wildcard="TXT files (*.txt)|*.txt",
            style=wx.FD_OPEN + wx.FD_FILE_MUST_EXIST,
        )
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            print("The user cancelled")
            return  # User closed file dialog

        path = openFileDialog.GetPath()
        print("File chosen=", path)
        return path

    def handle_file_open(self) -> None:
        """Call callback function if file selected."""
        path = self.open_file_dialog()
        if path is None:
            return

        self.on_file(path)


class CyclesWidget(wx.BoxSizer):
    """Sizer containing 'Cycles' text and number selector."""

    def __init__(self, parent: wx.Window):
        """Initialize the widget."""
        super().__init__(wx.HORIZONTAL)

        # Number selected to specify #cycles
        self.cycles = wx.SpinCtrl(
            parent, wx.ID_ANY, "10", size=(60, 30), min=1, name="#cycles"
        )
        # Text 'Cycles'
        self.cycles_text = wx.StaticText(parent, wx.ID_ANY, "Cycles")

        # Add text and cycle number selector to sizer.
        self.Add(self.cycles_text, 1, wx.LEFT, 20)
        self.Add(self.cycles, 1, wx.LEFT, 20)

    def GetValue(self):
        """Get the current cycle selector value."""
        return self.cycles.GetValue()


class MonitorWidget(wx.ScrolledWindow):
    """TODO."""

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
            wx.DefaultPosition,
            (100, 200),
            wx.SUNKEN_BORDER | wx.HSCROLL | wx.VSCROLL,
        )
        monitors_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(monitors_sizer)
        self.SetScrollRate(10, 10)
        self.SetAutoLayout(True)

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
            # label = "Test"
            if device.device_kind == self.devices.D_TYPE:
                for pin in list(device.outputs.keys()):
                    if device.device_id in self.initial_monitors_lst:
                        if pin in self.initial_monitor_pins:
                            label = "Remove"
                            value = True
                        else:
                            label = "Add"
                            value = False
                    else:
                        label = "Add"
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
                    label = "Remove"
                    value = True
                else:
                    label = "Add"
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

            device_sizer = wx.BoxSizer(
                wx.HORIZONTAL
            )  # Sizer for single device containing text
            # and one button horizontally
            monitors_sizer.Add(device_sizer, 1, wx.ALIGN_CENTRE, 110)
            self.device_text = wx.StaticText(self, wx.ID_ANY, device_name)
            device_sizer.Add(self.device_text, 1, wx.ALL, 10)
            device_sizer.Add(monitor_button, 1, wx.ALL, 10)

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
            obj.SetLabel("Remove")
        else:
            # stop monitoring device
            self.zap_command(device_id, pin)
            obj.SetLabel("Add")

    def monitor_command(self, device, port):
        """Set the specified monitor."""
        if self.monitors is not None:
            monitor_error = self.monitors.make_monitor(
                device, port, self.cycles_completed[0]
            )
            if monitor_error == self.monitors.NO_ERROR:
                print("Successfully made monitor.")
            else:
                print("Error! Could not make monitor.")

    def zap_command(self, device_id, pin):
        """Remove the specified monitor."""
        if self.monitors is not None:
            if self.monitors.remove_monitor(device_id, pin):
                print("Successfully zapped monitor")
            else:
                print("Error! Could not zap monitor.")


class SwitchWidget(wx.ScrolledWindow):
    """Scrollable window for switches."""

    def __init__(self, parent: wx.Window, names: Names, devices: Devices):
        """Initialize the widget."""
        super().__init__(
            parent,
            -1,
            wx.DefaultPosition,
            (100, 200),
            wx.SUNKEN_BORDER | wx.HSCROLL | wx.VSCROLL,
        )
        switches_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(switches_sizer)
        self.SetScrollRate(10, 10)
        self.SetAutoLayout(True)

        self.names = names
        self.devices = devices

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
                label = "On"
                value = True
            else:
                label = "Off"
                value = False
            switch_button = wx.ToggleButton(self, wx.ID_ANY, label=label)
            switch_button.SetValue(value)
            switch_button.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle_button)

            single_switch_sizer = wx.BoxSizer(wx.HORIZONTAL)
            switch_text = wx.StaticText(
                self, wx.ID_ANY, names.get_name_string(switches_id_val[i][0])
            )
            single_switch_sizer.Add(switch_text, 1, wx.ALL, 10)
            single_switch_sizer.Add(switch_button, 1, wx.ALL, 10)

            switches_sizer.Add(single_switch_sizer, 1, wx.ALIGN_CENTRE, 110)

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
            obj.SetLabel("On")
        else:
            switch_state = 0
            obj.SetLabel("Off")
        if self.devices.set_switch(switch_id, switch_state):
            print("Successfully set switch.")
        else:
            print("Error! Invalid switch.")


class ButtonsWidget(wx.BoxSizer):
    """Widget containing the control buttons."""

    def __init__(
        self, parent: wx.Window, on_run: Callable, on_continue: Callable
    ):
        """Initialize the widget."""
        super().__init__(wx.HORIZONTAL)

        # Run button
        self.run_button = wx.Button(parent, wx.ID_ANY, "Run")
        # Continue button
        self.cont_button = wx.Button(parent, wx.ID_ANY, "Continue")

        # Bind events to widgets
        self.run_button.Bind(wx.EVT_BUTTON, on_run)
        self.cont_button.Bind(wx.EVT_BUTTON, on_continue)

        self.Add(self.run_button, 1, wx.LEFT, 10)
        self.Add(self.cont_button, 1, wx.LEFT, 10)


class Console(wx.TextCtrl):
    """Console component.

    The console redirects from stdout.
    """

    def __init__(self, parent: wx.Window):
        """Initialize the component.

        Redirection only happens after initialization, so load this component
        before code that throws errors.
        """
        super().__init__(
            parent,
            -1,
            size=(200, 100),
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL,
        )
        sys.stdout = self

    def write(self, string):
        """Write string to console."""
        self.WriteText(string)
