import sys

# this file can be called to produce the necessary grid submission scripts


# this script is for actually submitting the job to the FermiGrid
def submit_grid_job(run, p_start, p_end, script_path, input_path, output_path, TA_tar_name):
    
    file = open('submit_grid_job.sh', "w")

    file.write('export SCRIPT_PATH=' + script_path + '\n')
    file.write('export INPUT_PATH=' + input_path +  '\n')
    file.write('export RAWDATA_PATH=/pnfs/annie/persistent/raw/raw/' + run + '/ \n')
    file.write('\n')
    file.write('QUEUE=medium \n')
    file.write('\n')
    file.write('OUTPUT_FOLDER=' + output_path + run + '\n')
    file.write('mkdir -p $OUTPUT_FOLDER \n')
    file.write('\n')
    file.write('jobsub_submit --memory=4000MB --expected-lifetime=${QUEUE} -G annie --disk=30GB --resource-provides=usage_model=OFFSITE --site=Colorado,BNL,Caltech,Nebraska,SU-OG,Wisconsin,UCSD,NotreDame,MIT,Michigan,MWT2,UChicago,Hyak_CE ')

    for i in range(int(p_start), int(p_end)+1):
        file.write('-f ${RAWDATA_PATH}/RAWDataR' + run + 'S0p' + str(i) + ' ')

    file.write('-f ${INPUT_PATH}/' + run + '_beamdb ')
    #file.write('-f ${INPUT_PATH}/my_files_' + str(p_start) + '_' + str(p_end) + '.txt ')
    file.write('-f ${INPUT_PATH}/run_container_job.sh ')
    file.write('-f ${INPUT_PATH}/' + TA_tar_name + ' ')
    file.write('-d OUTPUT $OUTPUT_FOLDER ')
    file.write('file://${SCRIPT_PATH}/grid_job.sh ' + str(p_start) + '_' + str(p_end) + '\n')
    file.close()

    return


