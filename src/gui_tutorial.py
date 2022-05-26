"""TODO."""
import wx

# 4.1.1 msw (phoenix) wxWidgets 3.1.5
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT


class MyGLCanvas(wxcanvas.GLCanvas):
    """TODO."""

    def __init__(self, parent, id, pos, size):
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

        self.pan_x = 0
        self.pan_y = 0
        self.zoom = 1

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

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
        GL.glTranslated(self.pan_x, self.pan_y, 0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text):
        """Handle drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure viewport, modelview and projection matrics
            self.init_gl()
            self.init = True

        GL.glClear(GL.GL_COLOR_BUFFER_BIT)  # Clear everything
        self.render_text(text, 10, 10)  # Draw specified text at (10,10)

        GL.glColor3f(0, 0, 1)  # blue signal trace
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
        # We have been drawing to the back buffer; flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            self.init_gl()
            self.init = True
        size = self.GetClientSize()
        text = "".join(
            [
                "Canvas redrawn on paint event, size is ",
                str(size.width),
                ", ",
                str(size.height),
            ]
        )
        self.render(text)

    def on_size(self, event):
        """Handle canvas resize event.

        Forces reconfiguration of viewport, modelview and
        projection matrices on next paint event.
        """
        self.init = False

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0, 0, 0)  # black text
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == "\n":
                y_pos -= 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(
                    font, ord(character)
                )  # ord() converts character into Unicode code value


class GUIx(wx.Frame):
    """TODO."""

    QuitID = 999
    OpenID = 998

    def __init__(self, title):
        """Initialise widgets and layout."""
        super().__init__(
            parent=None, title=title, size=(1000, 700)
        )  # constructor
        # wx.Font.AddPrivateFont('./fonts/Geomanist-Regular.ttf')
        # self.SetFont(wx.Font('./fonts/Geomanist-Regular.ttf'))
        # self.header_font = wx.Font('./fonts/Geomanist-Regular.ttf')
        # self.label_font = wx.Font('./fonts/Geomanist-Regular.ttf')
        QuitID = 999
        OpenID = 998
        # locale = wx.Locale(wx.LANGUAGE_ENGLISH)

        # File Menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_EXIT, "&Exit")  # Add exit to file dropdown menu
        menuBar.Append(fileMenu, "&File")  # Add file dropdown to menu bar
        self.SetMenuBar(menuBar)

        self.scrollable = wx.ScrolledCanvas(self, wx.ID_ANY)
        self.scrollable.SetSizeHints(200, 200)
        self.scrollable.ShowScrollbars(wx.SHOW_SB_ALWAYS, wx.SHOW_SB_DEFAULT)
        self.scrollable.SetScrollbars(20, 20, 15, 10)

        # Toolbar
        toolbar = (
            self.CreateToolBar()
        )  # Create toolbar (below menu bar) which has icons
        myimage = wx.ArtProvider.GetBitmap(
            wx.ART_NEW, wx.ART_TOOLBAR
        )  # New file icon for button on toolbar
        toolbar.AddTool(wx.ID_ANY, "New File", myimage)
        myimage = wx.ArtProvider.GetBitmap(
            wx.ART_FILE_OPEN, wx.ART_TOOLBAR
        )  # Open file icon
        toolbar.AddTool(OpenID, "Open File", myimage)
        myimage = wx.ArtProvider.GetBitmap(
            wx.ART_FILE_SAVE, wx.ART_TOOLBAR
        )  # Save file icon
        toolbar.AddTool(wx.ID_ANY, "Save File", myimage)
        myimage = wx.ArtProvider.GetBitmap(
            wx.ART_QUIT, wx.ART_TOOLBAR
        )  # Quit icon
        toolbar.AddTool(QuitID, "Quit", myimage)
        toolbar.Bind(
            wx.EVT_TOOL, self.Toolbarhandler
        )  # Bind toolbar function to toolbar
        toolbar.Realize()
        self.ToolBar = toolbar

        # Widgets
        self.text = wx.StaticText(self, wx.ID_ANY, "Text")  # Random text
        self.button1 = wx.Button(
            self, wx.ID_ANY, label="Button1", name="guwey", size=(5, 30)
        )  # Button
        self.button2 = wx.Button(self, wx.ID_ANY, "Button2", size=(5, 30))

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.OnMenu)  # OnMenu event
        self.button1.Bind(wx.EVT_BUTTON, self.OnButton1)  # OnButton1 event
        self.button2.Bind(wx.EVT_BUTTON, self.OnButton2)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(
            wx.HORIZONTAL
        )  # Sizer to put two buttons next to eachother horizontally
        button_sizer.Add(self.text, 1, wx.TOP + wx.LEFT + wx.RIGHT, 5)
        button_sizer.Add(self.button1, 1, wx.ALL, 10)
        button_sizer.Add(self.button2, 1, wx.ALL, 10)
        # button_sizer.Add(self.text, 1, wx.TOP+wx.LEFT+wx.RIGHT, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        # side_sizer.Add(self.text, 1, wx.TOP, 10)
        # side_sizer.Add(self.button1, 1, wx.ALL, 5)
        # side_sizer.Add(self.button2, 1, wx.ALL, 5)

        self.canvas = MyGLCanvas(
            self.scrollable, wx.ID_ANY, wx.DefaultPosition, wx.Size(300, 200)
        )
        self.canvas.SetSizeHints(500, 500)

        self.SetSizeHints(300, 300)
        self.SetSizer(button_sizer)

        # Scrolled window
        controlwin = wx.ScrolledWindow(
            self,
            -1,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.SUNKEN_BORDER | wx.HSCROLL | wx.VSCROLL,
        )
        button_sizer.Add(controlwin, 1, wx.EXPAND | wx.ALL, 10)
        button_sizer2 = wx.BoxSizer(wx.VERTICAL)
        controlwin.SetSizer(button_sizer2)
        controlwin.SetScrollRate(10, 10)
        controlwin.SetAutoLayout(True)

        button_sizer2.Add(
            wx.Button(controlwin, wx.ID_ANY, "Run"), 0, wx.ALL, 10
        )

    def OnMenu(self, event):
        """Event when user selects menu item."""
        Id = event.GetId()
        if (
            Id == wx.ID_EXIT
        ):  # If the exit button is selected from menu dropdown
            print("Quitting")  # Terminal print
            self.Close(True)

    def OnButton1(self, event):
        """Event when button 1 is pressed."""
        print("Crister Ronald Guwey")  # Terminal print

    def OnButton2(self, event):
        """When button 2 is pressed, find button 1 and change its label."""
        print("Button 2 pressed")  # Terminal print
        tmp = wx.FindWindowByName("guwey")
        if tmp is not None:
            tmp.SetLabel("Crister Ronald Guwey")

    def Toolbarhandler(self, event):
        """Handle toolbar events.

        Currently only has actions for quit icon and open icon.
        """
        if event.GetId() == self.QuitID:
            print("Quitting")
            self.Close(True)
        if (
            event.GetId() == self.OpenID
        ):  # Open a file dialog to open .txt files.
            openFileDialog = wx.FileDialog(
                self,
                "Open .txt File",
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


# Set up app
app = wx.App()
gui = GUIx("Demo")
gui.Show(True)
app.MainLoop()
