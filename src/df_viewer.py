#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 23 00:04:01 2022

@author: ken

Display a Pandas DataFrame within a GUI

"""

import os.path
from bomcheck import export2excel
from PyQt5 import QtPrintSupport
from PyQt5.QtCore import (QAbstractTableModel, Qt)
from PyQt5.QtGui import (QFont, QTextCursor, QTextDocument, QTextTableFormat)
from PyQt5.QtWidgets import (QDialog, QFileDialog, QGridLayout, QPushButton,
                             QTableView, QDialogButtonBox)

class DFwindow(QDialog):
    ''' Displays a Pandas DataFrame in a GUI window and shows three buttons
        below it: Print, Print Preview, and Save as .xlsx.
    '''
    def __init__(self, df, parent=None):
        super(DFwindow, self).__init__(parent)

        self.df_xlsx = df.copy()  # make a copy.  This will be used to save to an Excel file
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

        self.buttonPrint = QPushButton('&Print', self)
        self.buttonPrint.setShortcut('Ctrl+P')
        self.buttonPrint.clicked.connect(self.handlePrint)

        self.buttonPreview = QPushButton('Print Preview', self)
        self.buttonPreview.clicked.connect(self.handlePreview)

        self.save_as_xlsx = QPushButton('&Save as .xlsx', self)
        self.save_as_xlsx.setShortcut('Ctrl+S')
        self.save_as_xlsx.clicked.connect(self.save_xlsx)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.reject)

        layout = QGridLayout(self)
        layout.addWidget(self.view, 0, 0, 1, 4)
        layout.addWidget(self.buttonPrint, 1, 0)
        layout.addWidget(self.buttonPreview, 1, 1)
        layout.addWidget(self.save_as_xlsx, 1, 2)
        layout.addWidget(buttonBox, 1, 3)

    def handlePrint(self):
        printer = QtPrintSupport.QPrinter()
        printer.setPaperSize(printer.Letter)
        printer.setOrientation(printer.Landscape)
        dialog = QtPrintSupport.QPrintDialog(printer, self)
        if dialog.exec_() == QDialog.Accepted:
            self.handlePaintRequest(dialog.printer())

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

    def save_xlsx(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save File', filter="xlsx (*.xlsx)",
                                    options=QFileDialog.DontConfirmOverwrite)
        dirname, f = os.path.split(filename)
        f, e = os.path.splitext(f)
        results2export = [('BOM Check', self.df_xlsx)]
        export2excel(dirname, f, results2export, 'unknown')


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

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

    def item(self, row, col):
        return str(self._data.iat[row, col])


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
    is_duplicated = df.iloc[:, 0].duplicated()  # False, True, False, False, True, True, False
    df.iloc[:, 0] = df.iloc[:, 0] * ~is_duplicated  # where df.iloc[:, 0] is 0300-2022-384, 0300-2022-384, 2728-2020-908, ...
    return df



#if __name__ == '__main__':
#    app = QApplication(sys.argv)
#    window = DFwindow(df)
#    window.resize(1175, 800)
#    window.show()
#    sys.exit(app.exec_())