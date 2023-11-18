#########################################################################################
# Automatically send jobs to the grid, using the container-within-a-container method
# --> specifically designed for building events (w/out LAPPDs) using the DataDecoder TC
#
# Thanks to James Minock for finding a working solution to the grid incompatibility issue 
# and for developing the backbone for the various submission and execution scripts.
# Thanks to Marvin Ascencio and Paul Hackspacher for their help as well.
#
# Author: Steven Doran, May 2023
#########################################################################################

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
print('\n------- Please ensure you have produced a <RUN_NUMBER>_beamdb file prior to job submission -------')
print('\n------------------ and that the user name and the TA directory name are accurate -----------------')
print("\n*********************** Don't forget about Daylight Savings!! **************************\n")

run = input('\nRun number:  ')

# check if overlap tar file exits
exists = os.path.isfile('/pnfs/annie/persistent/processed/trigoverlap/R' + run + '_TrigOverlap.tar.gz')
if exists == False:
    print('\nNo TrigOverlap tar file exists for run ' + run + ' in /pnfs/annie/persistent/processed/trigoverlap/ --- please process TrigOverlap files before submitting the jobs!\n')
    exit()

process_all = input('\nWould you like to submit the entire run? (y/n)   ')

if process_all == 'y':
    process_all = True
    print("\n***Note: In selecting the entire run, the part files will overlap between job submissions to account for TrigOverlap issue***\n\
    --> For example if you specify 3 part files per job, the job submissions will be 0-2, 2-5, 5-8, etc... instead of 0-2, 3-5, 6-8, etc...\n\
    (Just a heads up - it's part of the script, just be mindful that your jobs will contain +1 file more than you specify in the next input)\n")
elif process_all == 'n':
    process_all = False
else:
    print('\n### ERROR: Please type y or n ###\n')
    exit()


# sort and find the highest numbered part file from that run (need for breaking up the jobs)

all_files = os.listdir('/pnfs/annie/persistent/raw/raw/' + run + '/')

all_files.sort(key=lambda file: int(file.split('p')[-1]))
last_file = all_files[-1]
final_part = int(last_file.split('p')[-1])

print('\nThere are ' + str(final_part+1) + ' part files in this run. Proceeding with job submissions...')

if process_all == True:
    first_part = int(0)
    last_part = final_part

if process_all == False:
    first_part = int(input('\nPlease specify the first part file of the batch:  '))
    last_part = int(input('\nPlease specify the final part file of the batch:  '))


step_size = int(input('\nPlease specify how many part files per job you would like to submit:   '))
print('\n')

if (step_size > (last_part-first_part + 1)):
    print('\n### ERROR: Stepsize larger than the number of part files selected or first part file > last part file ###\n')
    exit()


# We need to break the batch into seperate jobs. Unless the batch size is evenly divisible by
# the step size, the last job will be smaller than the other ones.

part_list = [[], []]     # [0] = first,  [1] = final
for i in range(first_part, last_part + 1, step_size):
    # to account for the trigoverlap issue (last part file is sometimes a .data format)
    if process_all == True and i != 0:
        part_list[0].append(i-1)
    else:
        part_list[0].append(i)
        
    if ((i+step_size-1) > last_part):    # the last job (will be smaller than the others)
        part_list[1].append(last_part)
    else:
        part_list[1].append(i+step_size-1)

# calculate disk space requirements
import math
disk_space = str(math.ceil(7 + .3*step_size + .05*step_size))   # fine for beam files
#disk_space = str(10)     # typically fine as a default - good for Laser single part submissions

# Submit the entire batch through multiple jobs, based on the user input (above)

for i in range(len(part_list[0])):     # loop over number of jobs
    
    # create the run_container_job and grid_job scripts
    os.system('rm ' + input_path + 'grid_job.sh')
    submit_jobs.grid_job(run, user, input_path, TA_tar_name, name_TA)
    os.system('rm run_container_job.sh')
    submit_jobs.run_container_job(run, name_TA)

    # For the DataDecoder TC, we first must produce "my_files.txt", which contains the paths to the raw data files
    # For some reason, when submitting my_files.txt from the input to the worker node, the job could not locate it, aside
    # from the final job in a batch. Therefore, if you submitted 5 jobs in total, only the last one could find the file. 
    # To remedy this, we produce my_files.txt on the worker node based on the input RAWData files in /srv.


    # We can then create the job_submit script that will send our job (with files) to the grid

    os.system('rm submit_grid_job.sh')
    submit_jobs.submit_grid_job(run, part_list[0][i], part_list[1][i], input_path, output_path, TA_tar_name, disk_space)


    # Lastly, we can execute the job submission script and send the job to the grid

    os.system('sh submit_grid_job.sh')
    print('\n# # # # # # # # # # # # # # # # # # # # #')
    print('Run ' + run + ' p' + str(part_list[0][i]) + '-' + str(part_list[1][i]) + ' sent')
    print('# # # # # # # # # # # # # # # # # # # # #\n')


print('\nJobs successfully submitted!\n')
