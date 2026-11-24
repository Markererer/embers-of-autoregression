#!/bin/bash
#SBATCH --job-name=seminars_autoregression
#SBATCH --output=/home/seminar_group5/joblogs_joke/seminars_autoregression_out%j.out
#SBATCH --error=/home/seminar_group5/joblogs_joke/seminars_autoregression_error%j.err
#SBATCH --cpus-per-task=10
#SBATCH --nodes=1
#SBATCH --nodelist=asus1
#SBATCH --time=08:30:00
#SBATCH --partition=asus1

set -e
set -x

echo "START: $(date)"
cd /temp
mkdir -p group5_MY_OWN_MINICONDA_MARCH26
mkdir -p group5_CACHE_MY_OWN_MINICONDA_MARCH26
mkdir -p group5_tmp
export CONDA_PKGS_DIRS=/temp/group5_CACHE_MY_OWN_MINICONDA_MARCH26
export TMPDIR=/temp/group5_tmp
export TMP_DIR=/temp/group5_tmp
export TMP=/temp/group5_tmp
export TEMP=/temp/group5_tmp
export PIP_CACHE_DIR=/temp/group5_CACHE_MY_OWN_MINICONDA_MARCH26



cd group5_MY_OWN_MINICONDA_MARCH26

wget https://repo.anaconda.com/miniconda/Miniconda3-py312_26.1.1-1-Linux-aarch64.sh

bash Miniconda3-py312_26.1.1-1-Linux-aarch64.sh -b -p /temp/group5_MY_OWN_MINICONDA_MARCH26/Miniconda3-py312_26.1.1-1-Linux-aarch64

echo "miniconda is installed"

source /temp/group5_MY_OWN_MINICONDA_MARCH26/Miniconda3-py312_26.1.1-1-Linux-aarch64/etc/profile.d/conda.sh

conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main 
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
conda create -y -p /temp/group5_MY_OWN_MINICONDA_MARCH26/Miniconda3-py312_26.1.1-1-Linux-aarch64/envs/newpy_pip python=3.12

conda activate /temp/group5_MY_OWN_MINICONDA_MARCH26/Miniconda3-py312_26.1.1-1-Linux-aarch64/envs/newpy_pip

echo "pip installing"

pip install -r /home/seminar_group5/embers-of-autoregression_joke/requirements.txt

echo "testing the environment"

python3 - << 'EOF'
import torch
print("Torch version:", torch.__version__)
EOF

cd /temp
cp -r /home/seminar_group5/embers-of-autoregression_joke .
cd /temp/embers-of-autoregression_joke
./experiment_commands.sh
cp -r ./logs /home/seminar_group5/embers-of-autoregression_joke/logs
cd /temp
echo "FINISH: $(date)"

echo "DONE"

cd ..
rm -rf /temp/embers-of-autoregression_joke
rm -rf group5_tmp
rm -rf group5_MY_OWN_MINICONDA_MARCH26
rm -rf group5_CACHE_MY_OWN_MINICONDA_MARCH26
echo "DONE DONE DONE"