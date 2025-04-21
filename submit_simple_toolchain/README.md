## Example grid submission scripts for a toolchain

Example scripts on how to run a simple toolchain on the FermiGrid, using James' container-in-a-container solution. 

Follows closely from the ANNIE wiki: https://cdcvs.fnal.gov/redmine/projects/annie_experiment/wiki/General_guideline_for_running_ANNIE_Singularity_Containers_on_Grid

These scripts run the toolchain, `PrintDQ`, which loops over Processed Data files and produces a .csv file containing data quality metrics.

A tutorial video on how to use the grid can be found here: https://annie-docdb.fnal.gov/cgi-bin/sso/ShowDocument?docid=5241 

## Usage

- Edit scripts accordingly to suite your needs, including the username and the appropriate path locations
- `sh submit_grid_job.sh`

### Additional information

It is very important to first TEST your toolchain locally to ensure it is working properly before submission. We are all stewards of the grid, and with that comes the responsibility to try and be efficient with your requested resources. General recommendations for memory, disk, and wall time can be found in the `submit_grid_job.sh` script. 

Please start small by submitting only a few test jobs to see how much resources you will need, and if your workflow is bug-free. Utilize the log scripts to help you with debugging. Information on your efficiency and the resources used by your jobs can be found here: https://fifemon.fnal.gov/monitor/d/000000167/user-batch-history?from=now-24h&to=now&var-user=<YOUR_USERNAME_HERE>&orgId=1&refresh=5m

Edit the above <YOUR_USERNAME_HERE> within the link.

----------------

To check on your jobs, use: jobsub_q -G annie --user <<username>>

To cancel job submissions, use: jobsub_rm -G annie <<username>>

To check why jobs are held, use: jobsub_q --hold -G annie <<username>>
