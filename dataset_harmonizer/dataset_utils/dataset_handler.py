from typing import List
from time import time

import xarray as xr
import numpy as np


class DatasetHandler:
    def __init__(self, interpolation, combination, renaming, attributes_to_add, coords_to_add, slicing, keep):
        self.target_grid = interpolation.target_grid
        self.target_reference_variable = interpolation.target_reference_variable
        self.interpolation_variables = interpolation.variables
        self.combination = combination
        self.renaming_map = renaming
        self.region_of_interest = slicing.region_of_interest
        self.vars_to_keep = keep.variables
        self.coords_to_keep = keep.coords
        self.file_attributes_to_add = attributes_to_add.file
        self.variable_attributes_to_add = attributes_to_add.variables
        self.coords_to_add = coords_to_add
        self.region_of_interest = slicing.region_of_interest

    def __select_subset_of_data(self, ds: xr.Dataset) -> xr.Dataset:
        variables_mapping = {key: slice(start, end) for key, (start, end) in self.region_of_interest.items()}
        ds = ds.isel(
            **variables_mapping,
        )

        return ds

    def __clean_dataset(self, ds: xr.Dataset) -> xr.Dataset:
        vars_to_drop = [v for v in ds.data_vars if v not in self.vars_to_keep]
        ds = ds.drop_vars(vars_to_drop)

        coords_to_drop = [c for c in ds.coords if c not in self.coords_to_keep]
        ds = ds.drop_vars(coords_to_drop)

        return ds

    def interpolate(self, da: xr.DataArray, dimension_slice_start: dict, dimension_slice_end: dict) -> xr.DataArray:
        interpolated_array = 0.5 * (da.isel(**dimension_slice_start) + da.isel(**dimension_slice_end))
        return interpolated_array

    def __fill_values(self, arr: xr.DataArray, dimension: str, target_dim_size: int) -> xr.DataArray:
        times_to_add = target_dim_size - arr[dimension].size

        if times_to_add <= 0:
            return arr

        last_col = arr.isel({dimension: -1})
        repeats = [last_col] * times_to_add
        arr = xr.concat([arr, *repeats], dim=dimension)

        return arr

    def __add_attributes(self, ds: xr.Dataset) -> xr.Dataset:
        for attr, value in self.file_attributes_to_add.items():
            ds.attrs[attr] = value

        for var, attrs in self.variable_attributes_to_add.items():
            if var in ds:
                for attr, value in attrs.items():
                    ds[var].attrs[attr] = value

        return ds

    def __add_coords(self, ds: xr.Dataset) -> xr.Dataset:
        for var, coords in self.coords_to_add.items():
            if var in ds:
                for coord in coords:
                    ds[var] = ds[var].assign_coords({coord: ds[coord]})
        return ds

    def __rename_variables(self, ds: xr.Dataset) -> xr.Dataset:
        variables_to_remove = []
        for var in self.renaming_map.keys():
            if (var not in ds) and (var not in ds.coords) and (var not in ds.dims):
                print(f"WARNING: Variable '{var}' not found in dataset for renaming. Removing from renaming map...")
                variables_to_remove.append(var)

        for var in variables_to_remove:
            self.renaming_map.pop(var)

        return ds.rename(self.renaming_map)

    def __pop_datasets(self, datasets: List[xr.Dataset], datasets_to_pop: List[str]):
        for var in datasets_to_pop:
            datasets.pop(var)

    def __run_interpolation(self, datasets: List[xr.Dataset]):
        target_ds = datasets[self.target_grid]
        datasets_to_pop = set()

        for grid_name, ds in datasets.items():
            if (grid_name == self.target_grid) or (grid_name not in self.interpolation_variables):
                continue

            for source_var_and_dims_mapping_dict in self.interpolation_variables[grid_name]:
                source_var = source_var_and_dims_mapping_dict["source_var"]
                dims_mapping = source_var_and_dims_mapping_dict["dims_mapping"]
                variable_dim, target_dim = next(iter(dims_mapping.items()))
                dimension_slice_start = {variable_dim: slice(0, -1)}
                dimension_slice_end = {variable_dim: slice(1, None)}

                interpolated_data_array = self.interpolate(
                    da=ds[source_var],
                    dimension_slice_start=dimension_slice_start,
                    dimension_slice_end=dimension_slice_end,
                )

                interpolated_data_array = self.__fill_values(
                    interpolated_data_array, variable_dim, target_ds[target_dim].size
                )

                target_ds[source_var] = xr.DataArray(
                    interpolated_data_array,
                    dims=target_ds[self.target_reference_variable].dims,
                    coords=target_ds[self.target_reference_variable].coords,
                )

                datasets_to_pop.add(grid_name)

        return datasets_to_pop

    def __unify_datasets(self, datasets: List[xr.Dataset]) -> xr.Dataset:
        combined_ds = datasets[self.target_grid]

        if self.combination is None:
            return combined_ds

        for dataset in self.combination.keys():
            if dataset == self.target_grid:
                print("WARNING: Target grid cannot be in combination section.")
                continue
            if dataset not in datasets:
                print(f"WARNING: Dataset '{dataset}' not found for combination. Skipping...")
                continue

            data_variables = self.combination[dataset]["variables"]

            for var in data_variables:
                if var not in datasets[dataset]:
                    raise ValueError(f"Variable '{var}' not found in dataset '{dataset}' for combination.")

                da = datasets[dataset][var]

                if data_variables[var] is not None:
                    da = da.rename(data_variables[var]["dims_mapping"])

                combined_ds[var.lower()] = da

        return combined_ds

    def __convert_dim_size(self, ds):
        for dim in ["X", "Y"]:
            ds[dim] = ds[dim].astype("int32")
        return ds

    # TODO: make this function generic
    def __add_mesh_file(self, ds, additional_datasets):
        mask_ds = additional_datasets["mask"]
        ds["nav_lat_grid_T"] = mask_ds["nav_lat"]
        ds["nav_lon_grid_T"] = mask_ds["nav_lon"]
        ds["nav_lat_grid_T"] = ds["nav_lat_grid_T"].rename({"y": "y_grid_T", "x": "x_grid_T"})
        ds["nav_lon_grid_T"] = ds["nav_lon_grid_T"].rename({"y": "y_grid_T", "x": "x_grid_T"})
        ds["mbathy"] = mask_ds["mbathy"]
        ds["tmask"] = mask_ds["tmask"]
        ds["mbathy"] = ds["mbathy"].rename({"y": "y_grid_T", "x": "x_grid_T"})
        ds["tmask"] = 1 - ds["tmask"]
        ds["tmask"] = ds["tmask"].rename({"y": "y_grid_T", "x": "x_grid_T"}).isel(t=0, z=0)

        # ds["votemper"] = ds["votemper"].fillna(-0)
        # ds["vosaline"] = ds["vosaline"].fillna(-0)
        # ds["vomecrty"] = ds["vomecrty"].fillna(-0)
        # ds["vozocrtx"] = ds["vozocrtx"].fillna(-0)
        # ds["vovecrtz"] = ds["vovecrtz"].fillna(-0)
        # ds["sohmld"] = ds["sohmld"].fillna(-0)
        # ds["sossheig"] = ds["sossheig"].fillna(-0)

        return ds

    def create_combined_dataset(self, grid_datasets: dict, additional_datasets: dict) -> xr.Dataset:
        start = time()
        print("Starting interpolation...")
        datasets_to_pop = self.__run_interpolation(grid_datasets)
        end = time()
        print(f"Interpolation took {end - start} seconds")

        self.__pop_datasets(grid_datasets, datasets_to_pop)

        start = time()
        print("Starting dataset unification...")
        ds = self.__unify_datasets(grid_datasets)
        end = time()
        print(f"Dataset unification took {end - start} seconds")

        start = time()
        print("Starting mesh addition...")
        ds = self.__add_mesh_file(ds, additional_datasets)
        end = time()
        print(f"Mesh addition took {end - start} seconds")

        start = time()
        print("Starting renaming...")
        ds = self.__rename_variables(ds)
        end = time()
        print(f"Renaming took {end - start} seconds")

        start = time()
        print("Starting adding attributes...")
        ds = self.__add_attributes(ds)
        end = time()
        print(f"Adding attributes took {end - start} seconds")

        start = time()
        print("Starting adding coords...")
        ds = self.__add_coords(ds)
        end = time()
        print(f"Adding coords took {end - start} seconds")

        start = time()
        print("Starting cleaning dataset...")
        ds = self.__clean_dataset(ds)
        end = time()
        print(f"Dataset cleaning took {end - start} seconds")

        start = time()
        print("Starting subset selection...")
        ds = self.__select_subset_of_data(ds)
        end = time()
        print(f"Subset selection took {end - start} seconds")

        ds = self.__convert_dim_size(ds)

        return ds
