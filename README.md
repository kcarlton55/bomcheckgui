# bomcheckgui
> <i>bomcheckgui.py has been converted to exe format.  [Click here](https://github.com/kcarlton55/bomcheckgui/releases/tag/v1.9  "website of bomcheckgui.exe") to go to the web page where it is located.</i>

### **What the program does**

Bomcheckgui is a graphical user interface (gui) for the [bomcheck](https://github.com/kcarlton55/bomcheck "bomcheck's home") program.
It compares bills of materials (BOMs).

### **How to install**
Assuming that you already have Python on your machine, use the package
manager software [pip](https://en.wikipedia.org/wiki/Pip_(package_manager))
that comes with Python:

`pip install bomcheckgui`

### **How to run**

To open up the gui, from the command line, or via a link you set up, run:

`bomcheckgui`

### **How it works**

Drag and drop the BOM files that you want to be checked onto the central
portion of the gui.  Click the icon that looks like a green check mark to
generate results.  An Excel file will be created and results stored to it.

### **bomcheck.cfg**
Bomcheck has a configuration file available named bomcheck.cfg.  With it the
default U/M measure can be switched from inches to mm, or to some other U/M.
Also, column names can be changed, and so forth.  Within the bomcheck.cfg
file are explanations about settings that can be employed.  To get started, download
the bomcheck.cfg from [here](https://github.com/kcarlton55/bomcheck/tree/master/docs),
then open the file with a text editor and modify it as suits you best.