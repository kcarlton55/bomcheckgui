:: A batch file to create bomcheckgui.exe from bomcheckgui.py.
:: With Python active and with modules listed in requirements.txt working in
:: a virtual environment, change directory to where you want new files created
:: and run this batch file.  This batch file requires the program 'pyinstaller'
:: to be installed on your machine.

pyinstaller C:\Users\Ken\Documents\shared\projects\bomcheckgui\bomcheckgui.py -w --icon=C:\Users\Ken\Documents\shared\projects\project1\icons\bomcheck.ico

mkdir dist\bomcheckgui\icons
copy C:\Users\Ken\Documents\shared\projects\bomcheckgui\icons dist\bomcheckgui\icons

mkdir dist\bomcheckgui\help_files
copy C:\Users\Ken\Documents\shared\projects\bomcheckgui\help_files dist\bomcheckgui\help_files

mkdir dist\bomcheckgui\sourcefiles
copy C:\Users\Ken\Documents\shared\projects\bomcheckgui\* dist\bomcheckgui\sourcefiles

copy C:\Users\Ken\Documents\shared\projects\bomcheckgui\bc_config\bc_config.py dist\bomcheckgui\

mkdir dist\bomcheckgui\sourcefiles\bc_config
copy C:\Users\Ken\Documents\shared\projects\bomcheckgui\bc_config dist\bomcheckgui\sourcefiles\bc_config


