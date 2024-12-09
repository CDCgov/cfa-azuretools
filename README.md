# STF Azure tools

This repository contains `azuretools`, a lightweight Python library of helper tooling to enable CFA Predict Short-Term Forecasting team members interact more efficiently with Azure, particularly Azure Batch. It also contains some simple worked examples in the `examples/` directory.

## Installation

This installation guide assumes you are working on a Debian/Ubuntu family Linux machine or in an equivalent virtual machine (e.g. a WSL2 Ubuntu from Windows). It assumes you are comfortable working at the Unix command line. It assumes you have Python 3 installed as your system `python`, as well as the standard `pip` package manager. Confirm this with:

```bash
python --version
which pip
```

Provided you are authenticated to `cdcent` at the command line, you can install `azuretools` from Github via:

```bash
pip install git+https://github.com/cdcent/cfa-stf-azuretools
```
