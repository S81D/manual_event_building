#!/bin/bash 
# Steven Doran

# job script that runs within the container and executes your toolchain

ARG1=$1     # example arguments passed down
ARG2=$2     # use these in the script as needed

# ------------------------------------------
# logfile for toolchain verbose
touch /srv/logfile_${ARG1}_${ARG2}.txt 

# for toolchains that need a list file: place the input file containing the necessary data files in the toolchain
rm /srv/DQ_tool//configfiles/PrintDQ/my_inputs.txt      # in case there is conflict with overwite
\cp /srv/my_inputs.txt /srv/ToolAnalysis/configfiles/PrintDQ/ 

echo "my_inputs.txt paths:" >> /srv/logfile_${ARG1}_${ARG2}.txt    # verify files are as expected
cat /srv/my_inputs.txt >> /srv/logfile_${ARG1}_${ARG2}.txt  
echo "" >> /srv/logfile_${ARG1}_${ARG2}.txt 
# ------------------------------------------


# enter ToolAnalysis directory 
cd ToolAnalysis/ 

# set up paths and libraries 
source Setup.sh 

echo "Running Toolchain..." >> /srv/logfile_${ARG1}_${ARG2}.txt 
echo "" >> /srv/logfile_${ARG1}_${ARG2}.txt 

# Run the toolchain, and output verbose to log file 
./Analyse configfiles/PrintDQ/ToolChainConfig >> /srv/logfile_${ARG1}_${ARG2}.txt 2>&1   # re-direct all stderr messages to this logfile


# ------------------------------------------
# check what files are created (for debugging)
echo "" >> /srv/logfile_${ARG1}_${ARG2}.txt 
echo "ToolAnalysis directory contents:" >> /srv/logfile_${ARG1}_${ARG2}.txt 
ls -lrth >> /srv/logfile_${ARG1}_${ARG2}.txt 
echo "" >> /srv/logfile_${ARG1}_${ARG2}.txt 
# ------------------------------------------


# copy any produced files to /srv for extraction
cp *.csv /srv/ 

# make sure any output files you want to keep are put in /srv or any subdirectory of /srv 

### END ###
