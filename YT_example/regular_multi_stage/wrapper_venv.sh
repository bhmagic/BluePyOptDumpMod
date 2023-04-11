#!/bin/sh

#module purge
#module load slurm
#module load gcc
#module load openmpi
#module load python39

. /home/wuy2/MET/bin/activate




#. /home/wuy2/.bash_profile
#conda activate MET


python $@

