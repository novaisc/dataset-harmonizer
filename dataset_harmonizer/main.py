from dataset_harmonizer.dataset_utils import DatasetHandler
from dataset_harmonizer.reader import DatasetReader
from dataset_harmonizer.config import ConfigReader

from dataset_harmonizer.utils import save_dataset, create_path

from tqdm import tqdm


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

    grid_paths = config.input_data.grid_file_paths
    additional_paths = config.input_data.additional_paths

    path_groups = dr.group_files_by_date_period(grid_paths)

    additional_datasets = dr.read_additional_files(additional_paths)

    for _, path_group in tqdm(path_groups):
        grid_datasets = dr.read_grid_files(path_group)

        combined_ds = dh.create_combined_dataset(grid_datasets, additional_datasets)

        region_interest_x_0, region_interest_x_1 = config.transformations.slicing.region_of_interest["X"]
        region_interest_y_0, region_interest_y_1 = config.transformations.slicing.region_of_interest["Y"]

        year = path_group["year"].iloc[0]
        month = path_group["month"].iloc[0]
        day = path_group["day"].iloc[0]

        period = config.transformations.combine_period
        base_name = config.output.file_name

        additional_folders = f"x_{region_interest_x_0}_{region_interest_x_1}-y_{region_interest_y_0}_{region_interest_y_1}/"

        patterns = {
            "day": f"-y{year}m{month}d{day}",
            "month": f"-y{year}m{month}",
            "year": f"-y{year}",
        }

        filename = f"{base_name}{patterns[period]}"

        output_path = create_path(
            directory=config.output.directory,
            file_name=filename,
            additional_folders=additional_folders,
        )

        save_dataset(combined_ds, output_path=output_path)

        combined_ds.close()
