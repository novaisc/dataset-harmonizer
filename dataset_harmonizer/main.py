from dataset_harmonizer.dataset_utils import DatasetHandler
from dataset_harmonizer.reader import DatasetReader
from dataset_harmonizer.config import ConfigReader

from dataset_harmonizer.utils import save_dataset, create_path


def read_data(config: ConfigReader):
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
    datasets = dr.read_multi_files(config.input_data.data_paths)
    return dh, datasets


def main(config_file: str):
    config = ConfigReader.from_yaml(config_file)
    dh, datasets = read_data(config)

    combined_ds = dh.create_combined_dataset(datasets)

    output_path = create_path(config.output.directory, config.output.file_name)
    save_dataset(combined_ds, output_path=output_path)
