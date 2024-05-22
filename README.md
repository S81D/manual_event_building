# FermiGrid_Scripts

Scripts to submit jobs to the grid. Utilizes James Minock's container-within-a-container solution. Jobs rely on submitting a tar-ball of ToolAnalysis to execute a toolchain, then complete and deposit the job output to ```/pnfs/annie/scratch/users/<user>/```.

-----------------------
Contains two files, ```submit_jobs.py``` and ```auto_submit_job.py```. The former contains functions that are called by the latter to create three scripts to be run on the grid. ```submit_grid_job.sh``` sends the actual job and the associated files + input/output path locations. ```grid_job.sh``` is what is actually ran by the worker node, and after entering our container, ```run_container_job.sh``` is ran to execute the the ToolChains. Currently customized for EventBuilding, primarily by using the ```EventBuilder``` ToolChain.

There are two pre-requirements necessary for these scripts. If you are building beam or cosmic run data, you should run the ```PreProcessTrigOverlap``` toolchain which will produce "trigger overlap files" that are used by the event building toolchain to fetch triggers that may be stored in neighboring part files. After producing these files, you will need to tar-ball them and copy to ```/pnfs/annie/persistent/processed/trigoverlap``` where the scripts assume the trigoverlap tar-ball will be located (there may already be a trigoverlap tar-ball in that location for the run you are producing). If you are event building source runs, overlap files are not necessary and you can set ```source = False``` in ```auto_submit_job.py``` to skip this step. Secondly, you will need to tarball ToolAnalysis (you can do this via: ```tar -czvf <archive_name>.tar.gz -C /path <folder_name>```). Drop this file into your input location, then run ```python3 auto_submit_job.py``` to execute the job submission (tar-balling toolanalysis is a requirement for all run types). User inputs are required, asking which run and how many part files you wish to produce. 

For an individual user utilizing this repo, the following changes need to be made:
- Modify ```auto_submit_job.py``` by changing the name of the user, the input and output paths (ideally on /scratch), and the name of the toolanalysis tarball (both the name of the tarball and the underlying directory name that you tar-balled in the first place).
- Specify whether you are building source runs (for trig overlap)

Keep in mind that all scripts and the TA tarball should be placed within your input path location that you set in ```auto_submit_job.py```. No files or scripts need to be put in the output location, as a directory (name = run number) will automatically be created there where the output files from your job + any log files will be deposited. There is also a rawdata path that pulls the raw data from ```/pnfs```. This does not need to be modified for individual users.

In addition, some ToolChains are sensitive to Daylight Savings, so ensure those files within your ToolAnalysis tar-ball are properly adjusted. 

```find_missing_files.py``` is useful for checking to see if the event building produced all of the part files. It's tedious to go through and find discrepencies when there are 100's of part files. To run it, simply specify the run number: ```python3 find_filesizes.py <RUN_NUMBER>```. After jobs have completed, use ```copy_grid_output.sh``` to copy Processed and Orphan files from your user area in /scratch to /persistent (for copying large amounts of files to /persistent, it is recommended to use ```ifdh cp```). This script will also run ```find_missing_files.py``` to tell you what part files were not successfully produced from your job submissions (and hence were not copied to /persistent). Both scripts should be in the same directory.

Note that the allocated memory and disk space specified in the script may not be sufficient for varying part file submission sizes. The scripts currently estimate the disk space needed based on the number of part files you are submitting per job. The memory allocation requested is 2000MB. Note that some source runs (Laser in particular) contain large part files, so it may be necessary to significantly increase the disk allocation (say to 30 GB).

To check on your jobs, use: ```jobsub_q -G annie --user <<username>>```

To cancel job submissions, use: ```jobsub_rm -G annie <<username>>```
