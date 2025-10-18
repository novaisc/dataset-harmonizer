# stdlib
import glob
import os

# 3rd party
import xarray as xr


class DatasetReader:
    def __init__(self, xarray_parameters: dict):
        self.xarray_parameters = xarray_parameters

    def read_multi_files(self, data_paths):
        datasets = {}
        reader_params = self.xarray_parameters.reader
        combine = reader_params.combine
        data_vars = reader_params.data_vars

        for var, pattern in data_paths.items():
            paths = glob.glob(pattern)
            if not paths:
                raise FileNotFoundError(f"No files found for variable '{var}' with pattern '{pattern}'")
            datasets[var] = xr.open_mfdataset(paths, combine=combine, data_vars=data_vars)

        return datasets

    def read_single_file(self, path) -> xr.Dataset:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found at path: {path}")
        ds = xr.open_dataset(path)
        return ds