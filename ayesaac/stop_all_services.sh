#!/usr/bin/env bash

# stop all the process name "./main.py" which are our process launch by start_all_services.sh
# /!\ warning if you have other script running on your pc named './main.py' they will be stopped too
# it can be checked by going to your terminal -> enter 'ps aux | grep -i ./main.py'
# if nothing is output except this one line containing 'grep --color=auto --exclude-dir=.bzr --exclude-dir=CVS --exclude-dir=.git --exclude-dir=.hg --exclude-dir=.svn -i ./main.py'
# which the grep command itself then it should work
pkill -f ./main.py

# run a script to delete the queues in case their were a crash in one of the modules
# and the queue were either not properly closed or the messages where stacking in a queue
# they will be restart
python3 ./services_lib/queues/delete_queues.py