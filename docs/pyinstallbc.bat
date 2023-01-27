:: A batch file to create bomcheckgui.exe from bomcheckgui.py.
:: With Python active and with modules listed in requirements.txt working in
:: a virtual environment, change directory to where you want new files created
:: and run this batch file.  This batch file requires the program 'pyinstaller'
:: to be installed on your machine.

pyinstaller -w --icon=C:\Users\Ken\Documents\shared\projects\bomcheckgui\bomcheck.ico C:\Users\Ken\Documents\shared\projects\bomcheckgui\src\bomcheckgui.pyw 


