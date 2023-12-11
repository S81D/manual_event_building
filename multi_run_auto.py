# A script to send many runs at a time automatically

import sys, os
import submit_jobs     # other py script for generating the job submission scripts

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Modify:

TA_tar_name = 'MyToolAnalysis_grid.tar.gz'                    # name of toolanalysis tar-ball
name_TA = 'MyFork_DD'                                         # name of the TA directory (within tar-ball)

user = 'doran'                                                # annie username

input_path = '/pnfs/annie/scratch/users/doran/'               # path to your grid input location (submit_job_grid.sh, run_container_job.sh, grid_job.sh and necessary submission files)
output_path = '/pnfs/annie/scratch/users/doran/output/'       # grid output location

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
print('\n#### This script will use overlap part files####\n')
runs = []

print("\nPlease enter run numbers to be processed (enter 'stop' to end script):")
while True:
    rn = input('\n>> ')
    if rn == 'stop':
        break
    
    else:
        all_files = os.listdir('/pnfs/annie/persistent/raw/raw/' + rn + '/')
        all_files.sort(key=lambda file: int(file.split('p')[-1]))
        last_file = all_files[-1]
        final_part = int(last_file.split('p')[-1])
        print('\nThere are ' + str(final_part+1) + ' part files in this run')

        # check if overlap tar file exits
        exists = os.path.isfile('/pnfs/annie/persistent/processed/trigoverlap/R' + rn + '_TrigOverlap.tar.gz')
        if exists == False:
            print('\nNo TrigOverlap tar file exists for run ' + rn + ' in /pnfs/annie/persistent/processed/trigoverlap/ --- please process TrigOverlap files before submitting this run!')
            print('\nPlease pick another run')
            continue
        
        proceed = input('\nProceed with run ' + rn + '? (y/n)   ')
        if proceed != 'y' and proceed != 'n':
            print('\n### ERROR: Please type y or n ###\n')
            proceed = input('\nProceed with run ' + rn + '? (y/n)   ')

        if proceed == 'y':
            runs.append(rn)
        elif proceed == 'n':
            continue

if len(runs) == 0:
    print('\nNo runs selected\n')
    exit()

print('\n', runs)
verify = input('\nThe following runs will be processed, proceed? (y/n)   ')
if verify != 'y' and verify != 'n':
    print('\n### ERROR: Please type y or n ###\n')
    verify = input('\nProceed? (y/n)   ')
if verify == 'n':
    print('\nPlease re-run code\n')
    exit()
    

elif verify == 'y':

    auto_step_size = 5
    step_size = input('\nStep size of ' + str(auto_step_size) + ' okay? (y/n)   ')
    if step_size != 'y' and step_size != 'n':
        print('\n### ERROR: Please type y or n ###\n')
        step_size = input('\nStep size of ' + str(auto_step_size) + ' okay? (y/n)   ')
    if step_size == 'n':
        auto_step_size = int(input('\nPlease specify step size:  '))


    for rn in range(len(runs)):

        all_files = os.listdir('/pnfs/annie/persistent/raw/raw/' + runs[rn] + '/')
        all_files.sort(key=lambda file: int(file.split('p')[-1]))
        last_file = all_files[-1]
        final_part = int(last_file.split('p')[-1])

        first_part = int(0)
        last_part = final_part

        if ((last_part - first_part) + 1) < auto_step_size:
            auto_step_size = (last_part - first_part) + 1


        part_list = [[], []]     # [0] = first,  [1] = final
        for i in range(first_part, last_part + 1, auto_step_size):
            if i != 0:
                part_list[0].append(i-1)
            else:
                part_list[0].append(i)
            if (i+auto_step_size) > last_part:
                if last_part < final_part:
                    part_list[1].append(last_part+1)
                else:
                    part_list[1].append(final_part)
            else:
                part_list[1].append(i + auto_step_size)


        # calculate disk space requirements
        import math
        disk_space = str(math.ceil(7 + .3*auto_step_size + .05*auto_step_size))   # fine for beam files

        # Submit the entire batch through multiple jobs, based on the user input (above)

        for i in range(len(part_list[0])):     # loop over number of jobs
            
            # create the run_container_job and grid_job scripts
            os.system('rm ' + input_path + 'grid_job.sh')
            submit_jobs.grid_job(runs[rn], user, input_path, TA_tar_name, name_TA)
            os.system('rm run_container_job.sh')
            submit_jobs.run_container_job(runs[rn], name_TA)

            # We can then create the job_submit script that will send our job (with files) to the grid
            os.system('rm submit_grid_job.sh')
            submit_jobs.submit_grid_job(runs[rn], part_list[0][i], part_list[1][i], input_path, output_path, TA_tar_name, disk_space)

            # Lastly, we can execute the job submission script and send the job to the grid
            os.system('sh submit_grid_job.sh')
            print('\n# # # # # # # # # # # # # # # # # # # # #')
            print('Run ' + runs[rn] + ' p' + str(part_list[0][i]) + '-' + str(part_list[1][i]) + ' sent')
            print('# # # # # # # # # # # # # # # # # # # # #\n')


    print('\nJobs successfully submitted!\n')