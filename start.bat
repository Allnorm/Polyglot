@echo off
title = Polyglot
if not exist "src\interlayer" (
    echo Interlayer not installed. Please check if the installation is correct.
	pause
	exit
)
cd src
python main.py googlefreeapi