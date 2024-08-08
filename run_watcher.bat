@echo off
cd %~dp0
start "" pythonw watcher.py 1>script_output.log 2>&1
