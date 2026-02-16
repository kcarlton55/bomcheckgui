#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 19:47:42 2021

@author: Ken Carlton

A graphical user interface for the bomcheck.py program.

"""


__version__ = '2.5'
__author__ = 'Ken Carlton'

import pdb # use with pdb.set_trace()
import ast
import sys
import os
sys.path.insert(0, '/media/sf_shared/projects/bomcheck/src')
#sys.path.insert(0, 'C:\\Users\\Ken\\Documents\\shared\\projects\\bomcheck\\src')
#sys.path.insert(0, 'C:\\Users\\a90003183\\OneDrive - ONEVIRTUALOFFICE\\python\\projects\\bomcheck\\src')
import qtawesome as qta  # I did use this, but problems with when using python 3.8
import bomcheck
import os.path
import requests
from datetime import date
import pandas as pd
from pathlib import Path
from bomcheck import export2xlsx
from PyQt5 import (QtPrintSupport)
from PyQt5.QtCore import (QAbstractTableModel, Qt)
from PyQt5.QtGui import (QColor, QFont, QKeySequence, QPainter, QTextCursor,
                         QTextDocument, QTextTableFormat, QDoubleValidator, QIcon,
                         QGuiApplication)
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QComboBox, QDialog,
                             QDialogButtonBox, QFileDialog, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QMainWindow, QMessageBox, QPushButton, QStatusBar,
                             QTableView, QTextEdit, QToolBar, QVBoxLayout,
                             QItemDelegate, QTableWidget, QHeaderView,
                             QTableWidgetItem, QAbstractItemView)
printStrs = []
run_bomcheck = True  # this is a global variable used in merge_index(), MainWindow's execute_search_sm and execute_bomcheck functions

class MainWindow(QMainWindow):
    
    global files
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowIcon(QIcon('check-mark.png'))

        try:
            self.configdb = get_configfn()
            with open(self.configdb, 'r') as file:
                x = file.read()
            self.dbdic = ast.literal_eval(x)
        except Exception as e:
            msg = ("Error 101:\n\n"
                   "Unable to open config.txt file which allows the program\n"
                   "to remember user settings.  Default settings will be used.\n"
                   "Otherwise the program will run as normal.\n\n" + str(e))
            msgtitle = 'Warning'
            message(msg, msgtitle, msgtype='Warning', showButtons=False)
            self.dbdic = {'udrop': '3*-025', 'uexceptions': '', 
                          'folder': '', 'file2save2': 'bomcheck',
                          'prod_folder': None, 'proj_folder': None,
                          'eng_planner': None}
            self.configdb = ''

        # Check for later software version.  If newer version found, inform user.
        self.chkcount = check_latest_version(self.dbdic.get('version_check_count', 0))

        self.folder = self.dbdic.get('folder', '') # get the working directory where user's bom excel files last came from

        file_menu = self.menuBar().addMenu('File')
        help_menu = self.menuBar().addMenu('Help')
        self.setWindowTitle('bomcheck')
        self.setMinimumSize(925, 300)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        btn_ac_execute = QAction(qta.icon("fa5s.play-circle", color="#228B22"), 'Run bomcheck', self)
        btn_ac_execute.triggered.connect(self.execute_bomcheck)
        btn_ac_execute.setStatusTip('Run bomcheck, i.e. compare SW BOM to SL BOM')
        toolbar.addAction(btn_ac_execute)

        btn_ac_search = QAction(qta.icon("fa6.circle-play", color="#228B22"), 'Run comparator', self)
        btn_ac_search.triggered.connect(self.execute_search_sm)
        btn_ac_search.setStatusTip('Compare SW/SL BOM to SM BOM')
        toolbar.addAction(btn_ac_search)

        btn_ac_clear = QAction(qta.icon("fa6s.x", color="#228B22"), 'Clear drag-drop zone', self)
        btn_ac_clear.triggered.connect(self.clear)
        btn_ac_clear.setStatusTip('Clear drag-drop zone')
        toolbar.addAction(btn_ac_clear)

        btn_ac_folder = QAction(qta.icon("mdi6.folder-arrow-right", color="#228B22"), "Open last used folder", self)
        btn_ac_folder.triggered.connect(self.openfolder)
        btn_ac_folder.setStatusTip('Open last used folder')
        toolbar.addAction(btn_ac_folder)

        empty_label1 = QLabel()
        empty_label1.setText('   ')
        toolbar.addWidget(empty_label1)

#####################################################################
        pn_filter_label = QLabel()
        pn_filter_label.setText('filter:')
        pn_filter_label.setStatusTip('....-....-   finds slow moving (sm) pt nos that begin with, for example, 3002-0430 and 6415-0300.  .......  (i.e. 7 dots) will find 3001170 and 2008950.  (filter is regex)' )
        toolbar.addWidget(pn_filter_label)

        self.pn_filter_input = QLineEdit()
        self.pn_filter_input.setText('....-....-')
        self.pn_filter_input.setFixedWidth(250)
        self.pn_filter_input.setStatusTip('....-....-   finds slow moving (sm) pt nos that begin with, for example, 3002-0430 and 6415-0300.  .......  (i.e. 7 dots) will find 3001170 and 2008950.  (filter is regex)' )
        toolbar.addWidget(self.pn_filter_input)

        similarity_filter_label = QLabel()
        similarity_filter_label.setText('    % similarity:')
        similarity_filter_label.setStatusTip('% of similarity between SW/SL descrip and SM descrip.  Below this amount will be filtered out.')
        toolbar.addWidget(similarity_filter_label)

        self.similarity_filter_input = QLineEdit()
        self.similarity_filter_input.setText('0')
        self.similarity_filter_input.setFixedWidth(30)
        self.similarity_filter_input.setAlignment(Qt.AlignRight)
        self.similarity_filter_input.setStatusTip('% of similarity between SW/SL descrip and SM descrip.  Below this amount will be filtered out.' )
        toolbar.addWidget(self.similarity_filter_input)

        age_filter_label = QLabel()
        age_filter_label.setText('    on shelf > ')
        age_filter_label.setStatusTip('Show only SM part nos. for parts that have "on shelf" age older than this many days.')
        toolbar.addWidget(age_filter_label)

        self.age_filter_input = QLineEdit()
        self.age_filter_input.setText('0')
        self.age_filter_input.setFixedWidth(35)
        self.age_filter_input.setAlignment(Qt.AlignRight)
        self.age_filter_input.setStatusTip('Show only SM part nos. for parts that have "on shelf" age older than this many days.')
        toolbar.addWidget(self.age_filter_input)
        
        merge_filter_label = QLabel()
        merge_filter_label.setText('    switches: ')
        merge_filter_label.setStatusTip('1) Include Demand (scheduled) pns.    2) Include On Hand pns.    3) Ignore drop list settings.')
        toolbar.addWidget(merge_filter_label)
                
        self.show_demand_chkbox = QCheckBox()
        self.show_demand_chkbox.setLayoutDirection(Qt.RightToLeft)
        self.show_demand_chkbox.setText("1)")
        self.show_demand_chkbox.setChecked(False)
        self.show_demand_chkbox.setStatusTip('1) Include both Demand (i.e. scheduled) and No Demand pt nums. The default is to filter out parts that have a Demand.')
        toolbar.addWidget(self.show_demand_chkbox)
        
        self.onhand_chkbox = QCheckBox()
        self.onhand_chkbox.setLayoutDirection(Qt.RightToLeft)
        self.onhand_chkbox.setText(" 2)")
        self.onhand_chkbox.setChecked(False)
        self.onhand_chkbox.setStatusTip('2) Include all "Qty On Hand" pt nums. The default is to filter out "Qty On Hand" parts that are zero.')
        toolbar.addWidget(self.onhand_chkbox)
        
        self.drop_chkbox = QCheckBox()
        self.drop_chkbox.setLayoutDirection(Qt.RightToLeft)
        self.drop_chkbox.setText(" 3)")
        self.drop_chkbox.setChecked(False)
        self.drop_chkbox.setStatusTip('3) Ignore drop list settings (See File > Settings > drop list).')
        toolbar.addWidget(self.drop_chkbox)

        fileopen_action = QAction(qta.icon("ei.folder-open", color="#228B22"), '&Open', self)
        fileopen_action.setShortcut(QKeySequence.Open)
        fileopen_action.triggered.connect(self.fileopen)
        file_menu.addAction(fileopen_action)

        execute_action = QAction(qta.icon("fa5s.play-circle", color="#228B22"), 'Run bomcheck', self)
        execute_action.triggered.connect(self.execute_bomcheck)
        file_menu.addAction(execute_action)
        
        execute_action = QAction(qta.icon("fa6.circle-play", color="#228B22"), 'Run comparator', self)
        execute_action.triggered.connect(self.execute_search_sm)
        file_menu.addAction(execute_action)

        settings_action = QAction(qta.icon("ei.wrench-alt", color="#228B22"), 'Settings', self) # was fa.gear, then was fa6.sun
        settings_action.triggered.connect(self.settings)
        file_menu.addAction(settings_action)

        quit_action = QAction(qta.icon("mdi.location-exit", color="#CC0000"), '&Quit', self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        help_action = QAction(qta.icon("ei.question-sign", color="#228B22"), 'bomcheck_help', self) # was fa.question, then was fa6.hand-point-right
        help_action.setShortcut(QKeySequence.HelpContents)
        help_action.triggered.connect(self._help)
        help_menu.addAction(help_action)
       
        helpslow_action = QAction(qta.icon("ei.question-sign", color="#228B22"), 'slow moving help', self)   # was fa.question, then was fa6.hand-point-right
        helpslow_action.triggered.connect(self._helpslow)
        help_menu.addAction(helpslow_action)

        helptrb_action = QAction(qta.icon("ei.question-sign", color="#228B22"), 'Troubleshoot', self)  # was fa.question, then was fa6.hand-point-right
        helptrb_action.triggered.connect(self._helptroubleshoot)
        help_menu.addAction(helptrb_action)

        separator = QAction(self)
        separator.setSeparator(True)
        help_menu.addAction(separator)

        bcgui_license = QAction(qta.icon("ei.info-circle", color="#228B22"), 'License', self)
        bcgui_license.triggered.connect(self._bcgui_license)
        help_menu.addAction(bcgui_license)

        about_action = QAction(qta.icon("ei.info-circle", color="#228B22"), '&About', self)
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.lstbox_view = ListboxWidget(self)
        self.lstbox_view.setWordWrap(True)
        self.setCentralWidget(self.lstbox_view)

    def fileopen(self):
        caption = 'Open file'
        try:
            directory = self.dbdic['folder']  # added 6/16/25
        except:
            directory = str(Path.cwd())
        filter_mask = "BOMs (*_sw.xlsx *_sw.xls *_sl.xlsx *_sl.xls *_sw.csv *_sm.xlsx);;All files (*.*)"
        initialfilter = "Excel files (*_sw.xlsx *_.sw.xls *_sl.xlsx *_sl.xls *_sm.xlsx *_sm.xls)"
        filenames = QFileDialog.getOpenFileNames(self,
            caption, directory, filter_mask, initialfilter)[0]

        if filenames:
            self.folder = os.path.dirname(filenames[0])
            with open(self.configdb, 'r+') as file:
                x = file.read()
                self.dbdic = ast.literal_eval(x)
                self.dbdic['folder'] = self.folder
                file.seek(0)
                file.write(str(self.dbdic))
                file.truncate()
            self.folder = self.dbdic['folder']
            self.lstbox_view.addItems([str(Path(filename)) for filename in filenames])


    def openfolder(self):
        ''' Open the folder determined by variable "self.folder"'''
        err = False
        try:   # get BOM folder name from 1st item in drag/drop list
            self.folder = os.path.dirname(self.lstbox_view.item(0).text())
            with open(self.configdb, 'r+') as file:
                x = file.read()
                self.dbdic = ast.literal_eval(x)
                self.dbdic['folder'] = self.folder
                file.seek(0)
                file.write(str(self.dbdic))
                file.truncate()
            self.folder = self.dbdic['folder']
            os.system(cmdtxt(self.folder))
        except Exception:  # it an error occured, most likely and AttributeError
            #print("error2 at MainWindow/openfolder", e)
            #print("error2 at MainWindow/openfolder... possibly due to no data in drag&drop zone")
            err = True

        if err:
            try:
                with open(self.configdb, 'r') as file:
                    x = file.read()
                    self.dbdic = ast.literal_eval(x)
                self.folder = self.dbdic.get('folder', '')
                if self.folder:
                    os.system(cmdtxt(self.folder))
                else:
                    msg = ('Drag in some files first.  Thereafter\n'
                       'clicking the folder icon will open the\n'
                       'folder where BOMs are located.')
                    msgtitle = 'Folder location not set'
                    message(msg, msgtitle, msgtype='Information')
            except Exception as e:  # it an error occured, moset likely and AttributeError
                print("Error 103 at MainWindow/openfolder", e)

    def execute_bomcheck(self):
        global run_bomcheck
        self.run_bomcheck = True
        run_bomcheck = True   # run_bomcheck is set as a global variable on line 47
        self.execute()

    def execute_search_sm(self):
        global run_bomcheck
        self.run_bomcheck = False
        run_bomcheck = False
        self.execute()

    def execute(self):
        global printStrs, standardflow, files

        try:
            with open(self.configdb, 'r+') as file:
                x = file.read()
                self.dbdic = ast.literal_eval(x)
                self.dbdic['version_check_count'] = self.chkcount
                try:
                    self.folder = os.path.dirname(self.lstbox_view.item(0).text())
                    self.dbdic['folder'] = self.folder
                    file.seek(0)
                    file.write(str(self.dbdic))
                    file.truncate()
                except Exception as e:  # it an error occured, moset likely and AttributeError
                    print("error4 at MainWindow/execute", e)
        except Exception as e:  # it an error occured, moset likely and AttributeError
            print("error5 at MainWindow/execute", e)

        defaultfname = self.getdefaultfname()
        standardflow = True
        try:
            with open(self.configdb, 'r+') as file:
                x = file.read()
                self.dbdic = ast.literal_eval(x)
                self.dbdic['file2save2'] = defaultfname
                file.seek(0)
                file.write(str(self.dbdic))
                file.truncate()
        except Exception as e:  # it an error occured, moset likely and AttributeError
               msg = ("Error 102:\n\n"
               "Unable to read/write to config.txt in order to record the\n"
               "folder location the last folder containing BOMs.\n"
               "Otherwise the program will run as normal.\n\n" + str(e))
               msgtitle = 'Warning'
               message(msg, msgtitle, msgtype='Warning', showButtons=False)

        self.createdfile = ''
        files = []
        n = self.lstbox_view.count()
        for i in range(n):
            files.append(self.lstbox_view.item(i).text())

        if standardflow == True:
            dfs, df, dfsm, msg = bomcheck.bomcheck(files,
                               d = not self.drop_chkbox.isChecked(),
                               dbdic = self.dbdic,
                               run_bomcheck = self.run_bomcheck,             
                               filter_pn = self.pn_filter_input.text(),
                               similar = self.similarity_filter_input.text(),
                               filter_age = self.age_filter_input.text(),
                               show_demand = self.show_demand_chkbox.isChecked(),
                               on_hand = self.onhand_chkbox.isChecked()
                               )
            showTextFile(files)

        else:
            msg = []

        createdfile = 'Created file: unknown'
        for x in msg:
            if 'Created file:' in x and len(x) > 4:
                k = x.strip('\n')
                if '/' in k:
                    lst = k.split('/')
                    createdfile = 'Created file: .../' + '/'.join(lst[-3:])
                elif '\\' in k:
                    lst = k.split('\\')
                    createdfile = 'Created file: ...\\' + '\\'.join(lst[-3:])
            elif 'Created file:' in x:
                createdfile = x

        if len(msg) == 1 and  'Created file:' in msg[0]:
            del msg[0]

        self.statusbar.showMessage(createdfile, 1000000)
        if msg:
            msgtitle = 'bomcheck discrepancy warning'
            message(str(''.join(msg)), msgtitle)
        if 'DataFrame' in str(type(df)) and self.run_bomcheck:
            df_window = DFwindow(df, self)
            df_window.resize(1000, 800)
            df_window.setWindowTitle('BOMs Compared   (IQDU:  I=Item, Q=Quantity, D=Description, U=U/M)')
            df_window.show()
        if 'DataFrame' in str(type(dfs)) and self.run_bomcheck:
            BOMtype='sw'
            df_window = DFEditor(dfs, BOMtype, self)
            df_window.resize(750, 800)
            df_window.setWindowTitle('BOMs from CAD only')
            df_window.exec_()
            df_window.show()
        if 'DataFrame' in str(type(dfsm)) and not self.run_bomcheck:
            df_window = DFwindow(dfsm, self)
            df_window.resize(1200, 800)         
            df_window.setWindowTitle('Slow Moving parts comparison')
            df_window.show()

    def clear(self):
        self.lstbox_view.clear()

    def _help(self):
        bomcheck.view_help('bomcheck_help', dbdic=self.dbdic)
        # self.dbdic sent so that dictionnary key 'cfgpathname', containing location
        # of bomcheck.cfg file, is sent to function bomcheck.open_help_webpage

    def _helpslow(self):
        bomcheck.view_help('slowmoving_help', 'master', dbdic=self.dbdic)         

    def _helptroubleshoot(self):
        bomcheck.view_help('bomcheck_troubleshoot', dbdic=self.dbdic)

    def _bcgui_license(self):
        bomcheck.view_help('license')

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()

    def settings(self):
        dlg = SettingsDialog()
        dlg.exec_()

    def getdefaultfname(self):
        '''Look at the list of filenames that have been dropped.  From that
        list look for a name that ends with '_sl.xlsx', and extract a potential
        name to assign to the bomcheck output file.  E.g. from 093345_sl.xlsx,
        present to the user: 093345_bomcheck.  If no filename found ending
        with _sl.xlsx, or if more than one such file, then present the name:
        bomcheck.

        Returns
        -------
        defaultFname: str
            default filename for the output xlsx file that bomcheck creates.
        '''
        j = 0
        files = []
        found = None
        n = self.lstbox_view.count()
        for i in range(n):
            files.append(self.lstbox_view.item(i).text())
        for f in files:
            if '_sl.xls' in f.lower():
                found = os.path.splitext(os.path.basename(f))[0]  # name sripped of path and extension
                found = found[:-3]  # take the _sl characters off the end
                j += 1
        if found and j == 1:
            defaultFname = found + '_bomcheck'
        else:
            defaultFname = 'bomcheck'
        return defaultFname


def get_version():
    return __version__


class SettingsDialog(QDialog):
    ''' A dialog box asking the user what the settings he would like to make.
    '''
    def __init__(self):
        super(SettingsDialog, self).__init__()

        self.setWindowTitle('Settings')
        self.setFixedWidth(450)
        self.setFixedHeight(450)  # was 150

        layout = QVBoxLayout()

        self.configdb = ''
        try:
            self.configdb = get_configfn()
            with open(self.configdb, 'r') as file: # Use file to refer to the file object
                x = file.read()
            self.dbdic = ast.literal_eval(x)
        except Exception as e:  # it an error occured, moset likely and AttributeError
            print("error8 at SettingsDialog", e)

        self.mtltest_chkbox = QCheckBox("For pns check if 'Type'≠'Material'.")
        _bool = self.dbdic.get('mtltest', True)
        self.mtltest_chkbox.setChecked(_bool)
        layout.addWidget(self.mtltest_chkbox)

        hbox1 = QHBoxLayout()

        self.decplcs = QComboBox()
        self.decplcs.setFixedWidth(35)
        self.decplcs.addItems(['0', '1', '2', '3', '4', '5'])
        _decplcs = str(self.dbdic.get('accuracy', 2))
        self.decplcs.setCurrentText(_decplcs)
        hbox1.addWidget(self.decplcs)
        decplcs_label = QLabel()
        decplcs_label.setText('Round SW converted lengths to X decimal plcs.')
        hbox1.addWidget(decplcs_label)

        layout.addLayout(hbox1)

        hbox2 =  QHBoxLayout()

        self.swum = QComboBox()
        self.swum.addItems(['in', 'ft', 'yd', 'mm', 'cm', 'm'])
        _from_um = str(self.dbdic.get('from_um', 'in'))
        self.swum.setCurrentText(_from_um)
        hbox2.addWidget(self.swum)
        swum_label = QLabel()
        swum_label.setText('SolidWorks U/M' + 10*' ')
        hbox2.addWidget(swum_label)

        empty_label1 = QLabel()
        empty_label1.setText('   ')
        hbox2.addWidget(empty_label1)

        self.slum = QComboBox()
        self.slum.addItems(['in', 'ft', 'yd', 'mm', 'cm', 'm'])
        _to_um = str(self.dbdic.get('to_um', 'ft'))
        self.slum.setCurrentText(_to_um)
        hbox2.addWidget(self.slum)
        slum_label = QLabel()
        slum_label.setText('SyteLine U/M' + 20*' ')
        hbox2.addWidget(slum_label)

        layout.addLayout(hbox2)

        drop_label = QLabel()
        drop_label.setText('drop list (Don\'t show these pt. nos. during SM pts. comparison.  (Filter type is "glob".)')
        layout.addWidget(drop_label)

        self.drop_input = QTextEdit()
        self.drop_input.setPlaceholderText('Separate pt. nos. with commas.  Letters are case sensitive.')
        if 'udrop' in self.dbdic:
            self.drop_input.setPlainText(self.dbdic.get('udrop', ''))
        layout.addWidget(self.drop_input)

        exceptions_label = QLabel()
        exceptions_label.setText('exceptions list (exceptions to pt. nos. in the drop list):')
        layout.addWidget(exceptions_label)

        self.exceptions_input = QTextEdit()
        self.exceptions_input.setPlaceholderText('Separate pt. nos. with commas.  Letters are case sensitive.')
        if 'uexceptions' in self.dbdic:
            self.exceptions_input.setPlainText(self.dbdic.get('uexceptions', ''))
        layout.addWidget(self.exceptions_input)
        
# =============================================================================
#         prod_folder_label = QLabel()
#         prod_folder_label.setText('Production folder (Excel "short" list of sm parts stored here.):')
#         layout.addWidget(prod_folder_label)
#
#         self.prod_folder_input = QTextEdit()
#         self.prod_folder_input.setPlaceholderText('C:\\path_to_folder\\')
#         if 'prod_folder' in self.dbdic:
#             self.prod_folder_input.setPlainText(self.dbdic.get('prod_folder', ''))
#         layout.addWidget(self.prod_folder_input)
# =============================================================================
        
        proj_folder_label = QLabel()
        proj_folder_label.setText('Projects folders (Record of sm parts stored here.):')
        layout.addWidget(proj_folder_label)
        
        self.proj_folder_input = QTextEdit()
        self.proj_folder_input.setPlaceholderText('C:\\folderpath\\2025\\, C:\\folderpath\\2026\\')
        if 'proj_folder' in self.dbdic:
            self.proj_folder_input.setPlainText(self.dbdic.get('proj_folder', ''))
        layout.addWidget(self.proj_folder_input)
        
        
        
        eng_planner_label = QLabel()
        eng_planner_label.setText('Location of file "Engineering Planner.xlsm"')
        layout.addWidget(eng_planner_label)
        
        self.eng_planner_input = QTextEdit()
        self.eng_planner_input.setPlaceholderText('C:\\folderpath\\Engineering Planner.xlsm')
        if 'eng_planner' in self.dbdic:
            self.eng_planner_input.setPlainText(self.dbdic.get('eng_planner', ''))
        layout.addWidget(self.eng_planner_input)
        
        
        

        
        
        
        
        

        self.QBtnOK = QPushButton('text-align:center')
        self.QBtnOK.setText("OK")
        self.QBtnOK.setMaximumWidth(75)
        self.QBtnOK.clicked.connect(self._done)

        self.QBtnCancel = QPushButton('text-align:center')
        self.QBtnCancel.setText("Cancel")
        self.QBtnCancel.setMaximumWidth(75)
        self.QBtnCancel.clicked.connect(self.cancel)

        hbox = QHBoxLayout()
        hbox.addWidget(self.QBtnOK)
        hbox.addWidget(self.QBtnCancel)
        layout.addLayout(hbox)
        self.setLayout(layout)

    def _done(self):
        try:
            with open(self.configdb, "r+") as file:
                x = file.read()
                self.dbdic = ast.literal_eval(x)
                if self.mtltest_chkbox.isChecked():
                    self.dbdic['mtltest'] = True
                else:
                    self.dbdic['mtltest'] = False

                drp = self.drop_input.toPlainText().replace('"', '').replace("'", "").replace('\n', '')
                self.dbdic['udrop'] = drp
                excep = self.exceptions_input.toPlainText().replace('"', '').replace("'", "").replace('\n', '')
                self.dbdic['uexceptions'] = excep
                
# =============================================================================
#                 pd_folder = self.prod_folder_input.toPlainText()
#                 self.dbdic['prod_folder'] = pd_folder
# =============================================================================
                pj_folder = self.proj_folder_input.toPlainText().replace('"', '').replace("'", "").replace('\n', '')
                self.dbdic['proj_folder'] = pj_folder
                eng_planner = self.eng_planner_input.toPlainText()
                self.dbdic['eng_planner'] = eng_planner
                     
                self.dbdic['accuracy'] = int(self.decplcs.currentText())
                self.dbdic['from_um'] = self.swum.currentText()
                self.dbdic['to_um'] = self.slum.currentText()
                
                file.seek(0)
                file.write(str(self.dbdic))
                file.truncate()
        except Exception as e:  # it an error occured, most likely and AttributeError
            msg =  "error9 at SettingsDialog.  " + str(e)
            print(msg)
            message(msg, 'Error', msgtype='Warning', showButtons=False)
        self.close()

    def cancel(self):
        self.close()


class AboutDialog(QDialog):
    ''' Show company name, logo, program author, program creation date
    '''
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)
        if __version__ == bomcheck.get_version():
            msg = ('Description: A program to compare Bills of\n'
                     'Materials (i.e., BOMs)\n\n'
                     'Version: ' + __version__ + '\n\n'
                     'Author: Ken Carlton, 1/27/2021\n'
                     'kencarlton55@gmail.com')
        else:
            msg = ('Description: A program to compare Bills of\n'
                     'Materials (i.e., BOMs)\n\n'
                     'bomcheckgui version: ' + __version__ + '\n'
                     'bomcheck version: ' + bomcheck.get_version() + '\n'
                     '(bomcheck is incorporated within bomcheckgui)\n\n'
                     'Author: Ken Carlton, 1/27/2021\n'
                     'kencarlton55@gmail.com\n\n'
                     'bomcheckgui home:\n    https://github.com/kcarlton55/bomcheckgui \n'
                     'bomcheckgui source code:\n    https://github.com/kcarlton55/bomcheckgui/blob/' + __version__  + '/src/bomcheckgui.py \n\n'
                     'bomcheck home:\n    https://github.com/kcarlton55/bomcheck \n'
                     'bomcheck source code:\n   https://github.com/kcarlton55/bomcheck/blob/' + bomcheck.get_version() + '/src/bomcheck.py \n'
                     )
        self.setFixedHeight(360)
        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.setWindowTitle('About')
        layout = QVBoxLayout()
        qmsg = QLabel(msg)
        qmsg.setTextInteractionFlags(Qt.LinksAccessibleByMouse | Qt.TextSelectableByMouse)
        layout.addWidget(qmsg)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


class ListboxWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._placeholder_text = "Drag & Drop"

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)  # https://stackoverflow.com/questions/4008649/qlistwidget-and-multiple-selection

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        #global folder
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            links = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    links.append(str(url.toLocalFile()))
                else:
                    links.append(str(url.toString()))

            self.addItems(links)

        else:
            event.ignore()

    # https://stackoverflow.com/questions/60076333/how-to-set-the-placeholder-text-in-the-center-when-the-qlistwidget-is-empty
    @property
    def placeholder_text(self):
        return self._placeholder_text

    @placeholder_text.setter
    def placeholder_text(self, text):
        self._placeholder_text = text
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.count() == 0:
            painter = QPainter(self.viewport())
            painter.setPen(QColor(192, 192, 192))
            painter.setFont(QFont('Decorative', 20, QFont.Bold))
            painter.save()
            fm = self.fontMetrics()
            elided_text = fm.elidedText(
                self.placeholder_text, Qt.ElideRight, self.viewport().width()
            )
            painter.drawText(self.viewport().rect(), Qt.AlignCenter, elided_text)
            painter.restore()

    def keyPressEvent(self, ev):
        i = self.currentItem()
        if ev.key() in (Qt.Key_Delete, Qt.Key_Backspace) and i != None:
            self.delete_selected()
            # ev.accept()  # not needed per https://doc.qt.io/qt-5/qkeyevent.html
            return
        elif ev.modifiers() & Qt.ControlModifier:
            if ev.key() == Qt.Key_V:   #https://doc.qt.io/qtforpython-5/PySide2/QtGui/QClipboard.html
                clipboard = QGuiApplication.clipboard()
                mimeData = clipboard.mimeData()
                if mimeData.hasText():
                    pathnames = mimeData.text().split('\n') # list of pathnames
                    for pathname in pathnames:
                        pathname = pathname.strip('"') # remove colons that MS puts at ends of pathname
                        if pathname[:5].lower() == 'file:':
                            pathname = pathname[8:]  # if pathname is like file:\\\C:\mydirectory\myfile.xlsx
                        self.addItem(QListWidgetItem(pathname))
        return QListWidget.keyPressEvent(self, ev)

    def delete_selected(self):
        for item in self.selectedItems():
            self.takeItem(self.row(item))


def cmdtxt(foldr):
    ''' Create a dirpath name based on a URI type scheme.  Put in front of
    it the command that will be capable of opening it in file manager program.

    e.g. in Windows:
        exlorer file:///C:/SW_Vault/CAD%20Documents/PRODUCTION%20SYSTEMS

    e.g. on my Ubuntu Linux system:
        thunar file:///home/ken/tmp/bom%20files

    Where %20 is equivalent to a space character.
    referece: https://en.wikipedia.org/wiki/File_URI_scheme
    '''
    if sys.platform[:3] == 'win':
        foldr = foldr.replace(' ', '%20')
        command = 'explorer file:///' + foldr
    elif sys.platform[:3] == 'lin':
        homedir = os.path.expanduser('~')
        foldr = os.path.join(homedir, foldr)
        foldr = foldr.replace(' ', '%20')
        command = 'thunar file:///' + foldr  # thunar is the name of a file manager
    return command


def message(msg, msgtitle, msgtype='Warning', showButtons=False):
    '''
    UI message to show to the user

    Parameters
    ----------
    msg: str
        Message presented to the user.
    msgtitle: str
        Title of the message.
    msgtype: str, optional
        Type of message.  Currenly only valid input is 'Warning'.
        The default is 'Warning'.
    showButtons: bool, optional
        If True, show OK and Cancel buttons. The default is False.

    Returns
    -------
    retval: QMessageBox.StandardButton
        "OK" or "Cancel" is returned
    '''
    msgbox = QMessageBox()
    if msgtype == 'Warning':
        msgbox.setIcon(QMessageBox.Warning)
    elif msgtype == 'Information':
        msgbox.setIcon(QMessageBox.Information)
    msgbox.setWindowTitle(msgtitle)
    msgbox.setText(msg)
    if showButtons:
        msgbox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    retval = msgbox.exec_()
    return retval


def get_configfn():
    '''1. Get the pathname to store user defined settings.  The file will be
    named config.txt.  The pathname will be vary depending on who's logged in.
    It will look like: C:\\Users\\Ken\\AppData\\Local\\bomcheck\\config.txt.
    2.  If a Linux system is used, the pathname will look like:
    /home/Ken/.bomcheck/config.txt
    3.  If directories in the path do not already exists, crete them.
    4.  If the config.txt file doesn't already exist, create it and put in it
    some inital data: {'udrop':'3*-025'}
    '''
    if sys.platform[:3] == 'win':  # if a Window operating system being used.
        datadir = os.getenv('LOCALAPPDATA')
        path = os.path.join(datadir, 'bomcheck')
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
        configdb = os.path.join(datadir, 'bomcheck', 'config.txt')

    elif sys.platform[:3] == 'lin':  # if a Linux operating system being used.
        homedir = os.path.expanduser('~')
        path = os.path.join(homedir, '.bomcheck')
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
        configdb = os.path.join(homedir, '.bomcheck', 'config.txt')

    else:
        printStr = ('At method "get_configfn", a suitable path was not found to\n'
                    'create file config.txt.  Notify the programmer of this error.')
        print(printStr)
        return ""

    _bool = os.path.exists(configdb)
    if not _bool or (_bool and os.path.getsize(configdb) == 0):
        with open(configdb, 'w') as file:
            file.write("{'udrop':'3*-025'}")

    return configdb


class DFwindow(QDialog):
    ''' Displays a Pandas DataFrame in a GUI window and shows three buttons
        below it: Print, Print Preview, and Save as .xlsx.
    '''
    
    def __init__(self, df, parent=None):
        super(DFwindow, self).__init__(parent)
        
        self.df_xlsx = df.copy(deep=True)  # make a copy.  This will be used to save to an txt file      
        self.df = merge_index(df)  # use for disply to user and for printing
        self.columnLabels = self.df.columns
        model = DFmodel(self.df, self)
        
        self.view = QTableView(self)
        self.view.setModel(model)
        self.view.setShowGrid(False)
        self.view.setAlternatingRowColors(True)
        self.view.resizeColumnsToContents()
        header = self.view.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft)

        self.setWindowFlags(Qt.Window
                            | Qt.WindowSystemMenuHint
                            | Qt.WindowMinimizeButtonHint
                            | Qt.WindowMaximizeButtonHint
                            | Qt.WindowCloseButtonHint)

        self.buttonPreview = QPushButton('&Print', self)
        self.buttonPreview.setShortcut('Ctrl+P')
        self.buttonPreview.clicked.connect(self.handlePreview)
   
        self.save_as_xlsx = QPushButton('&Export to Excel', self)
        self.save_as_xlsx.setShortcut('Ctrl+S')
        self.save_as_xlsx.clicked.connect(self.save_xlsx) 
   
        if not run_bomcheck:
            self.save_as_xlsx_short = QPushButton('Export shortened\nlist to Excel', self)
            self.save_as_xlsx_short.clicked.connect(self.save_xlsx_short)
            i = 1
        else:
            i = 0
            
        buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        buttonBox.button(QDialogButtonBox.Close).clicked.connect(self.reject)

        layout = QGridLayout(self)
        layout.addWidget(self.view, 0, 0, 1, 4+i)
        #layout.addWidget(self.buttonPrint, 1, 0)
        layout.addWidget(self.buttonPreview, 1, 1)
        layout.addWidget(self.save_as_xlsx, 1, 2)
        if not run_bomcheck:
            layout.addWidget(self.save_as_xlsx_short, 1, 3)
        layout.addWidget(buttonBox, 1, 3+i)
        
    def handlePreview(self):
        printer = QtPrintSupport.QPrinter()
        printer.setPaperSize(printer.Letter)
        printer.setOrientation(printer.Landscape)
        dialog = QtPrintSupport.QPrintPreviewDialog(printer, self)
        dialog.paintRequested.connect(self.handlePaintRequest)
        dialog.exec_()

    def handlePaintRequest(self, printer):
        document = QTextDocument()
        cursor = QTextCursor(document)
        font = QFont()
        font.setPointSize(7)
        document.setDefaultFont(font)
        model = self.view.model()
        tableFormat = QTextTableFormat() # https://stackoverflow.com/questions/65744428/qtexttable-insert-a-line-in-a-cell
        tableFormat.setBorder(0)
        tableFormat.setCellPadding(2)

        cursor.insertTable(model.rowCount() + 1,  # the + 1 accounts for col labels that will be added
                           model.columnCount(), tableFormat)

        lst = []
        for row in range(model.rowCount()):
            for column in range(model.columnCount()):
                lst.append(model.item(row, column))
        for c in reversed(self.columnLabels):
            lst.insert(0, c)


        for l in lst:
            cursor.insertText(l)
            cursor.movePosition(QTextCursor.NextCell)

        printer.setPaperSize(QtPrintSupport.QPrinter.Letter)
        document.print_(printer)
      
    def save_xlsx (self): 
        if 'alt\nqty\nused' in self.df_xlsx.columns:
            model = self.view.model()
            altqty_column_num = list(self.df_xlsx.columns).index('alt\nqty\nused') + len(self.df_xlsx.index[0])
            altqtys = []
            for i in range(self.df_xlsx.shape[0]):
                altqtys.append(model.item(i, altqty_column_num))
            self.df_xlsx['alt\nqty\nused'] = altqtys
        filter = "Excel (*.xlsx)" if run_bomcheck else "Excel (*_alts.xlsx)"
        
        try:
            if run_bomcheck:
                default_name = get_filename('bomcheck', files)
            else:
                default_name = get_filename('projects', files)
            filename, _ = QFileDialog.getSaveFileName(self, 'Save File', default_name, filter=filter)
            export2xlsx(filename, self.df_xlsx, run_bomcheck)
                        
        except Exception as e:
            print('Error within bomcheckgui at function "save_xlsx".')
            print(e)
            msg = str(e)
            msgtitle = 'Error while trying to save file'
            message(msg, msgtitle)
            
        
    def save_xlsx_short (self):  
        model = self.view.model()
        altqty_column_num = list(self.df_xlsx.columns).index('alt\nqty\nused') + len(self.df_xlsx.index[0])
        altqtys = []
        for i in range(self.df_xlsx.shape[0]):
            altqtys.append(model.item(i, altqty_column_num))
        self.df_xlsx['alt\nqty\nused'] = altqtys
        filter = "Excel (*.xlsx)" if run_bomcheck else "Excel (*_alts.xlsx)"
        df_short =  self.df_xlsx[self.df_xlsx['alt\nqty\nused'].str.strip() != '']

        try:
            default_name = get_filename('production', files)
            if df_short.shape[0] > 0:
                filename, _ = QFileDialog.getSaveFileName(self, 'Save File', default_name, filter=filter)
                export2xlsx(filename, df_short, run_bomcheck) 
            else:
                print('Cannot export.  Values in "alt qty used" column required.')
                msg = 'Cannot export.  Values in "alt qty used" column required.'
                msgtitle = 'Information'
                message(msg, msgtitle, msgtype='Information', showButtons=False)   
        except Exception as e:
            print('Error within bomcheckgui at function "save_xlsx".')
            print(e)
            msg = str(e)
            msgtitle = 'Error while trying to save file'
            message(msg, msgtitle)


class DFmodel(QAbstractTableModel):
    ''' Enables a Pandas DataFrame to be able to be shown in a GUI window.
    '''
    def __init__(self, data, parent=None):
        super(DFmodel, self).__init__(parent)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def item(self, row, col):
        return str(self._data.iat[row, col]) 

    # methods below added 11/7/2025.  Reference: https://www.pythonguis.com/faq/qtableview-cell-edit/
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def flags(self, index): 
        if not index.isValid():
            return Qt.ItemIsEnabled
            
        return super().flags(index) | Qt.ItemIsEditable  # add editable flag. 
    
    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section] + 2)

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            # Set the value into the frame.
            self._data.iloc[index.row(), index.column()] = value
            return True

        return False    
    

def merge_index(df):
    ''' This function will, first, take a pandas dataframe, df, whose index
    values are the assy and item no. colunns, and will merge those into the main
    body of the df object.  The new index will be the standard type of dataframe
    index, 0, 1, 2, 3, and so forth.  Panda's "reset_index" function is used
    to do this,  The resulting dataframe will look like this:

       assy                item
    0  0300-2022-384       6602-0400-000
    1  0300-2022-384       6602-0600-000
    2  2728-2020-908       6600-0025-001
    3  2730-2021-131       6600-0025-001
    4  2730-2021-131       6652-0025-005
    5  2730-2021-131       7215-0200-001
    6  6890-ACV0098372-01  2915-0050-000

    The column 0, 1, 2, 3,... is the index column.  Then, second, this function
    will remove duplicate assy nos. so that the data frame looks like this:

       assy                item
    0  0300-2022-384       6602-0400-000
    1                      6602-0600-000
    2  2728-2020-908       6600-0025-001
    3  2730-2021-131       6600-0025-001
    4                      6652-0025-005
    5                      7215-0200-001
    6  6890-ACV0098372-01  2915-0050-000
    '''
     
    if df.index.values.tolist()[0] != 0:
        df.reset_index(inplace=True)
    
    # Eliminate duplicate strings in first column.  If a sm parts dataframe,
    # eliminate corresponding values in the 'description' and 'cost' columns.
    s = df.iloc[:, 0].copy()
    is_duplicated = df.iloc[:, 0].duplicated()
    df.iloc[:, 0] = df.iloc[:, 0] * ~is_duplicated
    filter = s == df.iloc[:, 0]
    if 'DESCRIPTION' in df.columns:
        df['DESCRIPTION'] = df['DESCRIPTION'] * filter
    if 'COST' in df.columns:
        df['COST'] = df['COST'] * filter
    
    return df


class FloatDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super().__init__()

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(QDoubleValidator())
        return editor


class TableWidget(QTableWidget):
    def __init__(self, df, BOMtype):
        super().__init__()
        self.BOMtype = BOMtype
        self.df = df
              
        #self.setStyleSheet('font-size: 35px;')
        #ref: https://www.w3.org/TR/SVG11/types.html#ColorKeywords
        if BOMtype=='sw':
            self.setStyleSheet('background-color: peachpuff')
            self.setStyleSheet('alternate-background-color: mistyrose;')

        nRows, nColumns = self.df.shape
        self.setColumnCount(nColumns)
        self.setRowCount(nRows)

        self.setHorizontalHeaderLabels(df.columns)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        header.setDefaultAlignment(Qt.AlignLeft)

        #header.setSectionResizeMode(QHeaderView.ResizeToContents)
        vheader = self.verticalHeader()
        vheader.setVisible(False)

        if self.df.columns[4]=='Q':
            self.setItemDelegateForColumn(4, FloatDelegate())

        #data insertion
        assy = []
        assy_j0 = []
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                txt = str(self.df.iloc[i, j])
                if j == 0 and txt in assy_j0:
                    self.setItem(i, j, QTableWidgetItem('')) # In column 0, if assy no. already in that column, put '' there instead.
                    self.df.iloc[i, j] = ''
                elif j == 0:
                    assy_j0.append(txt)
                    assy.append(txt)
                    self.setItem(i, j, QTableWidgetItem(txt))
                else:
                    assy.append(txt)
                    self.setItem(i, j, QTableWidgetItem(txt))

        self.cellChanged[int, int].connect(self.updateDF)

        self.clip = QApplication.clipboard()

    def updateDF(self, row, column):
        text = self.item(row, column).text().strip()
        if self.df.columns[column]=='Op':
            for i in range(row, self.rowCount()):  # make op no. same for all pns for a particular assy no.
                self.item(i, column).setText(text)
                self.df.iloc[row, column] = text
                try:
                    textAtColumn0 = self.item(i+1, 0).text()  # In column 0, textAtColunn0 = '' or an assy pn.
                    if textAtColumn0:
                        break        # stop remplacing op nos. if a different assy no. listed, i.e. not ''
                except:
                    pass  #tried to exceed the no. of rows in a table              
        if self.df.columns[column]=='WC':
            for i in range(row, self.rowCount()):  # make op no. same for all pns for a particular assy no.
                self.item(i, column).setText(text)
                self.df.iloc[row, column] = text
                try:
                    textAtColumn0 = self.item(i+1, 0).text()  # In column 0, textAtColunn0 = '' or an assy pn.
                    if textAtColumn0:
                        break        # stop remplacing op nos. if a different assy no. listed, i.e. not ''
                except:
                    pass  #tried to exceed the no. of rows in a table
        else:
            self.df.iloc[row, column] = text

    def keyPressEvent(self, event):
        if (event.modifiers() & Qt.ControlModifier):
            selected = self.selectedRanges()
            topRow = selected[0].topRow()
            bottomRow = selected[0].bottomRow()
            leftColumn = selected[0].leftColumn()
            rightColumn = selected[0].rightColumn()
            if event.key()==Qt.Key_C and self.df.columns[leftColumn]=='Op' and rightColumn>4:
                rightColumn = 4

            if event.key() == Qt.Key_C:
                s = ''
                for r in range(topRow, bottomRow + 1):
                    for c in range(leftColumn, rightColumn +1):
                        try:
                            s += str(self.item(r, c).text()) + '\t'
                        except AttributeError:
                            s += '\t'
                    s = s[:-1] + '\n' #eliminate last '\t'
                self.clip.setText(s)


class DFEditor(QDialog):
    def __init__(self, df, BOMtype, parent=None):
        super().__init__(parent)
        self.df = df
        self.df_xlsx = df.copy(deep=True)  # make a copy.  This will be used to save to an txt file   
        mainLayout = QVBoxLayout()
        df.reset_index(inplace=True)
        self.table = TableWidget(df, BOMtype)
        mainLayout.addWidget(self.table)

        button_export = QPushButton('Export to .xlsx')
        #button_export.setStyleSheet('font-size: 30px')
        button_export.clicked.connect(self.save_xlsx)
        mainLayout.addWidget(button_export)

        self.setLayout(mainLayout)

        self.setWindowFlags(Qt.Window
                            | Qt.WindowSystemMenuHint
                            | Qt.WindowMinimizeButtonHint
                            | Qt.WindowMaximizeButtonHint
                            | Qt.WindowCloseButtonHint)
       
    def save_xlsx (self): 
        filter = "Excel (*.xlsx)" 
        filename, _ = QFileDialog.getSaveFileName(self, 'Save File', filter=filter)
        export2xlsx(filename, self.df_xlsx, True)
                
        
def showTextFile(filelst):
    '''
    This function under development

    Parameters
    ----------
    filelst : list
        list of filenames.  Each value is a string.

    Returns
    -------
    None.

    '''
    for x in [f for f in filelst if f[-4:].lower() == '.txt']:
        print(x)


def check_latest_version(count, intervals=[10,11]):
    '''When bomcheckgui is started, check and see if a later version of
    bomcheckgui and/or bomcheck exist, but don't check every time.  Instead
    check at various intervals.

    >>> NOTE: FOR COUNTS TO BE RECORDED PROPERLY, BOMCHECKGUI NEEDS TO BE
    OPENED AND RAN, THEN CLOSED.  NOT JUST OPENED AND CLOSED.

    Parameters
    ----------
    count : int
        Keep count of how many times bomcheckgui has been opened, i.e., the
        variable "count" is incremented.  This incremented value is returned
        to the function that called check_latest_version().  That function is
        responsible for storing the count value in a text file.  When
        bomcheckgui is restared, the restored value of count from the text is
        given as the first argument of check_latest_verson().

    intervals : list
        A list of integers.  E.g. something like [0, 1, 10].  Using this list,
        bomcheckgui will check for a later version if the value of count
        is found in the list.  When count exceeds the max int value in the
        list, count is reset to zero.  Thereafter count will start looking in
        the list afresh.

    Returns
    -------
    out : int
        The incremented value of count is returned.

    '''

    if count in intervals and latest_version_msg():  # show msg if later version
        msg = latest_version_msg()
        count += 1
        msgtitle = 'New version available'
        message(msg, msgtitle, msgtype='Information', showButtons=False)
        return count
    elif count < max(intervals):
        count += 1
        return count
    else:
        count = 0
        return count


def latest_version_msg():
    ''' Look on the pypi.org website and check if there is a later version of
    bomcheck.py available.  If so, return a string that provides instructions
    on how the user can upgrade to the latest version.

    Returns
    -------
    out : str
       If no new software version is available, return ''.  Else return a
       string with instructions about how to upgrade.
    '''
    try:
        package = 'bomcheck'
        response = requests.get(f'https://pypi.org/pypi/{package}/json', timeout=5)
        latest_version = response.json()['info']['version']
        current_version = bomcheck.get_version()           # e.g. like "1.9.6"
        lv = [int(i) for i in latest_version.split('.')]   # create a list of integers
        cv = [int(i) for i in current_version.split('.')]  # e.g. like [1, 9, 6]

        package = 'bomcheckgui'
        response = requests.get(f'https://pypi.org/pypi/{package}/json', timeout=5)
        latest_version_gui = response.json()['info']['version']
        current_version_gui = get_version()
        lv_gui = [int(i) for i in latest_version_gui.split('.')]
        cv_gui = [int(i) for i in current_version_gui.split('.')]

        printStr = []
        if (lv > cv) and (lv_gui > cv_gui):
            printStr.append('Installed: bomcheck ' + current_version + '\n'
                            'New version available: ' + latest_version + '\n')
            printStr.append('Installed: bomcheckgui ' + current_version_gui + '\n'
                            'New version available: ' + latest_version_gui + '\n\n')
            printStr.append("To install new versions, do:\n\n"
                            "    py getbc.py --upgrade\n\n"
                            "or activate bomcheck's virtual\n"
                            "environment and then do:\n\n"
                            "    py -m pip install --upgrade bomcheck\n"
                            "    py -m pip install --upgrade bomcheckgui\n\n\n")
            return ''.join(printStr)
        elif lv > cv:
            printStr.append('Installed: bomcheck ' + current_version + '\n'
                             'New version available: ' + latest_version + '\n\n')
            printStr.append("To install new version, do:\n\n"
                            "    py getbc.py --upgrade\n\n"
                            "or activate bomcheck's virtual\n"
                            "environment and then do:\n\n"
                            "    py -m pip install --upgrade bomcheck\n\n\n")
            return ''.join(printStr)
        elif lv_gui > cv_gui:
            printStr.append('Installed: bomcheckgui ' + current_version_gui + '\n'
                            'New version available: ' + latest_version_gui + '\n\n')
            printStr.append("To install new version, do:\n\n"
                            "    py getbc.py --upgrade\n\n"
                            "or activate bomcheckgui's virtual\n"
                            "environment and then do:\n\n"
                            "    py -m pip install --upgrade bomcheckgui\n\n\n")
            return ''.join(printStr)
        return ''
    except requests.ConnectionError:  # No internet connection
        pass


def get_filename(kind, files):
    # from dbdic looking to get values of keys 'prod_folder', 'proj_folder',
    # and 'eng_planner'.  The first values is s folder, the second a list of
    # folders (each separated by a comma), and the thirt the path name of the
    # file "Engineering Planner.xlsx".    
    try:
        configdb = get_configfn()
        with open(configdb, 'r') as file:
            x = file.read()
        dbdic = ast.literal_eval(x)
    except Exception as e:
        msg = ("Error 901:\n\n"
               "Unable to open config.txt file which allows the program\n"
               "to remember user settings.  Default settings will be used.\n"
               "Otherwise the program will run as normal.\n\n" + str(e))
        print(msg)
        #msgtitle = 'Warning'
        #message(msg, msgtitle, msgtype='Warning', showButtons=False)
        dbdic = {'udrop': '3*-025', 'uexceptions': '', 
                      'folder': '', 'file2save2': 'bomcheck',
                      'prod_folder': None, 'proj_folder': None,
                      'eng_planner': None}
        configdb = ''
    production_folder = dbdic.get('prod_folder', None)
    system_folders =  dbdic.get('proj_folder', None)
    eng_planner =  dbdic.get('eng_planner', None)

    # create two lists, one for sw files, the other sl.  Sort the lists pushing
    # to the back of the lists pns with the fifth characater being a -,
    # e.g. 3818-UNV2-000, and 6890-064545-2.  These are subassemblies and not
    # system part numbers.
    sw_files = []
    sl_files = []       
    for f in files:
        _ , fn = os.path.split(f)  
        if '_sw' in fn.lower():
            fn = fn.split('_')[0]
            if fn[4] == '-':
                sw_files.append(fn)
            else:
                sw_files.insert(0, fn)
        elif '_sl' in fn.lower(): 
            fn = fn.split('_')[0]
            if fn[4] == '-':
                sl_files.append(fn)
            else:
                sl_files.insert(0, fn)   
    # Sort again.  System part nos. most often begin with AC, DV, QS, etc.
    # Move these to the start of the lists.            
    sw_files2 = []
    sl_files2 = []
    for sw in sw_files:
        if (sw.startswith('AC') or sw.startswith('DV') or sw.startswith('QS')
                or sw.startswith('QC') or sw.startswith('SV') or sw.startswith('NR')
                or sw.startswith('NY') or sw.startswith('ED')):
            sw_files2.insert(0, sw)
        else:
            sw_files2.append(sw)
    for sl in sl_files:
        if (sl.startswith('AC') or sw.startswith('DV') or sw.startswith('QS')
                or sw.startswith('QC') or sw.startswith('SV') or sw.startswith('NR')
                or sw.startswith('NY') or sw.startswith('ED')):
            sl_files2.insert(0, sl)
        else:
            sl_files2.append(sl)
            
    # sl more often than not will contain a system pn.  It's the first choice.
    if sl_files2:
        systemNo = sl_files2[0]
    elif sw_files2:
        systemNo = sw_files2[0]
        
    # import an Excel file that allow system_pn to CO_number pairing        
    df = pd.read_excel(eng_planner, na_values=[' '], skiprows=3, 
                       usecols=['Item ', 'CO Number'])   # 'Item ', not 'Item', is the eng_planner Excel file
    df.columns = df.columns.str.strip()                  # Change 'Item ' to 'Item'
    df = df.dropna(how='any')
    CO_dict = dict(zip(df['Item'], df['CO Number']))
    CO = CO_dict.get(systemNo, 'CO00XXXXXX')
    
    def subfunction(system_folders = system_folders):   # this function called when "kind" = projects or bomcheck
        # Create a dic that looks like: 
        # {'C:\\...\\Projects folder\\2025\\':
        #     ['CO00118889 Edwards - ATLAS COPCO Rebrand', ...], 
        # 'C:\\...\\Projects folder\\2026':
        #     ['CO00120400 Edwards - ATLAS COPCO Rebrand', ...]}             
        system_folders = system_folders.replace('\n', '').split(',')  # creates a list object
        system_folders = [s.strip() for s in system_folders]  # remove any leading or trailing spaces from items in the list
        system_folders_dic = {}
        for s in system_folders:
            folders = os.listdir(s)   # obtain a list of dirs in each system folder, e.g. in 2025 folder, 2026, etc.
            system_folders_dic[s] = folders
        flag = False
        for key in system_folders_dic:
            for f in system_folders_dic[key]:
                if CO in f:
                    folder = os.path.join(key, f, 'Engineering')          
                    flag = True
                    break
        if flag:
            if not os.path.exists(folder):
                os.mkdir(folder)   # Make and "Engineering" folder if it does not already exist.
        else:
            folder = key
        return folder, systemNo + '_' + CO    
    
    if kind == 'production':
        # filename = os.path.join(production_folder, systemNo + '_' + CO + '_' + str(date.today())) 
        folder, pn_CO = subfunction()      
        filename = os.path.join(folder, pn_CO + '_shortlist_' + str(date.today()))
    elif kind == 'projects':
        folder, pn_CO = subfunction()      
        filename = os.path.join(folder, pn_CO + '_longlist_' + str(date.today()))
    elif kind == 'bomcheck':
        folder, pn_CO = subfunction()      
        filename = os.path.join(folder, pn_CO + '_bomcheck_' + str(date.today()) )
    
    return filename




app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec_())
