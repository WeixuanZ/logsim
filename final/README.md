This folder contains the code submission of the CUED GF2 project.

```
.
├── README.md
├── src
│   ├── devices.py
│   ├── exceptions.py
│   ├── gui.py
│   ├── gui_components.py
│   ├── locale
│   │   ├── logsim.pot
│   │   └── zh_CN
│   │       └── LC_MESSAGES
│   │           ├── logsim.mo
│   │           └── logsim.po
│   ├── logicgate.png
│   ├── logsim.py
│   ├── monitors.py
│   ├── names.py
│   ├── network.py
│   ├── parse.py
│   ├── scanner.py
│   ├── symbol_types.py
│   └── userint.py
└── tests
    ├── circuit1.txt
    ├── circuit2.txt
    ├── test_devices.py
    ├── test_integration.py
    ├── test_monitors.py
    ├── test_names.py
    ├── test_network.py
    ├── test_parse.py
    ├── test_scanner.py
    └── test_symbol_types.py
```

The software can be launched from source using

```shell
conda activate
python src/logsim.py  # launch GUI and open file explorer
python src/logsim.py tests/circuit1.txt  # launch GUI with file
python src/logsim.py -c tests/circuit2.txt  # launch command line interface
```

No extra dependency not already on the DPO system is required.

This program is also available in Simplified Chinese. If different from your
system language, you can launch `logsim` in Chinese using

```shell
LANG=zh_CN.utf8 python src/logsim.py
```

Alternatively, the software can also be launched from a self-contained
executable, which can be downloaded from
https://github.com/WeixuanZ/logsim/releases/download/v1.1.1/logsim-legacy.

```shell
wget -c https://github.com/WeixuanZ/logsim/releases/download/v1.1.1/logsim-legacy -O logsim
chmod +x ./logsim
./logsim  # launch GUI and open file explorer
./logsim tests/circuit1.txt  # launch GUI with file
./logsim -c tests/circuit2.txt  # launch command line interface
```

This is the more user-friendly way to use the software.
