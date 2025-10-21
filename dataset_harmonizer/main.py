from dataset_harmonizer.dataset_utils import DatasetHandler
from dataset_harmonizer.reader import DatasetReader
from dataset_harmonizer.config import ConfigReader

from dataset_harmonizer.utils import save_dataset, create_path


def main(config_file: str):
    config = ConfigReader.from_yaml(config_file)

    dr = DatasetReader(
        xarray_parameters=config.xarray_parameters,
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
    combined_pack_ds = dr.separate_files_per_specific_period(paths)
    for combined_paths in combined_pack_ds.values():
        datasets, date_pattern = dr.read_datasets(combined_paths)

        combined_ds = dh.create_combined_dataset(datasets)

        region_interest_x_0, region_interest_x_1 = config.transformations.slicing.region_of_interest["X"]
        region_interest_y_0, region_interest_y_1 = config.transformations.slicing.region_of_interest["Y"]

        additional_folders = f"x_{region_interest_x_0}_{region_interest_x_1}-y_{region_interest_y_0}_{region_interest_y_1}/{date_pattern['year']}"

        output_path = create_path(
            directory=config.output.directory, 
            file_name=config.output.file_name + f"-y{date_pattern['year']}m{date_pattern['month']}d{date_pattern['day']}", 
            additional_folders=additional_folders
        )
        save_dataset(combined_ds, output_path=output_path)

        combined_ds.close()
