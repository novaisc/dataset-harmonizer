# stdlib
import glob
import os
import re
from typing import List, Tuple

# 3rd party
import xarray as xr
import pandas as pd
from pandas.core.groupby import DataFrameGroupBy

from dataset_harmonizer.config import DATE_PATTERN


class DatasetReader:
    def __init__(self, xarray_parameters: dict, combine_period: str):
        self.xarray_parameters = xarray_parameters
        self.combine = xarray_parameters.reader.combine
        self.data_vars = xarray_parameters.reader.data_vars
        self.combine_period = combine_period.lower()

    def read_grid_files(self, paths_df: pd.DataFrame) -> dict:
        datasets = {}
        group_per_variable = paths_df.groupby("variable")

        for var, group in group_per_variable:
            datasets[var] = self.__read_dataset(group["path"].tolist())

        return datasets

    def read_additional_files(self, paths: dict):
        datasets = {}

        for file_name, path in paths.items():
            datasets[file_name] = self.__read_dataset(path)

        return datasets

    def __read_dataset(self, path):
        ds = xr.open_mfdataset(
            path,
            combine=self.combine,
            data_vars=self.data_vars,
            decode_times=True,
            decode_timedelta=True,
        )

        return ds

    def __check_if_groups_have_the_same_amount_of_paths(self, groups: DataFrameGroupBy):
        for _, group in groups:
            variables_and_counts = group["variable"].value_counts()
            if variables_and_counts.nunique() != 1:
                raise ValueError(f"Mismatch in number of files per variable:\n {group}")

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
        return df

    def __group_paths_df(self, df: pd.DataFrame):
        if self.combine_period == "day":
            groups = df.groupby(["year", "month", "day"])
        elif self.combine_period == "month":
            groups = df.groupby(["year", "month"])
        elif self.combine_period == "year":
            groups = df.groupby(["year"])
        else:
            raise ValueError(f"Combine period {self.combine_period} is not day, month or year")

        self.__check_if_groups_have_the_same_amount_of_paths(groups)
        return groups

    def group_files_by_date_period(self, file_paths: dict[str, str]) -> list[pd.DataFrame]:
        var_paths = {var: sorted(glob.glob(path_pattern)) for var, path_pattern in file_paths.items()}

        df = self.__convert_paths_to_df(var_paths)
        groups = self.__group_paths_df(df)

        return groups
