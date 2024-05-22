# FermiGrid_Scripts

Scripts to submit jobs to the grid. Utilizes James Minock's container-within-a-container solution. Jobs rely on submitting a tar-ball of ToolAnalysis to execute a toolchain, then complete and deposit the job output to ```/pnfs/annie/scratch/users/<user>/```.

An event building guide using ToolAnalysis can be found here: https://cdcvs.fnal.gov/redmine/projects/annie_experiment/wiki/Event_Building_with_ToolAnalysis

A guide for grid submissions can be found here: https://cdcvs.fnal.gov/redmine/projects/annie_experiment/wiki/General_guideline_for_running_ANNIE_Singularity_Containers_on_Grid

-----------------------
Contains two files, ```submit_jobs.py``` and ```auto_submit_job.py```. The first contains functions that are called by the second to create three scripts to be run on the grid. ```submit_grid_job.sh``` sends the actual job and the associated files + input/output path locations. ```grid_job.sh``` is what is actually ran by the worker node, and after entering our container, ```run_container_job.sh``` is ran to execute the the ToolChains. Currently customized for EventBuilding and using the ```EventBuilder``` ToolChain, but can be adapted to any toolchain in ToolAnalysis.

For event building, there are three requirements necessary before executing these scripts:
1. Ensure you are working and submitting grid jobs in your user directory in /scratch ```/pnfs/annie/scratch/users/<user>```.
2. You need a tarball of ToolAnalysis (you can do this via: ```tar -czvf <archive_name>.tar.gz -C /path <folder_name>```). Jobs will grab this file from the current working directory as outlined above.
3. If you are building beam or cosmic run data, you should run the ```PreProcessTrigOverlap``` toolchain and produce "trigger overlap files". These files are used by the event building toolchain to fetch triggers that may be stored in neighboring part files. After producing these files, you will need to tar-ball them and copy to ```/pnfs/annie/persistent/processed/trigoverlap``` where the scripts assume the trigoverlap tar-ball will be located (there may already be a trigoverlap tar-ball in that location for the run you are producing). If you are event building source runs, overlap files are not necessary and you can set ```source = False``` in ```auto_submit_job.py``` to skip this step.
  
To execute, run ```python3 auto_submit_job.py```. This will carry out the job submissions with a series of inputs required by the user:
- Run number
- Re-run (if 'y', it will check which jobs failed and resubmit them)
- Overlap (described above, this will automatically be 'n' if source run is specified

For an individual user utilizing this repo, the following changes need to be made:
- Modify ```auto_submit_job.py``` by changing the name of the user, the input and output paths (ideally on /scratch), and the name of the toolanalysis tarball (both the name of the tarball and the underlying directory name that you tar-balled in the first place).
- Specify whether you are building source runs (for trig overlap)
- Changes to other scripts are necessary if you are using it outside of event building
  

```find_missing_files.py``` is useful for checking to see if the event building produced all of the part files. To run it, simply specify the run number: ```python3 find_filesizes.py <RUN_NUMBER>```. After jobs have completed, use ```copy_grid_output.sh``` to copy Processed and Orphan files from your user area in /scratch to /persistent (for copying large amounts of files to /persistent, it is recommended to use ```ifdh cp```). This script will also run ```find_missing_files.py``` to tell you what part files were not successfully produced from your job submissions (and hence were not copied to /persistent). Both scripts should be in the same directory.

Note that the allocated memory and disk space specified in the script may not be sufficient for varying part file submission sizes. The scripts currently estimate the disk space needed based on the number of part files you are submitting per job. The memory allocation requested is 2000MB. Note that some source runs (Laser in particular) contain large part files, so it may be necessary to significantly increase the disk allocation (say to 30 GB). Current allotment for source runs is 10 GB.

To check on your jobs, use: ```jobsub_q -G annie --user <<username>>```

To cancel job submissions, use: ```jobsub_rm -G annie <<username>>```
