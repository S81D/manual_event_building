#########################################################################################
# Automatically send jobs to the grid, using the container-within-a-container method
# --> specifically designed for building events (w/out LAPPDs) using the EventBuilder TC
#
# Thanks to James Minock for finding a working solution to the grid incompatibility issue 
# and for developing the backbone for the various submission and execution scripts.
# Thanks to Marvin Ascencio and Paul Hackspacher for their help as well.
#
# Author: Steven Doran, December 2023
#########################################################################################

import sys, os
import submit_jobs     # other py script for generating the job submission scripts

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Modify:

TA_tar_name = 'MyToolAnalysis_grid.tar.gz'                    # name of toolanalysis tar-ball
name_TA = 'DD_TA'                                             # name of the TA directory (within tar-ball)

user = 'doran'                                                # annie username

input_path = '/pnfs/annie/scratch/users/doran/'               # path to your grid input location (submit_job_grid.sh, run_container_job.sh, grid_job.sh and necessary submission files)
output_path = '/pnfs/annie/scratch/users/doran/output/'       # grid output location

source = True                                                 # source run or not (LED, Laser, AmBe) --> do not include trigoverlap
                                                              # source runs submit single part files for each job

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
print('\n------- Please ensure you have produced a trigoverlap tar file prior to job submission -------')
print('\n---------------- and that the user name and the TA directory name are accurate ---------------')
print("\n*********************** Don't forget about Daylight Savings!! **************************\n")

run = input('\nRun number:  ')

if source == False:
	# check if overlap tar file exits
	exists = os.path.isfile('/pnfs/annie/persistent/processed/trigoverlap/R' + run + '_TrigOverlap.tar.gz')
	if exists == False:
         print('\nNo TrigOverlap tar file exists for run ' + run + ' in /pnfs/annie/persistent/processed/trigoverlap/ --- please process TrigOverlap files before submitting the jobs!\n')
         exit()


# sort and find the highest numbered part file from that run (need for breaking up the jobs)
all_files = os.listdir('/pnfs/annie/persistent/raw/raw/' + run + '/')
all_files.sort(key=lambda file: int(file.split('p')[-1]))
last_file = all_files[-1]
final_part = int(last_file.split('p')[-1])

print('\nThere are ' + str(final_part+1) + ' part files in this run. Proceeding with job submissions...')


# re-run will submit jobs using find_missing_files.py (only re-submit jobs that failed for a given run)
missing = input('\nIs this a re-run? (y/n)   ')
if missing != 'y' and missing != 'n':
    print('\n### ERROR: Please type y or n ###\n')
    exit()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# normal event building
