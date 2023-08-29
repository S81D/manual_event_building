#!/bin/bash 
# James Minock 

# logfile
touch /srv/logfile_2.txt 

# place the input file containing the necessary data files in the toolchain
echo "my_inputs.txt paths:" >> /srv/logfile_2.txt
cat /srv/my_inputs.txt >> /srv/logfile_2.txt 
\cp /srv/my_inputs.txt /srv/MyToolAnalysis_2_26_23/configfiles/BeamClusterAnalysis/ 
echo "" >> /srv/logfile_2.txt

# enter ToolAnalysis directory 
cd MyToolAnalysis_2_26_23/ 

# set up paths and libraries 
source Setup.sh 

# Run the toolchain, and output verbose to log file 
./Analyse configfiles/BeamClusterAnalysis/ToolChainConfig >> /srv/logfile_beamcluster.txt 

# log files
echo "ToolAnalysis directory contents:" >> /srv/logfile_2.txt
ls -lrth >> /srv/logfile_2.txt
echo "" >> /srv/logfile_2.txt
echo "ToolChain files:" >> /srv/logfile_2.txt
ls configfiles/BeamClusterAnalysis/ >> /srv/logfile_2.txt 
echo "" >> /srv/logfile_2.txt

# copy any produced files to /srv for extraction
cp *.ntuple.root /srv/ 

# make sure any output files you want to keep are put in /srv or any subdirectory of /srv 

### END ###
