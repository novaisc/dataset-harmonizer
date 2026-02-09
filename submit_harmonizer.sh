#!/bin/bash
#SBATCH --account=rrg-pmyers-ad
#SBATCH --mem-per-cpu=32000M
#SBATCH --time=1-00:00

module load StdEnv/2020 gcc/9.3.0 openmpi/4.0.3 python/3.10.2 mpi4py/3.1.3 hdf5-mpi/1.12.1 arrow/13.0.0 netcdf-mpi/4.9.0 proj/9.0.1 scipy-stack/2023b
source /home/caion/venvs/env/bin/activate

# module load StdEnv/2023 gcc/14.3 openmpi/5.0.8 hdf5-mpi/1.14.6 proj/9 python/3.12 scipy-stack arrow/21 mpi4py
# source /home/caion/venvs/caio_opendrift/bin/activate

python app.py

