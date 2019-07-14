from PyQt5 import QtWidgets,QtCore,QtGui

from main_ui import Ui_Dialog

class BotWindow(QtWidgets.QDialog,Ui_Dialog):
	def __init__(self,parent=None):
		super(BotWindow,self).__init__(parent)
		self.setupUi(self)
		self.pushButton.clicked.connect(self.parse_message)

	def parse_message(self):
		if self.lineEdit.text().lower() in ['quit','exit']:
			app.quit()
		else:
			self.textBrowser.append("User : {}".format(self.lineEdit.text()))
			self.lineEdit.setText("")

	

if __name__ == "__main__":
	import sys
	app = QtWidgets.QApplication(sys.argv)
	obj = BotWindow()
	obj.show()
	app.exec()