if missing == 'n':

    process_all = input('\nWould you like to submit the entire run? (y/n)   ')

    if process_all == 'y':
        process_all = True
    elif process_all == 'n':
        process_all = False
    else:
        print('\n### ERROR: Please type y or n ###\n')
        exit()


    # for beam runs, we want the part files to overlap between job submissions to account for TrigOverlap issue
    # (last part file is sometimes .data format)
    if source == False:
        overlap = input("\nInclude overlap? (y/n)     ** 'y' is recommended for beam runs **   ")
        if overlap != 'y' and overlap != 'n':
            print('\n### ERROR: Please type y or n ###\n')
            exit()
    elif source == True:
        overlap = 'n'


    if process_all == True:
        first_part = int(0)
        last_part = final_part

    if process_all == False:
        first_part = int(input('\nPlease specify the first part file of the batch:  '))
        last_part = int(input('\nPlease specify the final part file of the batch:  '))

    if source == False:
        step_size = int(input('\nPlease specify how many part files per job you would like to submit:   '))
    else:
        step_size = int(1)
        print('\nSource run selected (source = True) - each job will contain a single part file')
    print('\n')

    if (step_size > (last_part-first_part + 1)):
        print('\n### ERROR: Stepsize larger than the number of part files selected or first part file > last part file ###\n')
        exit()


    # We need to break the batch into seperate jobs. Unless the batch size is evenly divisible by
    # the step size, the last job will be smaller than the other ones.

    part_list = [[], []]     # [0] = first,  [1] = final
    for i in range(first_part, last_part + 1, step_size):

        if overlap == 'y':    # include overlap files if specified
            
            if i != 0:
                part_list[0].append(i-1)
            else:
                part_list[0].append(i)
            if (i+step_size) > last_part:
                if last_part < final_part:
                    part_list[1].append(last_part+1)
                else:
                    part_list[1].append(final_part)
            else:
                part_list[1].append(i + step_size)
                
                
        elif overlap == 'n':
            
            part_list[0].append(i)
            
            if ((i+step_size-1) > last_part):
                part_list[1].append(last_part)
            else:
                part_list[1].append(i+step_size-1)


    # calculate disk space requirements
    import math
    if source == False:
        disk_space = str(math.ceil(4 + 2.5 + .25*step_size + .15*step_size))   # fine for beam and cosmic runs
    else:
        disk_space = str(10)     # for source runs, submit single part files

    # Submit the entire batch through multiple jobs, based on the user input (above)

    for i in range(len(part_list[0])):     # loop over number of jobs
        
        # create the run_container_job and grid_job scripts
        os.system('rm ' + input_path + 'grid_job.sh')
        submit_jobs.grid_job(run, user, input_path, TA_tar_name, name_TA, source)
        os.system('rm run_container_job.sh')
        submit_jobs.run_container_job(run, name_TA, source)

        # We can then create the job_submit script that will send our job (with files) to the grid
        os.system('rm submit_grid_job.sh')
        submit_jobs.submit_grid_job(run, part_list[0][i], part_list[1][i], input_path, output_path, TA_tar_name, disk_space, source)

        # Lastly, we can execute the job submission script and send the job to the grid
        os.system('sh submit_grid_job.sh')
        print('\n# # # # # # # # # # # # # # # # # # # # #')
        print('Run ' + run + ' p' + str(part_list[0][i]) + '-' + str(part_list[1][i]) + ' sent')
        print('# # # # # # # # # # # # # # # # # # # # #\n')



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# re-submit jobs that failed
if missing == 'y':


    if source == False:
        overlap = input("\nInclude overlap? (y/n)     ** 'y' is recommended for beam runs **   ")
        if overlap != 'y' and overlap != 'n':
            print('\n### ERROR: Please type y or n ###\n')
            exit()
    elif source == True:
        overlap = 'n'


    # run find_missing_files.py
    run_number = run

    raw_data_dir = "/pnfs/annie/persistent/raw/raw/" + run_number + "/"
    #processed_dir = "/pnfs/annie/persistent/processed/processed_hits_new_charge/R" + run_number + "/"
    processed_dir = "/pnfs/annie/scratch/users/doran/output/" + run_number + "/"

    print('\nFinding missing files in ' + str(processed_dir))

    raw_files = [file for file in os.listdir(raw_data_dir) if file.startswith("RAWDataR" + run_number)]
    processed_files = [file for file in os.listdir(processed_dir) if file.startswith("ProcessedRawData_TankAndMRDAndCTC_R" + run_number) and not file.endswith(".data")]
    num_raw_files = len(raw_files)
    num_processed_files = len(processed_files)

    # Find the missing processed files
    missing_files = []
    for file in raw_files:
        expected_processed_file = "ProcessedRawData_TankAndMRDAndCTC_R" + file[8:]  # Remove "RAWDataR" prefix
        if expected_processed_file not in processed_files:
            missing_files.append(int(expected_processed_file[42:]))

    print("\nNumber of raw files: ", num_raw_files)
    print("Number of processed files: ", num_processed_files)
    print("Number of missing files: ", num_raw_files-num_processed_files)
    print("Missing processed files: ", missing_files)


    # go through the missing processed files to group them if there are consecutive part files
    def group_consecutive_elements(lst):
        result = []
        current_group = []
        for i in range(len(lst)):
            if i > 0 and lst[i] != lst[i - 1] + 1:
                result.append(current_group)
                current_group = []
            current_group.append(lst[i])
        if current_group:
            result.append(current_group)
        return result

    missing_list = group_consecutive_elements(missing_files)
    ml = 0
    for i in range(len(missing_list)):
        if len(missing_list[i]) > ml:
            ml = len(missing_list[i])
        
    print('\nMaximum part bunch size = ' + str(ml))

    if ml == 0:
        print('\nNo missing files!!! aborting...\n')
        exit()


    # Automatically assign a step size of (N) for resubmission. Loop through the missing part files,
    # if there is a group that is larger than N, ask the user if they wish to change the step size of that job

    # for source runs, assign as 1

    if source == False:
        auto_step_size = 4
    else:
        auto_step_size = 1
    
    automatic = input('\nAutomatic submission for a step size of ' + str(auto_step_size) + '? (y/n)   (source runs are set to 1)   ')
    if automatic != 'y' and automatic != 'n':
        print('\n### ERROR: Please type y or n ###\n')
        exit()

    for l in range(len(missing_list)):

        first_part = min(missing_list[l])
        last_part = max(missing_list[l])

        if automatic == 'n':

            print('\n### Part files', missing_list[l], 'are missing ###')

            if len(missing_list[l]) != 1:
                step_size = int(input('\nPlease specify how many part files per job you would like to submit for these missing files:   '))
            else:
                proceed_input = input("\nOnly 1 part file... proceed with submission? (type 'abort' to stop   ")
                step_size = 1
                if proceed_input != 'abort':
                    print('\nproceeding...')
                else:
                    print('\njob submission cancelled\n')
                    exit()


        if automatic == 'y':
            if len(missing_list[l]) >= auto_step_size:
                step_size = auto_step_size
            elif len(missing_list[l]) < auto_step_size:
                step_size = len(missing_list[l])


        if (step_size > (last_part-first_part + 1)):
            print('\n### ERROR: Stepsize larger than the number of part files selected or first part file > last part file ###\n')
            exit()

        part_list = [[], []]     # [0] = first,  [1] = final
        for i in range(first_part, last_part + 1, step_size):

            if overlap == 'y':    # include overlap files if specified
                
                if i != 0:
                    part_list[0].append(i-1)
                else:
                    part_list[0].append(i)
                if (i+step_size) > last_part:
                    if last_part < final_part:
                        part_list[1].append(last_part+1)
                    else:
                        part_list[1].append(final_part)
                else:
                    part_list[1].append(i + step_size)
                    
                    
            elif overlap == 'n':
                
                part_list[0].append(i)
                
                if ((i+step_size-1) > last_part):
                    part_list[1].append(last_part)
                else:
                    part_list[1].append(i+step_size-1)


        # calculate disk space requirements
        import math
        if source == False:
            disk_space = str(math.ceil(4 + 2.5 + .25*step_size + .15*step_size))   # fine for beam and cosmic runs
        else:
            disk_space = str(10)     # for source runs, submit single part files

        # Submit the entire batch through multiple jobs, based on the user input (above)

        for i in range(len(part_list[0])):     # loop over number of jobs
            
            # create the run_container_job and grid_job scripts
            os.system('rm ' + input_path + 'grid_job.sh')
            submit_jobs.grid_job(run, user, input_path, TA_tar_name, name_TA)
            os.system('rm run_container_job.sh')
            submit_jobs.run_container_job(run, name_TA)

            # We can then create the job_submit script that will send our job (with files) to the grid
            os.system('rm submit_grid_job.sh')
            submit_jobs.submit_grid_job(run, part_list[0][i], part_list[1][i], input_path, output_path, TA_tar_name, disk_space)

            # Lastly, we can execute the job submission script and send the job to the grid
            os.system('sh submit_grid_job.sh')
            print('\n# # # # # # # # # # # # # # # # # # # # #')
            print('Run ' + run + ' p' + str(part_list[0][i]) + '-' + str(part_list[1][i]) + ' sent')
            print('# # # # # # # # # # # # # # # # # # # # #\n')


print('\nJobs successfully submitted!\n')
