# stdlib
import glob
import os
import re

# 3rd party
import xarray as xr
import pandas as pd

from dataset_harmonizer.config import DATE_PATTERN


class DatasetReader:
    def __init__(self, xarray_parameters: dict, combine_period: str):
        self.xarray_parameters = xarray_parameters
        self.combine_period = combine_period.lower()

    def read_datasets(self, paths_df: pd.DataFrame) -> dict:
        reader_params = self.xarray_parameters.reader
        combine = reader_params.combine
        data_vars = reader_params.data_vars

        datasets = {}
        group_per_variable = paths_df.groupby("variable")

        for var, group in group_per_variable:
            datasets[var] = xr.open_mfdataset(
                group["path"].tolist(),
                combine=combine,
                data_vars=data_vars,
                decode_times=True,
                decode_timedelta=True,
                # chunks=self.xarray_parameters.chunks,
            )

        return datasets

    def __check_amount_of_paths(self, var_paths: dict):
        lengths = {var: len(paths) for var, paths in var_paths.items()}
        unique_lengths = set(lengths.values())

        if len(unique_lengths) != 1:
            msg = "Mismatch in number of files per variable:\n" + "\n".join(
                f"  {var}: {count}" for var, count in lengths.items()
            )
            raise ValueError(msg)

    def __convert_paths_to_df(self, var_paths: dict) -> tuple:
        df = pd.DataFrame(columns=["path", "variable", "year", "month", "day"])
        for key, paths in var_paths.items():
            for path in paths:
                file_name = os.path.basename(path)
                
                if not re.search(DATE_PATTERN, file_name):
                    raise ValueError(f"File '{file_name}' does not contain a valid date (yYYYYmMMdDD).")

                match_year = re.search(r"(?<=y)\d{4}", file_name)
                match_month = re.search(r"(?<=m)\d{2}", file_name)
                match_day = re.search(r"(?<=d)\d{2}", file_name)

                df.loc[len(df)] = {
                    "variable": key,
                    "path": path,
                    "year": match_year.group(),
                    "month": match_month.group(),
                    "day": match_day.group(),
                }

        if self.combine_period == "day":
            groups = df.groupby(["year", "month", "day"])
        elif self.combine_period == "month":
            groups = df.groupby(["year", "month"])
        elif self.combine_period == "year":
            groups = df.groupby(["year"])
        else:
            raise ValueError(f"Combine period {self.combine_period} is not day, month or year")

        return groups

    def group_files_by_date(self, file_paths: dict[str, str]) -> list[pd.DataFrame]:
        var_paths = {var: sorted(glob.glob(path_pattern)) for var, path_pattern in file_paths.items()}

        self.__check_amount_of_paths(var_paths)

        groups = self.__convert_paths_to_df(var_paths)

        return groups
