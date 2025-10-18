from dataset_harmonizer.utils import create_directory

def save_dataset(ds, output_path):
    print("Saving combined dataset...")
    ds.to_netcdf(output_path)
    print("Combined dataset saved!")