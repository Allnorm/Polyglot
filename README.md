# Polyglot
Telegram bot that use Google Api for translate messages
# How to use as binary file
1. Make any folder and place binary there
2. Start the bot for initial configuration (more in the section about the config file)
# How to use as sorce code
1. Make any folder and place sources there
2. Create folder "interlayer" in project root
3. Place one of your chosen interlayer files in this folder (ready-made assemblies are here: https://github.com/Allnorm/Polyglot-Interlayer)
4. Uncomment string "import interlayer.%filename% as interlayer" in utils.py
5. Install all need dependencies for main code and interlayer
6. Launch main.py
# How to build binary file
We using Pyinstaller for project building (https://pyinstaller.readthedocs.io/en/stable/)
You need to install all dependencies and launch command "pyinstaller --onefile -i icon.ico --add-data locales-list.json;. main.py"
Some interlayers may have special features when assembling. This should be specified by the author of the interlayer.
# Dependencies for main code
1. PyTelegramBotApi https://github.com/eternnoir/pyTelegramBotAPI, GPL-2.0 License
2. Pillow https://github.com/python-pillow/Pillow, HPND License
3. Pytesseract https://github.com/madmaze/pytesseract, Apache-2.0 License