# this next script is what is ran once it is in the grid
def grid_job(user, script_path, TA_tar_name, p_start, p_end):

    file = open(script_path + 'grid_job.sh', "w")

    file.write('#!/bin/bash \n')
    file.write('# From James Minock \n')
    file.write('\n')

    file.write('cat <<EOF\n')
    file.write('condor   dir: $CONDOR_DIR_INPUT \n')
    file.write('process   id: $PROCESS \n')
    file.write('output   dir: $CONDOR_DIR_OUTPUT \n')
    file.write('EOF\n')
    file.write('\n')

    file.write('HOSTNAME=$(hostname -f) \n')
    file.write('GRIDUSER="' + user + '" \n')
    file.write('\n')

    file.write('# Argument passed through job submission \n')
    file.write('PART_NAME=$1 \n')
    file.write('\n')

    file.write('# Create a dummy file in the output directory \n')
    file.write('DUMMY_OUTPUT_FILE=${CONDOR_DIR_OUTPUT}/${JOBSUBJOBID}_dummy_output \n')
    file.write('touch ${DUMMY_OUTPUT_FILE} \n')
    file.write('\n')

    file.write('# Copy datafiles \n')
    file.write('${JSB_TMP}/ifdh.sh cp -D $CONDOR_DIR_INPUT/RAWData* . \n')
    #file.write('${JSB_TMP}/ifdh.sh cp -D $CONDOR_DIR_INPUT/my_files_' + str(p_start) + '_' + str(p_end) + '.txt . \n')
    file.write('${JSB_TMP}/ifdh.sh cp -D $CONDOR_DIR_INPUT/' + TA_tar_name + ' . \n')
    file.write('tar -xzf ' + TA_tar_name + '\n')
    file.write('rm ' + TA_tar_name + '\n')
    file.write('\n')

    file.write('echo "Raw data files in my_files.txt:" >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('ls -v /srv/RAWData* >> my_files.txt \n')
    #file.write('cat my_files_' + str(p_start) + '_' + str(p_end) + '.txt >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('echo "" >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('\n')

    file.write('# Setup singularity container \n')
    file.write('singularity exec -B/srv:/srv /cvmfs/singularity.opensciencegrid.org/anniesoft/toolanalysis\:latest/ $CONDOR_DIR_INPUT/run_container_job.sh $PART_NAME \n')
    file.write('\n')

    file.write('echo "Moving the output files to CONDOR OUTPUT..." >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('\n')

    file.write('${JSB_TMP}/ifdh.sh cp -D /srv/logfile* $CONDOR_DIR_OUTPUT \n')
    file.write('${JSB_TMP}/ifdh.sh cp -D /srv/Orphan* $CONDOR_DIR_OUTPUT \n')
    file.write('${JSB_TMP}/ifdh.sh cp -D /srv/Processed* $CONDOR_DIR_OUTPUT \n')
    file.write('\n')

    file.write('echo "" >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('echo "Input:" >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('ls $CONDOR_DIR_INPUT >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('echo "" >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('echo "Output:" >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('ls $CONDOR_DIR_OUTPUT >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('\n')
    file.write('echo "" >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('echo "Cleaning up..." >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('echo "srv directory:" >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('ls -v /srv >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('rm /srv/RAWData* \n')
    file.write('rm /srv/my_files.txt \n')
    file.write('rm -rf ' + TA_tar_name + '/ \n')
    file.write('### END ###')

    file.close()

    return


# third script is the script that actually execuates the ToolChains once in the singularity environment
def run_container_job(name_TA, p_start, p_end):

    file = open('run_container_job.sh', "w")

    file.write('#!/bin/bash \n')
    file.write('# James Minock \n')
    file.write('\n')

    file.write('PART_NAME=$1 \n')
    file.write('\n')

    file.write('# sanity checks \n')
    file.write('touch /srv/logfile_${PART_NAME}.txt \n')
    file.write('pwd >> /srv/logfile_${PART_NAME}.txt \n')
    file.write('ls -v >>/srv/logfile_${PART_NAME}.txt \n')
    file.write('\n')


    # modify if needed, depending on the TC you are running

    file.write('# copy config files \n')

    #file.write('mv /srv/my_files_' + str(p_start) + '_' + str(p_end) + '.txt /srv/my_files.txt \n')    # previous problem with my_files.txt not copying correctly with multiple submissions
    file.write('cat /srv/my_files.txt >> /srv/logfile_${PART_NAME}.txt \n')
    file.write('\cp /srv/my_files.txt /srv/' + name_TA + '/configfiles/DataDecoder/ \n')
    file.write('\cp /srv/my_files.txt /srv/' + name_TA + '/configfiles/PreProcessTrigOverlap/ \n')
    file.write('\cp /srv/4201_beamdb /srv/' + name_TA + '/ \n')
    file.write('\n')

    file.write('# enter ToolAnalysis directory \n')
    file.write('cd ' + name_TA + '/ \n')
    file.write('\n')

    file.write('# set up paths and libraries \n')
    file.write('source Setup.sh \n')
    file.write('\n')

    file.write('# Run the toolchain \n')
    file.write('./Analyse configfiles/PreProcessTrigOverlap/ToolChainConfig >> /srv/logfile_trig_${PART_NAME}.txt \n')    # produce the trig overlap files
    file.write('./Analyse configfiles/DataDecoder/ToolChainConfig  >> /srv/logfile_DataDecoder_${PART_NAME}.txt \n')               # execute DataDecoder TC (eventbuilding)
    file.write('\n')

    file.write('"" >> /srv/logfile_${PART_NAME}.txt \n')
    file.write('pwd >> /srv/logfile_${PART_NAME}.txt \n')
    file.write('ls -lrth >> /srv/logfile_${PART_NAME}.txt \n')
    file.write('ls configfiles/DataDecoder/ >> /srv/logfile_${PART_NAME}.txt \n')
    file.write('\n')

    file.write('# copy any produced files \n')
    file.write('cp Orphan* /srv/ \n')
    file.write('cp Processed* /srv/ \n')
    file.write('\n')
    file.write('# make sure any output files you want to keep are put in /srv or any subdirectory of /srv \n')
    file.write('\n')
    file.write('### END ###')

    file.close()

    return

'''
# create the file that holds the paths to the raw data files, to be used by DataDecoder and PreProcessTrig
def my_file(run, p_start, p_end):

    file = open('my_files_' + str(p_start) + '_' + str(p_end) + '.txt', "w")

    for i in range(int(p_start), int(p_end)+1):
        file.write('/srv/RAWDataR' + run + 'S0p' + str(i) + '\n')

    file.close()

    return
'''

### done ###




    














