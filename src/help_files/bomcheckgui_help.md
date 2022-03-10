# bomcheckgui help

    Introduction
    How to run bomcheck
    [bomcheck_help](bomcheck_help.html)
    [Troubleshooting](bomcheck_troubleshooting.md)

## Introduction

The bomcheck program was originally written to be run from a Command Prompt Terminal (cmd.exe). The program bomcheckgui is actually a wrapper that presents a graphical user interface (gui) for the bomcheck program. That is, bomcheckgui runs the bomcheck program in the background. See bomcheck_help.html for info about how bomcheck works.
How to run bomcheckgui:

Drag and drop the BOM files that you want to be checked onto the central portion of the gui. File names that do not end with *_sw.xlsx, _sw.csv, sl_xlsx, or sl.csv* will be ignored. Files that contain a tilde character, ~, will also be ignored. (Yes, csv files can work, but they can be problematic.)

Press the green check button icon to run bomcheckgui and have your BOMs checked. An Excel file with results will then be displayed. The location of the results file will be shown in the bottom of the bomcheckgui window or in a pop-up window. The file location will be the same as that of the files that were checked. If checked files come from more than one folder, bomcheck will select one of those folders to place the results in.

If you wish to check other BOM files, push the clear button to clear the list of files. Then drag and drop the new files you want checked.

If at some point in your work day you close the folder that contains your BOMs, and later you want to reopen it to make changes, instead of having to search for that folder again, click on the folder icon. The folder will open.

**Tip**: Instead of dragging individual file names into the bomcheckgui program, you can drag in the folder that contains the files that are to be checked. Then once the program is run, the program's action will be to do a bom check of the files in that folder. The advantage of doing it this way is that files in a Microsoft File Explorer window can be updated without having to clear previous selections from bomcheckgui and then dragging in new ones.
