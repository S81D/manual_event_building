# FermiGrid_Scripts

Scripts to submit jobs to the grid. Utilizes James Minock's container-within-a-container solution.

-----------------------
Contains two files, ```submit_jobs.py``` and ```auto_submit_job.py```. The former contains functions that are called by the latter to create three scripts to be run on the grid. ```submit_grid_job.sh``` sends the actual job and the associated files + input/output path locations. ```grid_job.sh``` is what is actually ran by the worker node, and after entering our container, ```run_container_job.sh``` is ran to execute the the ToolChains. Currently customized for EventBuilding, primarily by using the ```DataDecoder``` ToolChain.


The only pre-requirement is to have the ```ANNIE_RunInformation_PSQL.txt``` present in your input directory. This is necessary for running the ```BeamFetcher``` pre-processing toolchain, which fetches and stores beam-related information from the IF beam database. Populate the txt file with the desired run information from the ANNIE SQL Database webpage (https://anniedata.fnal.gov/daq/SQL.html). Finally, run ```python3 auto_submit_job.py``` to execute the job submission. User inputs are required, asking which run and how many part files you wish to produce. 

In addition, some ToolChains are sensitive to Daylight Savings, so ensure those files within your ToolAnalysis tar-ball are properly adjusted. 

```find_filesizes.py``` is useful for checking to see if the event building produced all of the part files. It's tedious to go through and find discrepencies when there are 100's of part files. It will also output the avg, min, and max filesizes of the raw data (useful for the logbook). To run it, simply specify the run number: ```python3 find_filesizes.py <RUN_NUMBER>```.

** To Do: 
- Integrate Andrew's new BeamFetcher tool into event building
- Automated Daylight Savings change to configuration files in MRD-related tools
- Add finalized Data Processing ToolChain, once it is complete
