from dataset_harmonizer.utils import create_directory
import xarray as xr


def save_dataset(ds: xr.Dataset, output_path):
    print(f"Saving dataset in path {output_path}")
    ds = ds.chunk({"time_counter": -1})
    # encoding = {
    #     var: {"chunksizes": ds[var].data.chunksize}
    #     for var in ds.data_vars
    # }

    ds.to_netcdf(output_path)
    print("Combined dataset saved!")
