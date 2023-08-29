export INPUT_PATH=/pnfs/annie/scratch/users/doran/                       # Specify path of submission scripts
export DATA_PATH=/pnfs/annie/persistent/processed/processed_hits/R4314/  # For ToolChain, ProcessedData path

QUEUE=medium 

OUTPUT_FOLDER=/pnfs/annie/scratch/users/doran/output/beamcluster_test    # path where created files from your grid job will be placed
mkdir -p $OUTPUT_FOLDER                                                 

# wrapper script to submit your grid job
jobsub_submit --memory=4000MB --expected-lifetime=${QUEUE} -G annie --disk=30GB --resource-provides=usage_model=OFFSITE --site=Colorado,BNL,Caltech,Nebraska,SU-OG,UCSD,NotreDame,MIT,Michigan,MWT2,UChicago,Hyak_CE -f ${DATA_PATH}/ProcessedRawData_TankAndMRDAndCTC_R4314S0p2 -f ${DATA_PATH}/ProcessedRawData_TankAndMRDAndCTC_R4314S0p3 -f ${INPUT_PATH}/my_inputs.txt -f ${INPUT_PATH}/run_container_job.sh -f ${INPUT_PATH}/MyToolAnalysis_grid.tar.gz -d OUTPUT $OUTPUT_FOLDER file://${INPUT_PATH}/grid_job.sh


# First few flags specify the memory and disk allocation, and the sites that are "approved" for our nested container workaround.
# The -f flags are the arguments for input files, which will need to be modified as needed. 
# Ensure you are also including/submitting with the -f flag the following files:
    # - run_container_job.sh script, which is the script that will be executed within singularity.
    # - ToolAnalysis tar-ball
    # - Processed or RAW data files that are needed to run the toolchain
# -d is the output directory where completed/processed files from your grid job will be deposited on the anniegpvms
# Lastly, file://.... is the actual job script that will execute on the worker node.
