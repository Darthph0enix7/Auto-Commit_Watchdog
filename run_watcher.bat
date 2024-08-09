@echo off
echo Running watcher.py
cd %~dp0
python watcher.py > script_output.log 2>&1
echo watcher.py script started
pause