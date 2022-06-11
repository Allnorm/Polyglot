@echo off
set interlayer=googlefreeapi
title = Polyglot
cd src
if not exist interlayer (
    echo Interlayer not installed. Please check if the installation is correct.
	pause
	exit
)
if not exist ..\first_launch (
	echo Installing requirements, please wait...
	pip install -r requirements.txt
	cd interlayer
	pip install -r %interlayer%.txt
	cd ..\
	type nul > ..\first_launch
)
python main.py %interlayer%
