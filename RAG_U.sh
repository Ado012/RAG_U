#!/bin/bash
#SBATCH -p samplecluster
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time 30:00:00
#SBATCH --mem=50GB
#SBATCH --job-name RemoteWSynopsis
#SBATCH --mail-user=sample@sample.com
#SBATCH --mail-type=ALL
#SBATCH --output=my.stdout

# start summerizing
source ./venv/bin/activate

module load cuda/11.7

python ./main.py 


deactivate
