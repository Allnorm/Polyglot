@echo off
set interlayer=googlefreeapi
title = Polyglot
if not exist src\interlayer (
    echo Interlayer not installed. Please check if the installation is correct.
	pause
	exit
)
if not exist first_launch (
	echo Installing requirements, please wait...
	pip install -r requirements.txt
	cd src\interlayer
	pip install -r %interlayer%.txt
	cd ..\..\
	type nul > first_launch
)
cd src
python main.py %interlayer%