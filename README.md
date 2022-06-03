# logsim

Executables can be downloaded from
https://github.com/WeixuanZ/logsim/releases/latest.

This program is also available in Simplified Chinese. If different from your
system language, you can launch `logsim` in Chinese using

```shell
LANG=zh_CN.utf8 ./logsim
```

## Logic Description Language

In Extended Backus Naur Form (EBNF)
```
circuit = devices , connections , [ monitor ] ;
devices = "DEVICES" , ":" , device_definition , { device_definition } ;
connections = "CONNECTIONS" , ":" , connection , { connection } ;
monitor = "MONITORS" , ":" , [ monitor_statement ] ;

device_definition = device_name , { "," , device_name } , "=" , device_type , ";" ;

letter = "A" | "B" | "C" | "D" | "E" | "F" | "G"
       | "H" | "I" | "J" | "K" | "L" | "M" | "N"
       | "O" | "P" | "Q" | "R" | "S" | "T" | "U"
       | "V" | "W" | "X" | "Y" | "Z" | "a" | "b"
       | "c" | "d" | "e" | "f" | "g" | "h" | "i"
       | "j" | "k" | "l" | "m" | "n" | "o" | "p"
       | "q" | "r" | "s" | "t" | "u" | "v" | "w"
       | "x" | "y" | "z" ;
digit_excluding_zero = "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
digit = "0" | digit excluding zero ;

device_name = ( letter | "_" ) , { letter | digit | "_" } ;

device_type = ( "CLOCK", parameter )
            | ( "SWITCH", "<" , ( "0" | "1" ) , ">" )
            | ( ( "AND" | "NAND" | "OR" | "NOR" ), parameter )
            | "XOR"
            | "D_TYPE" ;
parameter = "<" , digit , { digit } , ">" ;

connection = pin , "-" , pin , ";" ;
pin = ( in_pin | out_pin ) ;
in_pin = ( device_name , "." , "I" , digit_excluding_zero , [ digit ] )
       | ( device_name , "." , ( "DATA" | "CLK" | "SET" | "CLEAR" ) ) ;
out_pin = device_name | ( device_name , "." , ( "Q" | "QBAR" ) ) ;

monitor_statement = pin , { "," , pin } , ";" ;
```

Examples are available in `tests/`.

## Development

Install `pre-commit` using `pip` and install the hooks using
```shell
pre-commit install
```
This will enable auto-formatting and linting before committing.

Run tests using
```shell
make test
```

Check test coverage using
```shell
make coverage
```

### Installing Dependencies

#### macOS

Create and activate a virtual environment, then use
```shell
pip install -r requirements.txt
```

#### Linux

There are no pre-built wheels for `wxpython` on `pip`. For Ubuntu 20.04, can
install the dependencies using

```shell
apt-get update && apt-get install --no-install-recommends -y python3.9 python3.9-dev python3-pip python3-opengl python3-wxgtk4.0 freeglut3-dev
```

Alternatively, can build at `pip` install

```shell
apt update && apt install --no-install-recommends -y make gcc libgtk-3-dev freeglut3 freeglut3-dev
pip install -r requirements.txt
```

Conda can also be used.


### Building Documentation

This project uses [Numpy style
docstrings](https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard),
the documentation is built with Sphinx.  Each push to `master` will trigger
a build and deploy Action to https://weixuanz.github.io/logsim/.

To build locally, use

```shell
make docs
```


### Building Executable

Executables can be built with `pyinstaller` using

```shell
make build
```

For details of dependencies required for building, please have a look at the
build GitHub Action config.
