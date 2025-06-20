#!/bin/bash
#SBATCH --job-name=datalad_hcp2
#SBATCH --partition=mit_normal
#SBATCH --output=./logs/datalad_%A_%a.out
#SBATCH --error=./logs/datalad_%A_%a.err
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=10G
#SBATCH --array=0-183
#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=wilke18@mit.edu

echo "Sourcing bashrc"
source $HOME/.bashrc

#sub_ids=("sub-01" "sub-02" "sub-03" "sub-04" "sub-05" "sub-06")

sub_index=$SLURM_ARRAY_TASK_ID

#TASK_ID=${sub_ids[$sub_index]}

echo "Processing: ${sub_index}"

# Run first script
#echo "Activating environment for first script..."
#mamba activate glmsingle
#if ! python hcptrt_GLMsingle_localizer_emotion.py "${TASK_ID}"; then
#    echo "First script failed! Exiting..."
#    mamba deactivate
#    exit 1
#fi
#mamba deactivate
echo "Activating conda"
conda activate thesis

echo "Running parcellate.py"
python run_datalad.py --file_num ${sub_index}

# # Only reach here if both scripts succeeded
# echo "Both scripts succeeded. Starting data transfer..."
# dest_dir="/orcd/data/satra/001/users/yibei/hcptrt/output/GLMsingle/results_v2/${TASK_ID}/"
# mkdir -p "$dest_dir"
# rsync -avz --ignore-existing /orcd/scratch/bcs/001/yibei/hcptrt/output/GLMsingle/results_v2/${TASK_ID}/ "$dest_dir"

# echo "All operations completed successfully!"
