'''
Created on 2013-2-9

@author: jifeng
'''

#!/usr/bin/python -d
import os
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import  QCompleter, QStringListModel
from gui import Ui_Form
from dialogUi import Ui_Dialog
from dialogUi2 import Ui_Dialog2
import todo
import Expar
import Expar_database
import elixir
import time
import SeqDep
import advance
import configure_finger
# lineEdit:input file; lineEdit_2:fragment_length;lineEdit_3:;lineEdit_4: maximal mismatch;lineEdit_5:;
# lineEdit_6, lineEdit_8, lineEdit_9, lineEdit_10, lineEdit_11,lineEdit_12
# lineEidt_7:maximal gap between PT and PX
# lineEdit_14: PT alignment longer than, lineEdit_16: PX alignment longer than
class MyForm(QtGui.QMainWindow,QtCore.QThread):
    tick = QtCore.pyqtSignal(int, name="changed") #New style signal
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self)
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        QtCore.QObject.connect(self.ui.pushButton, QtCore.SIGNAL("clicked()"), self.filebrower) #for input file
        QtCore.QObject.connect(self.ui.pushButton_2, QtCore.SIGNAL("clicked()"), self.submit) #submit
        QtCore.QObject.connect(self.ui.pushButton_3, QtCore.SIGNAL("clicked()"), self.reset) #reset
        QtCore.QObject.connect(self.ui.pushButton_4, QtCore.SIGNAL("clicked()"), self.add_taxid1) #add taxid to include
        QtCore.QObject.connect(self.ui.pushButton_5, QtCore.SIGNAL("clicked()"), self.add_taxid2) #add taxid to exclude
        QtCore.QObject.connect(self.ui.pushButton_6, QtCore.SIGNAL("clicked()"), self.advance) #add taxid to exclude
        self.ui.progressBar.hide()
        self.ui.progressBar.setProperty("value", 0)
        self.ui.lineEdit_add3 = QtGui.QLineEdit(self.ui.groupBox_2)
        self.ui.lineEdit_add3.setGeometry(QtCore.QRect(70, 20, 281, 21))
        self.ui.lineEdit_add3.setObjectName("lineEdit_3")
        self.ui.lineEdit_add3.setText(QtGui.QApplication.translate("Form", "", None, QtGui.QApplication.UnicodeUTF8))
        completer = QCompleter()
        self.ui.lineEdit_add3.setCompleter(completer)
        model = QStringListModel()
        completer.setModel(model)
        completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        Expar.get_data(model)
        self.ui.lineEdit_add2 = QtGui.QLineEdit(self.ui.groupBox_4)
        self.ui.lineEdit_add2.setGeometry(QtCore.QRect(70, 19, 281, 21))
        self.ui.lineEdit_add2.setObjectName("lineEdit_2")
        self.ui.lineEdit_add2.setText(QtGui.QApplication.translate("Form", "", None, QtGui.QApplication.UnicodeUTF8))
        completer = QCompleter()
        self.ui.lineEdit_add2.setCompleter(completer)
        model = QStringListModel()
        completer.setModel(model)
        completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        Expar.get_data(model)
        self.dbdir=os.path.join(os.path.expanduser("~"),".pyqtodo")
        self.dbfile=os.path.join(self.dbdir,str(int(time.time()))+"tasks.sqlite")
        if not os.path.isdir(self.dbdir):
            os.mkdir(self.dbdir)
            # Set up the Elixir internal thingamajigs
        elixir.metadata.bind = "sqlite:///%s"%self.dbfile
        elixir.setup_all()
        if not os.path.exists(self.dbfile):
            elixir.create_all()
        global saveData
        if elixir.__version__ < "0.6":
            saveData=elixir.session.flush
        else:
            saveData=elixir.session.commit
        saveData()
    def filebrower(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', './')
        self.ui.lineEdit.setText(fname)
    def add_taxid1(self):
            mid=" OR "
            if  self.ui.lineEdit_5.text()=="":
                self.ui.lineEdit_5.setText(self.ui.lineEdit_add3.text())
            else:
                self.ui.lineEdit_5.setText(self.ui.lineEdit_add3.text()+mid+self.ui.lineEdit_5.text())
            self.ui.lineEdit_add3.setText("")
    def add_taxid2(self):
            mid=" OR "
            if  self.ui.lineEdit_15.text()=="":
                self.ui.lineEdit_15.setText(self.ui.lineEdit_add2.text())
            else:
                self.ui.lineEdit_15.setText(self.ui.lineEdit_add2.text()+mid+self.ui.lineEdit_15.text())
            self.ui.lineEdit_add2.setText("")
    def submit(self):
        input_filename=Expar.input_content(self.ui.textEdit.toPlainText(),self.ui.lineEdit.text())
        if input_filename!='':
            Expar.main_page(input_filename,self.ui.lineEdit_5.text(),self.ui.lineEdit_15.text(),self.ui.checkBox.isChecked(),self.ui.checkBox_2.isChecked(),self.ui.checkBox_3.isChecked(),int(self.ui.lineEdit_10.text()),int(self.ui.lineEdit_9.text()),int(self.ui.lineEdit_2.text()),int(self.ui.lineEdit_3.text()))
            #Expar.main_page('HSV2.fasta','hsv2 (taxid:10310) OR hsv-1 (taxid:10298)','homo (taxid:9605)',self.ui.checkBox.isChecked(),self.ui.checkBox_2.isChecked(),self.ui.checkBox_3.isChecked(),int(self.ui.lineEdit_10.text()),int(self.ui.lineEdit_9.text()),int(self.ui.lineEdit_2.text()),int(self.ui.lineEdit_3.text()))
            self.dialog = QtGui.QDialog()
            self.dialog.ui = Ui_Dialog()
            self.dialog.ui.setupUi(self.dialog)
            QtCore.QObject.connect(self.dialog.ui.pushButton, QtCore.SIGNAL("clicked()"), self.submit2) #submit
            QtCore.QObject.connect(self.dialog.ui.pushButton_3, QtCore.SIGNAL("clicked()"), self.savefilefinger)
            for finger in todo.Task.query.all():
                item=QtGui.QTreeWidgetItem([str(finger.finger_id),str(finger.finger_type),str(finger.start),str(finger.length),str(finger.sequence),str(finger.exclude),str(finger.include)])
                #print "exclude:",str(finger.exclude)
                item.finger=finger
                item.setCheckState(0,QtCore.Qt.Checked)
                self.dialog.ui.list.sortByColumn(0, QtCore.Qt.AscendingOrder)
                self.dialog.ui.list.addTopLevelItem(item)
                self.dialog.ui.list.setSortingEnabled(True)
                self.dialog.ui.list.setColumnWidth(4,250)
            self.dialog.exec_()
    def submit2(self):
        self.ui.progressBar.hide()
        iterator = QtGui.QTreeWidgetItemIterator(self.dialog.ui.list)
        task_list={}
        while True:
            value = iterator.value()
            if value is None:
                break
            if value.checkState(0):
                task_list[str(value.text(0))]=1
            else:
                print ""
            iterator.__iadd__(1)
        if task_list==[]:
            return
        #print task_list
        self.dialog2 = QtGui.QDialog()
        self.dialog2.ui = Ui_Dialog2()
        self.dialog2.ui.setupUi(self.dialog2)
        QtCore.QObject.connect(self.dialog2.ui.pushButton, QtCore.SIGNAL("clicked()"), self.savefilebrower_all)
        for finger in todo.Task.query.all():
            if task_list.has_key(str(finger.finger_id)):
                if str(finger.finger_type)=='HTH':
                    QtGui.QMessageBox.warning(Form,"Warning", "HTH fingerprinting sites may take a long time to process!")
                    break
        for finger in todo.Task.query.all():
            self.tick.emit(1)
            SeqDep.delete_file('~tem')
            SeqDep.delete_file('~tri')
            if task_list.has_key(str(finger.finger_id)):
                name='seq_'+str(finger.finger_id)+'_'+str(finger.finger_type)+'_'+str(finger.start)+'_'+str(finger.length)
                finger.done=True
                elixir.session.commit
                Expar_database.templet_generation_and_prediction(finger.sequence, name, int(self.ui.lineEdit_9.text()),int(self.ui.lineEdit_10.text()), float(self.ui.lineEdit_11.text()), float(self.ui.lineEdit_12.text()),float(self.ui.lineEdit_13.text()),float(self.ui.lineEdit_7.text()))
                #Expar_database.templet_generation_and_prediction(finger.sequence, name,8, 30, 37, 0,1,0.00000005)
        for tritemp in todo.Tritemp.query.all():
            item=QtGui.QTreeWidgetItem([str(tritemp.finger_id),str(tritemp.type),str(tritemp.start),str(tritemp.trig_gen),str(tritemp.trigger),str(tritemp.temp), str(tritemp.temp_bayes_class),str(tritemp.temp_pwm_class), str(tritemp.temp_p90_score),str(tritemp.temp_diff_score),str(tritemp.tri_temp_tm),str(tritemp.temp_tm),str(tritemp.bonds)])
            self.dialog2.ui.list.sortByColumn(0, QtCore.Qt.AscendingOrder)
            self.dialog2.ui.list.addTopLevelItem(item)
            self.dialog2.ui.list.setSortingEnabled(True)
            self.dialog2.ui.list.setColumnWidth(4,250)
        #print SeqDep.method_2_prediction(finger.sequence)
        print "************************************\nDone!\n**************************************\n"
        self.dialog2.exec_()

    def reset(self):
                self.ui.lineEdit_9.setText('8')# minimum trigger length
                self.ui.lineEdit_10.setText('30') # maximum trigger length
                self.ui.checkBox.setChecked(True) #checkbox for H-H
                self.ui.checkBox_2.setChecked(True) #checkbox for H-T
                self.ui.checkBox_3.setChecked(True) #checkbox for T-H
                self.ui.lineEdit_11.setText('37') # temperature
                self.ui.lineEdit_12.setText('1') # Na+
                self.ui.lineEdit_13.setText('0') # Mg2+
                self.ui.radioButton.setChecked(True) #um selected for two step hybridization
                self.ui.radioButton_5.setChecked(True) #um selected for strand concentration
                self.ui.lineEdit_7.setText('0.00005')#strand concentration
    def savefilebrower_all(self):
        print "entered savefilebrower_all"
        fName = QtGui.QFileDialog.getSaveFileName(self, "Save as xls file", "Save as new file", self.tr("Text Files (*.xls)"))
        #print "step5", globals()
        if fName.isEmpty() == False:
            Expar.write_xls(str(fName),self, todo.Task.query.all(), todo.Tritemp.query.all())
            #t=file1+'simple.xls'
            #rb = xlrd.open_workbook(t)
            #wb = copy(rb)
            #print(rb.sheet_by_index(0).cell(0,0).value)
            #wb.save(fName)
            print(fName)
            print('is generated!')
            QtGui.QMessageBox.about(self, "Saved", "%s is generated!" % (fName))
            #SeqDep.delete_file('~') # delete all the files under this folder and begins with '~'
            SeqDep.delete_file2()
            self.close()
            exit()
    def savefilefinger(self):
        print "entered savefilefinger"
        fName = QtGui.QFileDialog.getSaveFileName(self, "Save as xls file", "Save as new file", self.tr("Text Files (*.xls)"))
        if fName.isEmpty() == False:
            Expar.write_xls_2(str(fName),self, todo.Task.query.all(), todo.Tritemp.query.all())
            print(fName)
            print('is generated!')
            QtGui.QMessageBox.about(self, "Saved", "%s is generated!" % (fName))
    def advance(self):
        self.dialog_advance = QtGui.QDialog()
        self.dialog_advance.ui= advance.Ui_Dialog()
        self.dialog_advance.ui.setupUi(self.dialog_advance)
        self.dialog_advance.connect(self.dialog_advance.ui.buttonBox,QtCore.SIGNAL("accepted()"), self.saveAdvancedSettings)
        self.dialog_advance.exec_()
    def saveAdvancedSettings(self):
        configure_finger.min_tri_temp_tm=float(self.dialog_advance.ui.lineEdit.text())
        configure_finger.max_tri_temp_tm=float(self.dialog_advance.ui.lineEdit_2.text())
        configure_finger.max_temp_tm=float(self.dialog_advance.ui.lineEdit_4.text())
        configure_finger.max_temp_bonds=float(self.dialog_advance.ui.lineEdit_5.text())
class ProgressBar(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('ProgressBar')
        self.pbar = QtGui.QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)
        self.button = QtGui.QPushButton('Start', self)
        self.button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.button.move(40, 80)
        self.connect(self.button, QtCore.SIGNAL('clicked()'), self.onStart)
        self.timer = QtCore.QBasicTimer()
        self.step = 0
        self.button.setText('Start')
        self.timer.start(100, self)
    def timerEvent(self, event):
        if self.step >= 100:
            self.timer.stop()
            self.pbar.setValue(100)
            return
        self.pbar.setValue(self.step)
    def onStart(self):
        self.step=self.step+10

####################################################################################################
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    if os.system('perl -v >perl.version'):
	QtGui.QMessageBox.critical(Form,"Error", "you haven't properly installed perl yet! wakaka")
	exit()
    Newui = MyForm()
    Newui.show()
    sys.exit(app.exec_())



#    app = QtGui.QApplication(sys.argv)
#    Form = QtGui.QWidget()
#    if os.system('perl -v >perl.version'):
#        QtGui.QMessageBox.critical(Form,"Error", "you haven't properly installed perl yet! wakaka")
#        exit()
#    Newui = MyForm()
#    Newui.show()
#    sys.exit(app.exec_())
