from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class InputData:
    data_paths: dict


@dataclass
class VariableConfig:
    source_var: str
    dims_mapping: dict


@dataclass
class Interpolation:
    target_grid: str
    target_reference_variable: str
    variables: dict[str, VariableConfig]


@dataclass
class AttributesToAdd:
    file: dict
    variables: dict


@dataclass
class Slicing:
    region_of_interest: dict


@dataclass
class Keep:
    variables: list
    coords: list


@dataclass
class Transformations:
    combine_period: str
    interpolation: Interpolation
    combination: dict
    renaming: dict
    attributes_to_add: AttributesToAdd
    coords_to_add: dict
    slicing: Slicing
    keep: Keep


@dataclass
class Reader:
    combine: str
    data_vars: str


@dataclass
class XarrayParameters:
    engine: str
    reader: Reader
    chunks: dict


@dataclass
class Dataset:
    name: str


@dataclass
class Files:
    netcdf: str
    plot: str
    animation: str
    log: str

@dataclass
class Output:
    directory: str
    file_name: str

@dataclass
class ConfigReader:
    input_data: InputData
    transformations: Transformations
    xarray_parameters: XarrayParameters
    output: Output

    @classmethod
    def from_yaml(cls, path: str):
        path = Path(path)
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        variables = {k: VariableConfig(**v) for k, v in data["transformations"]["interpolation"]["variables"].items()}

        return cls(
            input_data=InputData(
                data_paths=data["input_data"]["data_paths"],
            ),
            transformations=Transformations(
                combine_period=data["transformations"]["combine_period"],
                interpolation=Interpolation(
                    data["transformations"]["interpolation"]["target_grid"],
                    data["transformations"]["interpolation"]["target_reference_variable"],
                    variables,
                ),
                combination=data["transformations"]["combination"],
                renaming=data["transformations"]["renaming"],
                attributes_to_add=AttributesToAdd(**data["transformations"]["attributes_to_add"]),
                coords_to_add=data["transformations"]["coords_to_add"],
                slicing=Slicing(**data["transformations"]["slicing"]),
                keep=Keep(**data["transformations"]["keep"]),
            ),
            xarray_parameters=XarrayParameters(
                engine=data["xarray"]["engine"],
                reader=Reader(**data["xarray"]["reader"]),
                chunks=data["xarray"]["chunks"],
            ),
            output=Output(**data["output"])
        )
