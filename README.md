# STF Azure tools

This repository contains `azuretools`, a lightweight Python library of helper tooling to enable CFA Predict Short-Term Forecasting team members interact more efficiently with Azure, particularly Azure Batch. It also contains some simple worked examples in the `examples/` directory.

## Installation

This installation guide assumes you are working on a Debian/Ubuntu family Linux machine or in an equivalent virtual machine (e.g. a WSL2 Ubuntu from Windows). It assumes you are comfortable working at the Unix command line. It assumes you have Python 3 installed as your system `python`, as well as the standard `pip` package manager. Confirm this with:

```bash
python --version
which pip
```

You can install `azuretools` from Github via:

```bash
pip install git+https://github.com/cdcent/cfa-azuretools
```

## Projects that use `azuretools`
One way to get a sense of `azuretools` is to look at projects that use it. Here are a few:

#### [Pyrenew-HEW: Multi-signal renewal modeling](https://github.com/cdcgov/pyrenew-hew)
- Most relevant python scripts live in the [`pipelines/batch`](https://github.com/CDCgov/pyrenew-hew/tree/main/pipelines/batch) subdirectory

#### [Wastewater-informed COVID Forecasting](https://github.com/cdcgov/wastewater-informed-covid-forecasting)
- Currently [getting refactored to use `azuretools`](https://github.com/CDCgov/wastewater-informed-covid-forecasting/pull/230)

### Your project?
- Let us know if you have a project that uses `azuretools` that you'd like us to showcase here.
