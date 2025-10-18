# Dataset Harmonizer

A Python tool for harmonizing oceanographic NetCDF datasets.  
It allows interpolation of variables to a common grid, combination of multiple datasets, renaming of variables and coordinates, adding attributes, and subsetting data for a region of interest. This is particularly useful for NEMO ocean model outputs and preparing data for tools like OpenDrift.

---

## Features

- Interpolates variables from different grids (U, V, W) to a common target grid (T grid by default).
- Combines multiple datasets into a single harmonized dataset.
- Renames variables and coordinates to standardized names.
- Adds file and variable attributes for CF-compliance and documentation.
- Subsets data to a region of interest.
- Fully configuration-driven using a YAML file.

---

## Installation

### Using pip (recommended for virtual environments)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

The program is entirely driven by the configuration file `parameters.yaml`.
You do **not** need to modify the code to run it on your own datasets. All processing steps—interpolation, combination, renaming, adding attributes, and subsetting—are controlled from this file.

Key sections in `parameters.yaml`:

* `input_data`: Paths to input NetCDF files (supports glob patterns).

* `transformations`:

  * `interpolation`: Define which variables to interpolate to the target grid.
  * `combination`: Define other datasets and variables to merge into the combined dataset.
  * `renaming`: Standardize variable and coordinate names.
  * `attributes_to_add`: File-level and variable-level attributes.
  * `coords_to_add`: Coordinates to assign to variables.
  * `slicing`: Define the region of interest to subset.
  * `keep`: List of variables and coordinates to keep in the final dataset.

* `xarray`: Options for reading NetCDF files with `xarray`.

* `output`: Output directory and file name for the harmonized dataset.

## Usage

1. Prepare your input NetCDF datasets.

2. Open `parameters.yaml` and edit paths, variables, and transformation settings as needed.

3. Run the program:

```bash
python app.py
```
4. The harmonized dataset will be saved to the folder specified in the configuration (output.directory).

