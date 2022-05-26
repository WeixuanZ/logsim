"""TODO."""
import wx

# 4.1.1 msw (phoenix) wxWidgets 3.1.5
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT
import webbrowser


class Canvas(wxcanvas.GLCanvas):
    """TODO."""

    def __init__(
        self, parent, id, pos, size, devices=[], network=[], monitors=[]
    ):
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
        font = GLUT.GLUT_BITMAP_HELVETICA_12

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


class Gui(wx.Frame):
    """TODO."""

    OpenID = 998
    HelpID = 110

    def __init__(self, title):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(1000, 800))
        # wx.Font.AddPrivateFont('./fonts/Geomanist-Regular.ttf')
        # self.SetBackgroundColour((20, 17, 17))
        # self.header_font = wx.Font(25, wx.)
        OpenID = 998
        HelpID = 110

        # Configure file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(OpenID, "&Open")
        fileMenu.Append(HelpID, "&Help")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Configure widgets
        self.scrollable_canvas = wx.ScrolledCanvas(self, wx.ID_ANY)
        self.scrollable_canvas.SetSizeHints(500, 500)
        self.scrollable_canvas.ShowScrollbars(
            wx.SHOW_SB_DEFAULT, wx.SHOW_SB_DEFAULT
        )
        self.scrollable_canvas.SetScrollbars(20, 20, 15, 10)

        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.cont_button = wx.Button(self, wx.ID_ANY, "Continue")
        self.cycles = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.cycles_text = wx.StaticText(self, wx.ID_ANY, "Cycles")

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.cont_button.Bind(wx.EVT_BUTTON, self.on_cont_button)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)
        cycle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        monitors_sizer = wx.BoxSizer(wx.VERTICAL)

        self.canvas = Canvas(
            self.scrollable_canvas, wx.ID_ANY, (10, 10), wx.Size(300, 200)
        )
        self.canvas.SetSizeHints(500, 500)
        main_sizer.Add(self.scrollable_canvas, 1, wx.EXPAND + wx.TOP, 10)

        side_sizer.AddSpacer(30)
        side_sizer.Add(cycle_sizer, 1, wx.LEFT, 100)
        side_sizer.Add(monitors_sizer, 1, wx.LEFT, 100)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        controlwin1 = wx.ScrolledWindow(
            self,
            -1,
            wx.DefaultPosition,
            (100, 200),
            wx.SUNKEN_BORDER | wx.HSCROLL | wx.VSCROLL,
        )
        # Add Text 'Monitors' above box containing monitors.
        # Currently causes massive gap!
        # Put them together into another sizer?
        # side_sizer.Add(wx.StaticText(self, wx.ID_ANY, 'Monitors'),
        # 1, wx.LEFT, 10)
        side_sizer.Add(controlwin1, 1, wx.EXPAND | wx.ALL, 10)
        monitors_sizer = wx.BoxSizer(wx.VERTICAL)
        controlwin1.SetSizer(monitors_sizer)
        controlwin1.SetScrollRate(10, 10)
        controlwin1.SetAutoLayout(True)
        for device in ["A", "B", "C", "D", "E", "F"]:
            device_sizer = wx.BoxSizer(wx.HORIZONTAL)
            monitors_sizer.Add(device_sizer, 1, wx.LEFT, 80)
            self.device_text = wx.StaticText(controlwin1, wx.ID_ANY, device)
            self.delete_button = wx.Button(controlwin1, wx.ID_ANY, "Delete")
            self.delete_button.Bind(wx.EVT_BUTTON, self.on_delete_button)
            device_sizer.Add(self.device_text, 1, wx.ALL, 10)
            device_sizer.Add(self.delete_button, 1, wx.ALL, 10)

        cycle_sizer.Add(self.cycles_text, 1, wx.LEFT, 20)
        cycle_sizer.Add(self.cycles, 1, wx.LEFT, 20)

        self.SetSizeHints(200, 200)
        self.SetSizer(main_sizer)

        controlwin2 = wx.ScrolledWindow(
            self,
            -1,
            wx.DefaultPosition,
            (100, 200),
            wx.SUNKEN_BORDER | wx.HSCROLL | wx.VSCROLL,
        )
        # Add Text 'Switches' above box containing switches.
        # Currently causes massive gap!
        # Put them together into another sizer?
        # side_sizer.Add(wx.StaticText(self, wx.ID_ANY, 'Switches'),
        # 1, wx.LEFT, 10)
        side_sizer.Add(controlwin2, 1, wx.EXPAND | wx.ALL, 10)
        switches_sizer = wx.BoxSizer(wx.VERTICAL)
        controlwin2.SetSizer(switches_sizer)
        controlwin2.SetScrollRate(10, 10)
        controlwin2.SetAutoLayout(True)

        switches = [
            ["switch1", True],
            ["switch2", True],
            ["switch3", False],
            ["switch4", True],
        ]
        switch_buttons = []
        for i, switch in enumerate(switches):

            if switch[1]:
                label = "On"
                value = True
            else:
                label = "Off"
                value = False

            switch_buttons.append(
                wx.ToggleButton(controlwin2, wx.ID_ANY, label=label)
            )
            switch_buttons[i].SetValue(value)
            switch_buttons[i].Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle_button)

        for i, switch_button in enumerate(switch_buttons):
            single_switch_sizer = wx.BoxSizer(wx.HORIZONTAL)
            switches_sizer.Add(single_switch_sizer, 1, wx.LEFT, 80)
            self.switch_text = wx.StaticText(
                controlwin2, wx.ID_ANY, switches[i][0]
            )
            single_switch_sizer.Add(self.switch_text, 1, wx.ALL, 10)
            single_switch_sizer.Add(switch_button, 1, wx.ALL, 10)

        side_sizer.Add(buttons_sizer, 1, wx.LEFT, 100)
        buttons_sizer.Add(self.run_button, 1, wx.LEFT, 10)
        buttons_sizer.Add(self.cont_button, 1, wx.LEFT, 10)

    def on_menu(self, event):
        """TODO."""
        if event.GetId() == self.OpenID:
            openFileDialog = wx.FileDialog(
                self,
                "Open Logic Description File",
                "",
                "",
                wildcard="TXT files (*.txt)|*.txt",
                style=wx.FD_OPEN + wx.FD_FILE_MUST_EXIST,
            )
            if openFileDialog.ShowModal() == wx.ID_CANCEL:
                print("The user cancelled")
                return  # User closed file dialog
            print(
                "File chosen=", openFileDialog.GetPath()
            )  # If file is selected, obtain path of file, for reading.
        if event.GetId() == self.HelpID:
            webbrowser.open("https://github.com/WeixuanZ/logsim#readme")

    def on_run_button(self, event):
        """TODO."""
        pass

    def on_cont_button(self, event):
        """TODO."""
        pass

    def on_delete_button(self, event):
        """TODO."""
        pass

    def on_toggle_button(self, event):
        """TODO."""
        obj = event.GetEventObject()
        if obj.GetValue():
            obj.SetLabel("On")
        else:
            obj.SetLabel("Off")


app = wx.App()
gui = Gui("Logic Simulator")
gui.Show(True)
app.MainLoop()
