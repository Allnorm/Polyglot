# Polyglot
Telegram bot that use any API for translate messages
# How to launch
1. Make any folder and place here "src" folder and launcher file (start.bat/start.sh) for your OS.
2. Launch this file. Bot will install all dependencies and generate a configuration file automatically, taking into account the peculiarities of the functioning of Interlayer.
3. To reinstall dependencies, delete the "first_launch" file.
4. To change the interlayer, change the contents of the variable in the launcher to match the name of the interlayer file in the folder.
# Dependencies for main code
1. PyTelegramBotApi https://github.com/eternnoir/pyTelegramBotAPI, GPL-2.0 License
2. Pillow https://github.com/python-pillow/Pillow, HPND License
3. Pytesseract https://github.com/madmaze/pytesseract, Apache-2.0 License
4. Certifi https://github.com/certifi/python-certifi, Mozilla Public License v. 2.0
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
[Unit]<br>
Description=Polyglot bot<br>
<br>
[Service]<br>
WorkingDirectory=/home/allnorm/polyglot<br>
ExecStart=/home/allnorm/polyglot/start.sh<br>
RestartSec=15s<br>
Restart=on-failure<br>
<br>
[Install]<br>
WantedBy=default.target<br>
