# Ayesaac
Integrating a helpful computer vision aid for the Alana platform.


## Setup
0. Clone this repo. You probably already did this. Well done!

1. Get the Alana utils key for the code that must not be published. 
    This is a cryptographic key that authenticates the github repo to let you download it. 
    Get it from an email or slack or however I end up sharing it and save the file in the project folder next to this README.


2. Run bash in this folder
    On Linux/Mac, this is just opening a terminal window.
    On windows, you need another program.
        Fortunately, if you cloned this repo then you should have git for windows, which comes with its own bash terminal that works (or use Cygwin if you like that sort of thing).
            
        From the start menu, type "git bash" and it should give you the option to launch the app. 
        If you don't have it, download from here: https://www.git-scm.com/download/win
        
        cd to this folder fixing the path slash directions - for example for me that is 
            folder in windows:
                D:\Projects\Ayesaac 
            -> command in bash:
                cd /d/projects/Ayesaac  
    

3. Run setup script
    bash environment_setup.sh


4. (For if you want to use PyCharm) If you do use or want to use PyCharm (and consider it - it's good), set the project interpreter to use the anaconda environment created in that setup script
    If you don't do this, running python in PyCharm won't find any of the dependencies we just installed.
    
    From the command line, type 
        conda env list
    to get the path next to the name "Ayesaac"; copy it.

    File -> Settings
        Project:Ayesaac -> Project Interpreter -> click the cog icon near the top right -> Add...
            Conda Environment -> Existing environment -> ... -> paste your directory into the box choose the "python.exe" in that location
            