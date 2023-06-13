# FermiGrid_Scripts

Scripts to submit jobs to the grid. Utilizes James Minock's container-within-a-container solution.

-----------------------
Contains two files, ```submit_jobs.py``` and ```auto_submit_job.py```. The former contains functions that are called by the latter to create three scripts to be run on the grid. ```submit_grid_job.sh``` sends the actual job and the associated files + input/output path locations. ```grid_job.sh``` is what is actually ran by the worker node, and after entering our container, ```run_container_job.sh``` is ran to execute the the ToolChains. Currently customized for EventBuilding, primarily by using the ```DataDecoder``` ToolChain.

The only pre-requirement are to run the ```BeamFetcher``` ToolChain in ToolAnalysis to produce the necessary ```<RUN_NUMBER>_beamdb``` files and to tarball ToolAnalysis (you can do this via: ```tar -czvf <archive_name>.tar.gz <folder_name>)``` . Drop those into your input location, then run ```python3 auto_submit_job.py``` to execute the job submission. User inputs are required, asking which run and how many part files you wish to produce. 

For an individual user utilizes this repo, the following changes need to be made:
- Modify ```auto_submit_job.py``` by changing the name of the user, the input and output paths (ideally on /scratch), and the name of the toolanalysis tarball (both the name of the tarball and the underlying directory name that you tar-balled in the first place).

Keep in mind that all scripts, the TA tarball, and beamdb file should be placed within your input path location that you set in ```auto_submit_job.py```. No files or scripts need to be put in the output location, as a directory (name = run number) will automatically be created there where the output files from your job + any log files will be deposited. There is also a rawdata path that pulls the raw data from /pnfs. This does not need to be modified for individual users.

In addition, some ToolChains are sensitive to Daylight Savings, so ensure those files within your ToolAnalysis tar-ball are properly adjusted. 

```find_filesizes.py``` is useful for checking to see if the event building produced all of the part files. It's tedious to go through and find discrepencies when there are 100's of part files. It will also output the avg, min, and max filesizes of the raw data (useful for the logbook). To run it, simply specify the run number: ```python3 find_filesizes.py <RUN_NUMBER>```.

** To Do: 
- Integrate Andrew's new BeamFetcher tool into event building
- Automated Daylight Savings change to configuration files in MRD-related tools
- Add finalized Data Processing ToolChain, once it is complete
