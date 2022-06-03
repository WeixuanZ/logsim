#!/usr/bin/env python3
"""Parse command line options and arguments for the Logic Simulator.

This script parses options and arguments specified on the command line, and
runs either the command line user interface or the graphical user interface.

Usage
-----
Show help: logsim.py -h
Command line user interface: logsim.py -c <file path>
Graphical user interface: logsim.py [<file path>]
"""
import getopt
from pathlib import Path
import sys
import wx
from os import environ

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from userint import UserInterface
from gui import Gui
from exceptions import Errors

_ = wx.GetTranslation


def _displayHook(obj):
    if obj is not None:
        print(repr(obj))


class App(wx.App):
    """The app."""

    locale = None
    SUPPORTED_LANGS = {
        "default": wx.LANGUAGE_DEFAULT,
        "zh_CN": wx.LANGUAGE_CHINESE_SIMPLIFIED,
    }

    def OnInit(self):
        """Initialize the app."""
        sys.displayhook = _displayHook
        lang_encode = environ.get("LANG")
        if lang_encode is not None:
            lang = lang_encode.split(".")[0]
            if lang not in App.SUPPORTED_LANGS:
                lang = "default"
        else:
            lang = "default"

        self.appName = "Logic simulator"

        wx.Locale.AddCatalogLookupPathPrefix(
            str(Path(__file__).resolve().with_name("locale"))
        )
        self.locale = wx.Locale()
        self.locale.Init(App.SUPPORTED_LANGS[lang])
        self.locale.AddCatalog("logsim")

        return True


def main(arg_list):
    """Parse the command line options and arguments specified in arg_list.

    Run either the command line user interface, the graphical user interface,
    or display the usage message.
    """
    usage_message = (
        "Usage:\n"
        "Show help: logsim.py -h\n"
        "Command line user interface: logsim.py -c <file path>\n"
        "Graphical user interface: logsim.py [<file path>]"
    )
    try:
        options, arguments = getopt.getopt(arg_list, "hc:")
    except getopt.GetoptError:
        print("Error: invalid command line arguments\n")
        print(usage_message)
        sys.exit()

    # Initialise instances of the four inner simulator classes
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    for option, path in options:
        if option == "-h":  # print the usage message
            print(usage_message)
            sys.exit()
        elif option == "-c":  # use the command line user interface
            errors = Errors()
            scanner = Scanner(path, names, errors)
            parser = Parser(names, devices, network, monitors, scanner, errors)
            parser.parse_network()
            if parser.errors.error_counter > 0:
                parser.errors.print_error_messages(names, scanner)
                return
            # Initialise an instance of the userint.UserInterface() class
            userint = UserInterface(names, devices, network, monitors)
            userint.command_interface()

    if not options:  # no option given, use the graphical user interface
        path = None

        if len(arguments) == 1:  # wrong number of arguments
            [path] = arguments
            errors = Errors()
            scanner = Scanner(path, names, errors)
            parser = Parser(names, devices, network, monitors, scanner, errors)
            parser.parse_network()
            if parser.errors.error_counter > 0:
                parser.errors.print_error_messages(names, scanner)
                return

        app = App()
        gui = Gui(
            _("Logic Simulator"), path, names, devices, network, monitors
        )
        gui.Show(True)
        app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])
