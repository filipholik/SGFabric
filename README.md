# SGFabric
Modified files from SGSim and BPFabric to build an emulated Smart Grid network controlled by eBPF functions.    
Contains glue files which have to be added to SGSim and BPFabric (or have to replace original files).    

# Requirements
Requires current version of BPFabric and SGSim.  
Dashboard requires Gradient Able Flask. 

# TODO
Create a storage on the controller for caching content of eBPF maps.    

# Topology 
![SGFabric topology](https://github.com/filipholik/SGFabric/blob/main/SGFabric.png)

# Usage
Add / replace corresponding files in BPFabric and SGSim.   

Printing maps tables:  
8 table 0 list   
8 table 0 assetdisc list  
