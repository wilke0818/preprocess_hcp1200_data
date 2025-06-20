import json
import os
from dotenv import load_dotenv
import csv
import pandas as pd
import argparse

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

    parser = argparse.ArgumentParser(description="A simple script for generating study specific IDs")
    parser.add_argument('--unfiltered_data_csv', default='hcp_7t_unfiltered.csv', help='Path to the unfiltered 7T CSV data')

    args = parser.parse_args()
    base_dir = os.getenv("HCP_1200_BASE_DIR")

    unfiltered_data = pd.read_csv(args.unfiltered_data_csv)
    
    unfiltered_data['subject'] = unfiltered_data['Subject'].astype(str)
    
    subject_ids = unfiltered_data['Subject']
    
    with open('hcp_7t_subject_ids.txt') as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines]
    
    path = os.path.join(base_dir,'HCP1200')
    all_data = []
    for subject in lines:
        s_path = os.path.join(path,subject,'MNINonLinear','Results')
        subject_data = {'subject': subject}
        has_all = True
        for task in tasks:
            subject_data[task] = False
            t_path = os.path.join(s_path,task)
            if os.path.exists(t_path):
                if 'tfMRI' in task and 'MOVIE' not in task:
                        #tfMRI_EMOTION_hp200_s2_level2_MSMAll.feat/100610_tfMRI_EMOTION_level2_hp200_s2_MSMAll.dscalar.nii
                    p = tasks[task].split('_')
                    task_path = os.path.join(t_path,f"{task}_{tasks[task]}.feat",f"{subject}_{task}_{p[2]}_{p[0]}_{p[1]}_{p[3]}.dscalar.nii")
                else:
                    task_path = os.path.join(t_path,f"{task}_{tasks[task]}.dtseries.nii")
                if os.path.exists(task_path):
                    subject_data[task] = True
            if 'rfMRI' not in task:
                has_all &= subject_data[task]
        subject_data['has_all_movies'] = subject_data['tfMRI_MOVIE4_7T_AP']&subject_data['tfMRI_MOVIE3_7T_PA']&subject_data['tfMRI_MOVIE2_7T_PA']&subject_data['tfMRI_MOVIE1_7T_AP']
        subject_data['has_all_tasks'] = has_all
        all_data.append(subject_data)
    
    subjects_with_qc_issues = unfiltered_data[(unfiltered_data['QC_Issue'].notna())&(unfiltered_data['QC_Issue'].str.contains('A')|unfiltered_data['QC_Issue'].str.contains('B')|unfiltered_data['QC_Issue'].str.contains('C'))]
    
    print(len(unfiltered_data[(unfiltered_data['QC_Issue'].notna())&(unfiltered_data['QC_Issue'].str.contains('C'))]))
    print(subjects_with_qc_issues['QC_Issue'])
    
    all_data_df = pd.DataFrame(all_data)
    has_movies = all_data_df[all_data_df['has_all_movies']]
    has_all = all_data_df[all_data_df['has_all_tasks']]
    print(len(has_movies))
    print(len(has_all))
    
    has_all_no_qc_issues = has_all[~has_all['subject'].isin(subjects_with_qc_issues['subject'])]
    has_all_no_qc_issues = has_all_no_qc_issues.merge(unfiltered_data[['subject', '7T_fMRI_Mov_Vrs']], on='subject', how='left')
    
    subject_id_map = {}
    
    print(has_all_no_qc_issues)
    
    
    import random
    subject_ids = list(has_all_no_qc_issues['subject'])
    random.shuffle(subject_ids)
    subject_id_map = {}
    for i,subject_id in enumerate(subject_ids):
        subject_id_map[subject_id] = f"sub-{i+1}"
    
    with open('restricted_subject_id_map.json','w') as f:
      json.dump(subject_id_map,f)
      #json.dump(subject_id_map,f)

if __name__=='__main__':
    main()
