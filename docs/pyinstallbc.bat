:: A batch file to create bomcheckgui.exe from bomcheckgui.py.
:: With Python active and with modules listed in requirements.txt working in
:: a virtual environment, change directory to where you want new files created
:: and run this batch file.  This batch file requires the program 'pyinstaller'
:: to be installed on your machine.

pyinstaller C:\Users\Ken\Documents\shared\projects\bomcheckgui\bomcheckgui.py -w --icon=C:\Users\Ken\Documents\shared\projects\project1\icons\bomcheck.ico


