## Example grid submission scripts for a toolchain

Example scripts on how to run a simple toolchain on the FermiGrid, using James' container-in-a-container solution. 

Follows closely from the ANNIE wiki: https://cdcvs.fnal.gov/redmine/projects/annie_experiment/wiki/General_guideline_for_running_ANNIE_Singularity_Containers_on_Grid

These scripts run the toolchain, `BeamClusterAnalysis`, which loops over Processed Data files and produces a .root ntuple containing event information.
