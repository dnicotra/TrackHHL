# TrackHHL

This repository contains an implementation of a track reconstruction algorithm using the HHL quantum algorithm, described in [this article](https://arxiv.org/abs/2308.00619).

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8192122.svg)](https://zenodo.org/doi/10.5281/zenodo.8192122)



# Installation

This project uses [Poetry](https://python-poetry.org/) to manage dependencies. After installing it, clone this repo and install the dependencies in a virtual environment using Poetry.
```console
git clone https://github.com/dnicotra/TrackHHL.git
cd TrackHHL
poetry install
```
You can then run your own script with
```console
poetry run python your_script.py
```
or activate the environment in your shell with
```console
poetry shell
```

# Description

- `notebooks\`: contains a few IPython notebooks that show the usage of the code
- `tests\`: contains several automatic tests
- `trackhhl\`: the main library
  - `event_model\`: contains the data-models `Hit`, `Module`, `Track`, `Event`, `Segment` and `MCInfo`
  - `hamiltonians\`: contains the abstract class `Hamiltonian` and the implementation of the `SimpleHamiltonian` used in the article. The `SimpleHamiltonian` class can be used to solve a tracking problem using a classical linear solver (with the method `solve_classically`) or using the Qiskit implementation of the HHL algorithm (with the method `solve_hhl`). Check `notebooks\example.ipynb` for the basic usage.
  - `toy\`: contains the toy-model used for numerical simulations in the article
