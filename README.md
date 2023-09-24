# bomcheckgui
<i>bomcheckgui.py has been converted to exe format.  [Look for it here](https://github.com/kcarlton55/bomcheckgui "bomcheckgui.exe")</i>

### **What the program does**

Bomcheckgui is a graphical user interface (gui) for the [bomcheck](https://github.com/kcarlton55/bomcheck "bomcheck's home") program.
It compares Bills of Materials (BOMs).

### **How to install**
Assuming that you already have Python on your machine, use the package
manager software [pip](https://en.wikipedia.org/wiki/Pip_(package_manager))
that comes with Python, and type this on on the command line to install:

`pip install bomcheckgui`

This will also automatically install bomcheck if it is not already installed on
your machine

### **How to run**

To run the program, from the command line, enter:

`bomcheckgui`

### **How it works**

Drag and drop the BOM files that you want to be checked onto bomcheckgui's
drag/drop window.  Click the green check mark icon to generate results.
(See bomcheck's help section for additional information)

### **bomcheck.cfg**
Bomcheck has a configuration file available named bomcheck.cfg.  With it the
default Unit of Measure (U/M) can be switched from inches to mm or to some
other U/M.  Also, column header names can be changed to suit the user's needs.
Within the bomcheck.cfg file are explanations about what settings that can be
employed.  To get started, download bomcheck.cfg from
[https://github.com/kcarlton55/bomcheck/tree/master/doc](https://github.com/kcarlton55/bomcheck/tree/master/docs),
save to your local disk, then open with text editor and modify it as you like.
Afterwards go to bomcheckgui's settings and point the program to your config
file.