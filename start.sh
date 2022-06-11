#/bin/bash
cd "$(dirname "$(readlink -f "$0")")"
interlayer="googlefreeapi"
cd src
if ! [ -d interlayer ]; then
    read -p  "Interlayer not installed. Please check if the installation is correct."
	exit
fi
if ! [ -f ../first_launch ]; then
    echo Installing requirements, please wait...
    pip install -r requirements.txt
	cd interlayer
	pip install -r ${interlayer}.txt
	cd ../
	touch ../first_launch
fi
python main.py $interlayer
