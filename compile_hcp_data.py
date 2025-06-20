import json
import os
import nibabel as nib
import numpy as np

import csv
import pandas as pd

import argparse
from dotenv import load_dotenv

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


task_to_names = {
        'rfMRI_REST1_7T_PA': 'rfMRI1',
        'rfMRI_REST2_7T_AP': 'rfMRI2',
        'rfMRI_REST3_7T_PA': 'rfMRI3',
        'rfMRI_REST4_7T_AP': 'rfMRI4',
        'tfMRI_MOVIE1_7T_AP': '7T_MOVIE1_CC1',
        'tfMRI_MOVIE2_7T_PA': '7T_MOVIE2_HO1',
        'tfMRI_MOVIE3_7T_PA': '7T_MOVIE3_CC2',
        'tfMRI_MOVIE4_7T_AP': '7T_MOVIE4_HO2'
    }


task_to_contrast = {
    'tfMRI_WM': {
        '2BK': '2bk_vs_baseline',
        '0BK': '0bk_vs_baseline',
        '2BK-0BK': '2bk_vs_0bk',
        'BODY': 'body_vs_baseline',
        'FACE': 'face_vs_baseline',
        'PLACE': 'place_vs_baseline',
        'TOOL': 'tool_vs_baseline',
        'BODY-AVG': 'body_vs_others',
        'FACE-AVG': 'face_vs_others',
        'PLACE-AVG': 'place_vs_others',
        'TOOL-AVG': 'tool_vs_others',
    },
    'tfMRI_SOCIAL': {
        'TOM-RANDOM': 'tom_vs_random',
        'TOM': 'tom_vs_baseline',
        'RANDOM': 'random_vs_baseline'
    },
    'tfMRI_RELATIONAL': {
        'MATCH': 'matching_vs_baseline',
        'REL': 'relational_vs_baseline',
        'REL-MATCH': 'relational_vs_matching'
    },
    'tfMRI_EMOTION': {
        'FACES': 'faces_vs_baseline',
        'SHAPES': 'shapes_vs_baseline',
        'FACES-SHAPES': 'faces_vs_shapes',
    },
    'tfMRI_LANGUAGE': {
        'MATH': 'math_vs_baseline',
        'STORY': 'story_vs_baseline',
        'STORY-MATH': 'story_vs_math'
    },
    'tfMRI_MOTOR': {
        'LF': 'lf_vs_baseline',
        'LH': 'lh_vs_baseline',
        'RF': 'rf_vs_baseline',
        'RH': 'rh_vs_baseline',
        'T': 't_vs_baseline',
        'LF-AVG': 'lf_vs_others',
        'LH-AVG': 'lh_vs_others',
        'RF-AVG': 'rf_vs_others',
        'RH-AVG': 'rh_vs_others',
        'T-AVG': 't_vs_others'
    },
    'tfMRI_GAMBLING': {
        'PUNISH': 'punish_vs_baseline',
        'REWARD': 'reward_vs_baseline',
        'REWARD-PUNISH': 'reward_vs_punish'
    }
}


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="parses arguments for compiling the HCP1200 data that is needed")
    parser.add_argument('--global_z', action="store_true", help='Global z-score movie and resting state data')
    parser.add_argument('--output_dir', default='./anon_7t_filtered_no_qc_issue', type=str)
    args = parser.parse_args()

    base_dir = os.getenv("HCP_1200_BASE_DIR")

    output_dir = args.output_dir

    subject_id_map = {}
    with open('restricted_subject_id_map.json') as f:
      subject_id_map = json.load(f)
    
    # For each subject
    for subject_id in list(subject_id_map.keys()):
        print(f"Running {subject_id}")
    #   Need to go into the appropriate HCP folders
        src_folder = os.path.join(base_dir,'HCP1200',subject_id,'MNINonLinear','Results')
    #   For each localizer 
        for task in task_to_contrast:
            print(f"Running task {task}")
            task_result_folder = os.path.join(src_folder,task,f"{task}_{tasks[task]}.feat")
            contrast_file = os.path.join(task_result_folder,'Contrasts.txt')
            p = tasks[task].split('_')
            cifti_file = os.path.join(task_result_folder,f"{subject_id}_{task}_{p[2]}_{p[0]}_{p[1]}_{p[3]}.dscalar.nii")
    #     Use Contrast.txt to determine which data from the CIFTI file to get
            with open(contrast_file) as f:
                task_contrasts = f.readlines()
            task_contrasts = [c.strip() for c in task_contrasts]
            task_data = nib.load(cifti_file).get_fdata()
            for contrast in task_to_contrast[task]:
                contrast_idx = task_contrasts.index(contrast)
                contrast_data = task_data[contrast_idx,:]
                task_str = task.split('_')[1].lower()
                dst_folder = os.path.join(output_dir,'localizer_responses',subject_id_map[subject_id],task_str)
                os.makedirs(dst_folder,exist_ok=True)
                np.save(os.path.join(dst_folder,f"{task_to_contrast[task][contrast]}.npy"),contrast_data)
        for task in tasks:
            if task in task_to_contrast: continue
            if not os.path.exists(os.path.join(src_folder,task)) or not os.path.exists(os.path.join(src_folder,task,f"{task}_{tasks[task]}.dtseries.nii")):
                print(f"{os.path.join(src_folder,task)} not found")
                if 'MOVIE' in task:
                    raise ValueError("Should have had all movies available")
                else:
                    print("was resting state")
                    continue
            print(f"Running task {task}")
            src_file = os.path.join(src_folder,task,f"{task}_{tasks[task]}.dtseries.nii")
            data = nib.load(src_file).get_fdata()
    
            if args.global_z:
                global_z_data = (data - np.mean(data))/np.std(data)
                assert global_z_data.shape == data.shape
                final_data = global_z_data #dont need to worry that this is a copy
            else:
                final_data = data
    
            if 'MOVIE' in task:
                dst_folder = os.path.join(output_dir,'movie_responses',subject_id_map[subject_id])
            else:
                dst_folder = os.path.join(output_dir,'resting_state_responses',subject_id_map[subject_id])
            os.makedirs(dst_folder,exist_ok=True)
            np.save(os.path.join(dst_folder,f"{task_to_names[task]}.npy"),final_data)


if __name__=='__main__':
    main()
#     Save the data with appropriate name, in new folder with new study subject ids as NumPy files
# With that can then create parcellated versions of each
# Create contrast data files specifying paths to data, groupings (family in our case) and necessary other things

