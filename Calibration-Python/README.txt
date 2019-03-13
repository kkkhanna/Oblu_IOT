Please follow the instructions below to generate the calibration file.

1. Installing Anaconda 2

   Download and install the Anaconda 2 (python 2.7 version)for windows from 
   http://continuum.io/downloads. 
   For more details visit http://conda.pydata.org/docs/install/full.html.

2. Installing the modules

   Install the modules matplotlib, pyserial, scipy, termcolor.
   There can be many ways to install the modules. Installing using
   conda is the easiest easy.
   	a.Go to the folde Scripts under anaconda2 in C.
   	b.Open the command prompt there and type the following command
   	c.conda install <module name>
   If the module is already installed update to the recent version using
        conda update <module name>
   If it does not install, go for Christoph Gohlke's binaries. 
   Download the required binaries and install using the command
        conda install <path/to/the/binary/with/name>
   For more info visit http://conda.pydata.org/docs/faq.html#conda-pip-and-virtualenv
	
3. Instaliing Pycharm

   Download and install Pycharm Community executable from 
   https://www.jetbrains.com/pycharm/download/download-thanks.html?platform=windows&code=PCC.
   For more details visit https://www.jetbrains.com/pycharm-edu/quickstart/installation.html.

4. Additional Equipment required

   Icosahedron: This script/app makes use of the icosahedron to get the 
   data of each phase to generate the calibration file.

5. Running the script to generate calibration file(.h) 
   
   a. In the folder calibration_file_python you will find the file named "main". 
   b. Open it in pycharm and change the com_port value to current port address of the module. 
   c. Go to File --> Default settings. In the Project Interpreter select Anaconda 2. Click Apply. 
      (This is a one time initial setup. Need not repeat it in future runs.)
   d. Now run the file in pycharm. Follow the instructions given in terminal 
   e. After successful completion the calibration file will be generated and stored in the same folder. 


Note to developer:

   To view the individual side data in graph plz uncomment line 170 in extract_stationary_segments.py.
   During run time after each side, close the graph to proceed to next step.



