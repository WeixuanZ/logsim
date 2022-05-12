# logsim

## Development

Install `pre-commit` using `pip` and install the hooks using
```shell
pre-commit install
```

Run tests using
```shell
make test
```

### Installing Dependencies

#### macOS

Create and activate a virtual environment, then use 
```shell
pip install -r requirements.txt
```

#### Linux

There are no pre-built wheels for `wxpython` on `pip`. For Ubuntu 20.04, can install the dependencies using
```shell
apt-get update && apt-get install --no-install-recommends -y python3.9 python3.9-dev python3-pip python3-opengl python3-wxgtk4.0 freeglut3-dev
```
Alternatively, can build at `pip` install
```shell
apt update && apt install --no-install-recommends -y make gcc libgtk-3-dev freeglut3 freeglut3-dev
pip install -r requirements.txt
```
Conda can also be used.
