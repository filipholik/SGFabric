# SGFabric
Modified files from SGSim and BPFabric to build an emulated Smart Grid network controlled by eBPF functions.    
Contains glue files which have to be added to SGSim and BPFabric (or have to replace original files).    

# Requirements
Requires current version of BPFabric and SGSim.  
Dashboard requires Gradient Able Flask. 

# Installation
BPFabric: apt-get install gcc-multilib protobuf-compiler protobuf-c-compiler libprotobuf-c-dev libprotobuf-dev clang-14 git python3-protobuf python3-twisted

SGSim: apt-get install mininet
git clone https://github.com/filipholik/SmartGridSim 
unzip SmartGridSim/comlib_dps.zip -d SmartGridSim
unzip SmartGridSim/comlib_dss.zip -d SmartGridSim

# Topology 
![SGFabric topology](https://github.com/filipholik/SGFabric/blob/main/SGFabric.png)

# Usage
Add / replace corresponding files in BPFabric and SGSim.   

Printing maps tables:  
8 table 0 list   
8 table 0 assetdisc list  

Read Scripts/guide.txt for further instructions. 
