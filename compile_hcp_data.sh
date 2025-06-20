#!/bin/bash
#SBATCH --job-name=compile_hcp
#SBATCH --partition=mit_normal
#SBATCH --output=./logs/compile_%A.out
#SBATCH --error=./logs/compile_%A.err
#SBATCH --time=02:00:00
#SBATCH --mem=10G
#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=wilke18@mit.edu

echo "Sourcing bashrc"
source $HOME/.bashrc

#sub_ids=("sub-01" "sub-02" "sub-03" "sub-04" "sub-05" "sub-06")

#sub_index=$SLURM_ARRAY_TASK_ID

#TASK_ID=${sub_ids[$sub_index]}

#echo "Processing: ${sub_index}"

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

echo "Running compile_hcp_data.py with global z"
python compile_hcp_data.py --global_z

# # Only reach here if both scripts succeeded
# echo "Both scripts succeeded. Starting data transfer..."
# dest_dir="/orcd/data/satra/001/users/yibei/hcptrt/output/GLMsingle/results_v2/${TASK_ID}/"
# mkdir -p "$dest_dir"
# rsync -avz --ignore-existing /orcd/scratch/bcs/001/yibei/hcptrt/output/GLMsingle/results_v2/${TASK_ID}/ "$dest_dir"

# echo "All operations completed successfully!"
