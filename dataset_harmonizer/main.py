from dataset_harmonizer.dataset_utils import DatasetHandler
from dataset_harmonizer.reader import DatasetReader
from dataset_harmonizer.config import ConfigReader

from dataset_harmonizer.utils import save_dataset, create_path

from tqdm import tqdm

def open_func():
    import xarray as xr
    import os
    folder = "/home/caion/projects/rrg-pmyers-ad/caio/DatasetHarmonizer/output/x_116_430-y_520_750/2002/"
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".nc")]
    for file in files:
        ds = xr.open_dataset(file)
        ds.close()


def main(config_file: str):
    config = ConfigReader.from_yaml(config_file)

    dr = DatasetReader(
        xarray_parameters=config.xarray_parameters,
        combine_period=config.transformations.combine_period,
    )
    dh = DatasetHandler(
        interpolation=config.transformations.interpolation,
        combination=config.transformations.combination,
        renaming=config.transformations.renaming,
        attributes_to_add=config.transformations.attributes_to_add,
        coords_to_add=config.transformations.coords_to_add,
        slicing=config.transformations.slicing,
        keep=config.transformations.keep,
    )

    paths = config.input_data.data_paths
    path_groups = dr.group_files_by_date(paths)
    for _, path_group in tqdm(path_groups):
        datasets = dr.read_datasets(path_group)

        combined_ds = dh.create_combined_dataset(datasets)

        region_interest_x_0, region_interest_x_1 = config.transformations.slicing.region_of_interest["X"]
        region_interest_y_0, region_interest_y_1 = config.transformations.slicing.region_of_interest["Y"]

        year = path_group['year'].iloc[0]
        month = path_group['month'].iloc[0]
        day = path_group['day'].iloc[0]

        additional_folders = f"x_{region_interest_x_0}_{region_interest_x_1}-y_{region_interest_y_0}_{region_interest_y_1}/{year}"

        period = config.transformations.combine_period
        base_name = config.output.file_name

        patterns = {
            "day":   f"-y{year}m{month}d{day}",
            "month": f"-y{year}m{month}",
            "year":  f"-y{year}",
        }

        filename = f"{base_name}{patterns[period]}"

        output_path = create_path(
            directory=config.output.directory,
            file_name=filename,
            additional_folders=additional_folders,
        )

        save_dataset(combined_ds, output_path=output_path)

        combined_ds.close()
