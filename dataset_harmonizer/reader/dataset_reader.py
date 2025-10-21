# stdlib
import glob
import os
import re

# 3rd party
import xarray as xr


class DatasetReader:
    def __init__(self, xarray_parameters: dict):
        self.xarray_parameters = xarray_parameters

    def read_paths_and_files(self, data_paths):
        datasets = {}
        reader_params = self.xarray_parameters.reader
        combine = reader_params.combine
        data_vars = reader_params.data_vars

        for var, pattern in data_paths.items():
            paths = sorted(glob.glob(pattern))
            if not paths:
                raise FileNotFoundError(f"No files found for variable '{var}' with pattern '{pattern}'")
            datasets[var] = xr.open_mfdataset(
                paths, combine=combine, data_vars=data_vars, decode_times=True, decode_timedelta=True
            )

        return datasets

    def read_datasets(self, data_paths: dict) -> dict:
        reader_params = self.xarray_parameters.reader
        combine = reader_params.combine
        data_vars = reader_params.data_vars

        datasets = {}
        for var, path in data_paths.items():
            if not os.path.exists(path):
                raise FileNotFoundError(f"File not found for variable '{var}' at path: {path}")

            datasets[var] = xr.open_mfdataset(
                path, combine=combine, data_vars=data_vars, decode_times=True, decode_timedelta=True
            )

        first_string = next(iter(data_paths.values()))
        year_month_day = re.search("y....m..d..", first_string).group()
        date_pattern = {
            "year": year_month_day[1:5],
            "month": year_month_day[6:8],
            "day": year_month_day[9:11],
        }

        return datasets, date_pattern

    def read_single_file(self, path) -> xr.Dataset:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found at path: {path}")
        ds = xr.open_dataset(path)
        return ds

    def get_files_list(self, pattern: str):
        files = sorted(glob.glob(pattern))
        if not files:
            raise FileNotFoundError(f"No files found with pattern '{pattern}'")
        return files

    def separate_files_per_specific_period(self, file_paths: list):
        var_paths = {}
        for var, path in file_paths.items():
            var_paths[var] = sorted(glob.glob(path))

        combined_pack_paths = {}

        paths_length = len(next(iter(var_paths.values())))

        for i in range(paths_length):
            combined_pack_paths[i] = {var: var_paths[var][i] for var in var_paths.keys()}

        return combined_pack_paths
