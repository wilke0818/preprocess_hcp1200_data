import argparse
from dotenv import load_dotenv
import warnings
import os
import subprocess


def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout) # Print the output
    print(result.stderr) # Print the errors
    print(result.returncode) # Print the exit code
    return result

tasks = {'rfMRI_REST1_7T_PA': 'Atlas_MSMAll_hp2000_clean',
        'rfMRI_REST2_7T_AP': 'Atlas_MSMAll_hp2000_clean',
        'rfMRI_REST3_7T_PA': 'Atlas_MSMAll_hp2000_clean',
        'rfMRI_REST4_7T_AP': 'Atlas_MSMAll_hp2000_clean',
        'tfMRI_EMOTION': 'hp200_s2_level2_MSMAll',
        'tfMRI_GAMBLING': 'hp200_s2_level2_MSMAll',
        'tfMRI_LANGUAGE': 'hp200_s2_level2_MSMAll',
        'tfMRI_MOTOR': 'hp200_s2_level2_MSMAll',
        'tfMRI_RELATIONAL': 'hp200_s2_level2_MSMAll',
        'tfMRI_SOCIAL': 'hp200_s2_level2_MSMAll',
        'tfMRI_WM': 'hp200_s2_level2_MSMAll',
        'tfMRI_MOVIE1_7T_AP': 'Atlas_MSMAll_hp2000_clean',
        'tfMRI_MOVIE2_7T_PA': 'Atlas_MSMAll_hp2000_clean',
        'tfMRI_MOVIE3_7T_PA': 'Atlas_MSMAll_hp2000_clean',
        'tfMRI_MOVIE4_7T_AP': 'Atlas_MSMAll_hp2000_clean'
        }

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description='Example program')
    parser.add_argument('--file_num', type=int)
    args = parser.parse_args()

    base_dir = os.getenv("HCP_1200_BASE_DIR")

    num_files_to_get = 1
    with open('hcp_7t_subject_ids.txt') as f:
        lines = f.readlines()
        lines = [line.rstrip() for line in lines]
    print(len(lines))
    subject_ids = lines[num_files_to_get*args.file_num:num_files_to_get*(args.file_num+1)]
    for subject_id in subject_ids:
        print(subject_id)
        f_path = os.path.join(base_dir,'HCP1200',str(subject_id))
        command = ['datalad','get','-n',f_path]
        run_command(command)
        f_path = os.path.join(f_path,'MNINonLinear')
        command = ['datalad','get','-n',f_path]
        run_command(command)
        f_path = os.path.join(f_path,'Results')
        command = ['datalad','get','-n',f_path]
        run_command(command)
        for task in tasks:
            task_path = os.path.join(f_path,task)
            if os.path.isdir(task_path):
                if 'tfMRI' in task and 'MOVIE' not in task:
                    task_path = os.path.join(task_path,f"{task}_{tasks[task]}.feat")
                    command = ['datalad','get',task_path]
                    run_command(command)
                else:
                    task_path = os.path.join(task_path,f"{task}_{tasks[task]}.dtseries.nii")
                    command = ['datalad','get',task_path]
                    run_command(command)
            else:
                warnings.warn(f"{task_path} not found")
        


if __name__=='__main__':
    main()
