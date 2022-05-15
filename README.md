# logsim

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


### Building Documentation

This project uses [Numpy style docstrings](https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard),
the documentation is built with Sphinx.
Each push to `master` will trigger a build and deploy Action to https://weixuanz.github.io/logsim/.

To build locally, use

```shell
make docs
```
