# Polyglot
Telegram bot that use any API for translate messages
# How to use as binary file
1. Make any folder and place binary there
2. Start the bot for initial configuration. Bot will have to generate a configuration file automatically, taking into account the peculiarities of the functioning of Interlayer.
# How to use as sorce code
1. Make any folder and place sources there
2. Create folder "interlayer" in project root
3. Place one of your chosen interlayer files in this folder (ready-made assemblies are here: https://github.com/Allnorm/Polyglot-Interlayer)
4. Uncomment string "import interlayer.%filename% as interlayer" in utils.py
5. Install all need dependencies for main code and interlayer
6. Launch main.py. Bot will have to generate a configuration file automatically, taking into account the peculiarities of the functioning of Interlayer.
# How to build binary file
We using Pyinstaller for project building (https://pyinstaller.readthedocs.io/en/stable/)
You need to install all dependencies and launch command "pyinstaller --onefile -i icon.ico --add-data locales-list.json;. main.py"
Some interlayers may have special features when assembling. This should be specified by the author of the interlayer.
# Dependencies for main code
1. PyTelegramBotApi https://github.com/eternnoir/pyTelegramBotAPI, GPL-2.0 License
2. Pillow https://github.com/python-pillow/Pillow, HPND License
3. Pytesseract https://github.com/madmaze/pytesseract, Apache-2.0 License
# Possible obscure items in the configuration file without items added by Interlayer
* token - Telegram bot's token
* max-inits - sets the maximum amount of text distortion allowed. Can be from 0 (function disabled) to 100
* locales-repository - the repository from which the localization file will be loaded. If you run the bot with the -l switch, it will copy its own localization file built into it.
* msg-logging - if true, the bot writes to the log who exactly used his commands. If debug is enabled - adds message content
* enable-auto - enables and disables automatic translations
* pytesseract - path to Tesseract-OCR executable library, usually needed for Windows. Set to "disable" to fully disable this function
* len-limit - limit the length of the input message. 0 - disables the restriction. May be useful for some Interlayers.
* enable-ad - boolean variable, enable or disable the ad engine
* ad-percent - indicates the percentage of the ad display frequency
* distort-output - a boolean variable, indicates whether to show the languages in which the distortion occurred
# An example of a working systemd unit for autoloading
[Unit]
Description=Polyglot bot<br>
<br>
[Service]<br>
WorkingDirectory=/home/allnorm/polyglot<br>
ExecStart=/home/allnorm/polyglot/polyglot<br>
RestartSec=15s<br>
Restart=on-failure<br>
<br>
[Install]<br>
WantedBy=default.target<br>
