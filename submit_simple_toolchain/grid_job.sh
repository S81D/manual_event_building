#!/bin/bash 
# Author: Steven Doran

# script that executes on the grid node

cat <<EOF
condor   dir: $CONDOR_DIR_INPUT 
process   id: $PROCESS 
output   dir: $CONDOR_DIR_OUTPUT 
EOF

HOSTNAME=$(hostname -f) 
GRIDUSER="<USERNAME>"            # modify

# Argument passed through job submission
JOBNAME=$1
ARG1=$2         // example arguments
ARG2=$3


# --------------------------------------------------------------------------
# Create a dummy log file in the output directory to track progress / errors
DUMMY_OUTPUT_FILE=${CONDOR_DIR_OUTPUT}/${JOBNAME}_${ARG1}_${ARG2}_${JOBSUBJOBID}_dummy_output    // JOBSUBJOBID is a long multi-digit id # for your grid job
touch ${DUMMY_OUTPUT_FILE}

# keep track of run time
start_time=$(date +%s)   # start time in seconds 
echo "The job started at: $(date)" >> ${DUMMY_OUTPUT_FILE}
echo "" >> ${DUMMY_OUTPUT_FILE}
# --------------------------------------------------------------------------


# Copy datafiles from $CONDOR_INPUT onto worker node (the present working directory will be: /srv)
${JSB_TMP}/ifdh.sh cp -D $CONDOR_DIR_INPUT/ProcessedRawData* . 
${JSB_TMP}/ifdh.sh cp -D $CONDOR_DIR_INPUT/MyToolAnalysis_grid.tar.gz . 

# un-tar Toolanalysis
tar -xzf MyToolAnalysis_grid.tar.gz    
rm MyToolAnalysis_grid.tar.gz


# often times you will need to create a list file for the toolchain, containing the data files you have attached 
FILES_PRESENT=$(ls /srv/Processed* 2>/dev/null | wc -l)
echo "*** There are $FILES_PRESENT files here ***" >> ${DUMMY_OUTPUT_FILE}
ls -v /srv/Processed* >> my_inputs.txt     # create my_inputs.txt for toolchain



# --------------------------------------------------------------------------
# this fixes a weird bug by making sure everything is bind mounted correctly - leave this in
echo "Make sure singularity is bind mounting correctly (ls /cvmfs/singularity)" >> ${DUMMY_OUTPUT_FILE}
ls /cvmfs/singularity.opensciencegrid.org >> ${DUMMY_OUTPUT_FILE}
# --------------------------------------------------------------------------



# Setup singularity container and execute the run_container script (pass any args to the next script)
singularity exec -B/srv:/srv /cvmfs/singularity.opensciencegrid.org/anniesoft/toolanalysis\:latest/ $CONDOR_DIR_INPUT/run_container_job.sh $ARG1 $ARG2

# ------ The script run_container_job.sh will now run within singularity ------ #



# cleanup and move files to $CONDOR_OUTPUT after leaving singularity environment
echo "Moving the output files to CONDOR OUTPUT..." >> ${DUMMY_OUTPUT_FILE} 
${JSB_TMP}/ifdh.sh cp -D /srv/logfile* $CONDOR_DIR_OUTPUT         # log files
${JSB_TMP}/ifdh.sh cp -D /srv/*.csv $CONDOR_DIR_OUTPUT            # Modify: any .root files etc.. that are produced from your toolchain

# --------------------------------------------------------------------------
echo "" >> ${DUMMY_OUTPUT_FILE} 
echo "Input:" >> ${DUMMY_OUTPUT_FILE} 
ls $CONDOR_DIR_INPUT >> ${DUMMY_OUTPUT_FILE} 
echo "" >> ${DUMMY_OUTPUT_FILE} 
echo "Output:" >> ${DUMMY_OUTPUT_FILE} 
ls $CONDOR_DIR_OUTPUT >> ${DUMMY_OUTPUT_FILE} 

echo "" >> ${DUMMY_OUTPUT_FILE} 
echo "Cleaning up..." >> ${DUMMY_OUTPUT_FILE} 
echo "" >> ${DUMMY_OUTPUT_FILE} 
# --------------------------------------------------------------------------

# make sure to be a RESPONSIBLE fermilab user and clean up after yourself! (clean up the files left on the worker node)
rm /srv/Processed* 
rm /srv/*.txt 
rm /srv/*.csv
rm /srv/*.sh
rm -rf /srv/ToolAnalysis/ 

# --------------------------------------------------------------------------
echo "remaining files in srv directory:" >> ${DUMMY_OUTPUT_FILE} 
ls -v /srv >> ${DUMMY_OUTPUT_FILE} 
echo "" >> ${DUMMY_OUTPUT_FILE} 

# log the run time
end_time=$(date +%s)
echo "Job ended at: $(date)" >> ${DUMMY_OUTPUT_FILE}
echo "" >> ${DUMMY_OUTPUT_FILE}
duration=$((end_time - start_time))
echo "Script duration (s): ${duration}" >> ${DUMMY_OUTPUT_FILE}
# --------------------------------------------------------------------------

### END ###
