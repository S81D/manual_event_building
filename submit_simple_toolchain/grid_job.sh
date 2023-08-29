#!/bin/bash 
# From James Minock 

cat <<EOF
condor   dir: $CONDOR_DIR_INPUT 
process   id: $PROCESS 
output   dir: $CONDOR_DIR_OUTPUT 
EOF

HOSTNAME=$(hostname -f) 
GRIDUSER="doran"            # modify

# Create a dummy log file in the output directory
DUMMY_OUTPUT_FILE=${CONDOR_DIR_OUTPUT}/${JOBSUBJOBID}_dummy_output 
touch ${DUMMY_OUTPUT_FILE} 

# Copy datafiles from $CONDOR_INPUT onto worker node (/srv)
${JSB_TMP}/ifdh.sh cp -D $CONDOR_DIR_INPUT/ProcessedRawData* . 
${JSB_TMP}/ifdh.sh cp -D $CONDOR_DIR_INPUT/MyToolAnalysis_grid.tar.gz . 
${JSB_TMP}/ifdh.sh cp -D $CONDOR_DIR_INPUT/my_inputs.txt . 

# un-tar TA
tar -xzf MyToolAnalysis_grid.tar.gz    
rm MyToolAnalysis_grid.tar.gz

# Setup singularity container 
singularity exec -B/srv:/srv /cvmfs/singularity.opensciencegrid.org/anniesoft/toolanalysis\:latest/ $CONDOR_DIR_INPUT/run_container_job.sh 

# ------ The script run_container_job.sh will now run within singularity ------ #


# cleanup and move files to $CONDOR_OUTPUT after leaving singularity environment
echo "Moving the output files to CONDOR OUTPUT..." >> ${DUMMY_OUTPUT_FILE} 
${JSB_TMP}/ifdh.sh cp -D /srv/logfile* $CONDOR_DIR_OUTPUT         # log files
${JSB_TMP}/ifdh.sh cp -D /srv/*.ntuple.root $CONDOR_DIR_OUTPUT    # Modify: any .root files etc.. that are produced from your toolchain

echo "" >> ${DUMMY_OUTPUT_FILE} 
echo "Input:" >> ${DUMMY_OUTPUT_FILE} 
ls $CONDOR_DIR_INPUT >> ${DUMMY_OUTPUT_FILE} 
echo "" >> ${DUMMY_OUTPUT_FILE} 
echo "Output:" >> ${DUMMY_OUTPUT_FILE} 
ls $CONDOR_DIR_OUTPUT >> ${DUMMY_OUTPUT_FILE} 

echo "" >> ${DUMMY_OUTPUT_FILE} 
echo "Cleaning up..." >> ${DUMMY_OUTPUT_FILE} 
echo "srv directory:" >> ${DUMMY_OUTPUT_FILE} 
ls -v /srv >> ${DUMMY_OUTPUT_FILE} 

# make sure to clean up the files left on the worker node
rm /srv/ProcessedRawData* 
rm /srv/my_inputs.txt 
rm -rf MyToolAnalysis_2_26_23/ 

### END ###
