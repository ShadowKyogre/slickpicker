from PyQt4 import QtCore,QtGui
import re

COLOR_RE = re.compile(r'(#[0-9a-fA-F]{3})([0-9a-fA-F]{3})?')

class QColorValidator(QtGui.QValidator):
	def __init__(self, parent=None):
		super().__init__(parent)

	def validate(self, text, pos):
		portion = text
		matchy = COLOR_RE.match(portion)
		text_len=len(text)
		#print(matchy, text)
		if matchy is not None:
			if matchy.group(1) == portion and text_len == 4:
				return (QtGui.QValidator.Acceptable, text, pos)
			elif matchy.group(1) and matchy.group(2) is None:
				return (QtGui.QValidator.Intermediate, text, pos)
			elif matchy.group(1) and matchy.group(2) and text_len == 7:
				return (QtGui.QValidator.Acceptable, text, pos)
			else:
				return (QtGui.QValidator.Invalid, text, pos)
		else:
			if text_len == 0:
				return (QtGui.QValidator.Intermediate, text, pos)
			elif text_len < 4 and text[0] == '#':
				return (QtGui.QValidator.Intermediate, text, pos)
			partial = re.compile(re.escape(text[:pos]))
			for named_col in QtGui.QColor.colorNames():
				match = partial.match(named_col)
				if match is not None:
					if match.string == text:
						return (QtGui.QValidator.Acceptable, text, pos)
					else:
						return (QtGui.QValidator.Intermediate, text, pos)
		return (QtGui.QValidator.Invalid, text, pos)

class QSpinSlider(QtGui.QWidget):
	def __init__(self, parent=None, slider=None, spinner=None):
		super().__init__(parent)

		if slider is None:
			self.slider = QtGui.QSlider()
			self.slider.setOrientation(QtCore.Qt.Horizontal)
		else:
			self.slider = slider

		if spinner is None:
			self.spinner = QtGui.QSpinBox()
		else:
			self.spinner = spinner

		if self.slider.orientation() == QtCore.Qt.Horizontal:
			layout = QtGui.QHBoxLayout(self)
			layout.addWidget(self.slider, alignment = QtCore.Qt.AlignVCenter)
		else:
			layout = QtGui.QVBoxLayout(self)
			layout.addWidget(self.slider, alignment = QtCore.Qt.AlignHCenter)

		layout.addWidget(self.spinner, alignment = QtCore.Qt.AlignHCenter)
		
		self.slider.valueChanged.connect(self.spinner.setValue)
		self.spinner.valueChanged.connect(self.slider.setValue)
		self.slider.rangeChanged.connect(self._updateSpinner)
		#self.spinner.maximumChanged.connect(self.slider.setMaximum)
		#self.spinner.minimumChanged.connect(self.slider.setMiniimum)
	
	def _updateSpinner(self, min, max):
		self.spinner.setRange(min, max)

class QColorLineEdit(QtGui.QLineEdit):
	colorChanged = QtCore.pyqtSignal('QColor')

	def __init__(self, color=None, parent=None):
		super().__init__(parent)
		#self.clicked.connect(lambda x: self.adjustColor())
		self.textChanged.connect(self.adjustColor)
		cmpl = QtGui.QCompleter()
		cmpl.setModel(QtGui.QStringListModel(QtGui.QColor.colorNames()))
		self.setCompleter(cmpl)

		if isinstance(color,QtGui.QColor):
			self.setColor(color)
		else:
			self.setColor(QtGui.QColor())
		self.setValidator(QColorValidator())
	
	def adjustColor(self, text):
		if self.hasAcceptableInput():
			#print("Updating color display with", text)
			self.setColor(text)
		#self.color = QtGui.QColorDialog.getColor(initial=self.color,parent=self)

	def color(self):
		return self._color
	
	def setColor(self,color):
		if isinstance(color,QtGui.QColor):
			#print(color.name())
			self._color = color
			self.setText(color.name())
			self.colorChanged.emit(color)
		elif isinstance(color, str):
			self.setText(color)
			self._color = QtGui.QColor(color)
			self.colorChanged.emit(self._color)
		else:
			raise ValueError("That isn't a QColor!")
	
	color = QtCore.pyqtProperty('QColor', fget=color, fset=setColor)

class QColorSpinEdit(QtGui.QWidget):
	colorChanged = QtCore.pyqtSignal('QColor')
	def __init__(self, color=None, parent=None):
		super().__init__(parent)
		layout = QtGui.QFormLayout(self)

		self.HEdit = QSpinSlider()
		self.SEdit = QSpinSlider()
		self.VEdit = QSpinSlider()
		
		self.REdit = QSpinSlider()
		self.GEdit = QSpinSlider()
		self.BEdit = QSpinSlider()
		
		self.HEdit.slider.setRange(0,359)
		self.SEdit.slider.setRange(0,255)
		self.VEdit.slider.setRange(0,255)
		
		self.REdit.slider.setRange(0,255)
		self.GEdit.slider.setRange(0,255)
		self.BEdit.slider.setRange(0,255)

		self.HEdit.slider.sliderMoved.connect(self._makeHSVColor)
		self.SEdit.slider.sliderMoved.connect(self._makeHSVColor)
		self.VEdit.slider.sliderMoved.connect(self._makeHSVColor)

		self.REdit.slider.sliderMoved.connect(self._makeRGBColor)
		self.GEdit.slider.sliderMoved.connect(self._makeRGBColor)
		self.BEdit.slider.sliderMoved.connect(self._makeRGBColor)


		layout.addRow("Hue", self.HEdit)
		layout.addRow("Saturation", self.SEdit)
		layout.addRow("Value", self.VEdit)

		layout.addRow("Red", self.REdit)
		layout.addRow("Green", self.GEdit)
		layout.addRow("Blue", self.BEdit)

	def _makeRGBColor(self, val):
		self.setColor(QtGui.QColor.fromRgb(self.REdit.slider.value(),
					self.GEdit.slider.value(),
					self.BEdit.slider.value()))

	def _makeHSVColor(self, val):
		self.setColor(QtGui.QColor.fromHsv(self.HEdit.slider.value(),
						   self.SEdit.slider.value(),
						   self.VEdit.slider.value()))

	def color(self):
		return self._color
	
	def setColor(self, color):
		self._color = color
		self.HEdit.slider.setValue(color.hue())
		self.SEdit.slider.setValue(color.saturation())
		self.VEdit.slider.setValue(color.value())
		self.REdit.slider.setValue(color.red())
		self.GEdit.slider.setValue(color.green())
		self.BEdit.slider.setValue(color.blue())
		self.colorChanged.emit(color)

	color = QtCore.pyqtProperty('QColor', fget=color, fset=setColor)

class QColorEdit(QtGui.QWidget):
	colorChanged = QtCore.pyqtSignal('QColor')

	def __init__(self, color=None, parent=None):
		super().__init__(parent)
		layout = QtGui.QGridLayout(self)
		
		self.previewPanel = QtGui.QPushButton()
		self.picky = QtGui.QPushButton()
		self.previewPanel.setCheckable(True)
		self.previewPanel.setText("▶")
		self.colorEdit = QColorLineEdit()
		self.spinColEdit = QColorSpinEdit(self)
		self.spinColEdit.setWindowFlags(QtCore.Qt.Popup)
		self._color = QtGui.QColor()
		self._picking = False

		self.previewPanel.clicked.connect(self._toggleHsv)
		self.picky.clicked.connect(self._preparePicking)
		self.colorEdit.colorChanged.connect(self.colorChanged.emit)
		self.spinColEdit.colorChanged.connect(self.colorChanged.emit)
		self.colorChanged.connect(self._updatePreview)
		self.spinColEdit.colorChanged.connect(self.setColor)
		self.colorEdit.colorChanged.connect(self.spinColEdit.setColor)
		self.spinColEdit.installEventFilter(self)

		layout.addWidget(self.colorEdit,0,0,1,4)
		#layout.addWidget(self.spinColEdit,1,0,1,5)
		layout.addWidget(self.previewPanel,0,5,1,1)
		layout.addWidget(self.picky,0,4,1,1)
		self._updatePreview(self.color)

	def _preparePicking(self, event):
		self._picking = True
		self.grabKeyboard()
		self.grabMouse(QtCore.Qt.CrossCursor)

	def mouseMoveEvent(self, event):
		if self._picking:
			self._pickColor(event.globalPos())
			return
		return QWidget.mouseMoveEvent(self, event)

	def keyPressEvent(self, event):
		if self._picking:
			if event.key() == QtCore.Qt.Key_Escape:
				self._picking = False
				self.releaseKeyboard()
				self.releaseMouse()
			event.accept()
			return
		return QWidget.keypressEvent(self, event)

	def mouseReleaseEvent(self, event):
		if self._picking:
			self._picking = False
			self.releaseKeyboard()
			self.releaseMouse()
			self._pickColor(event.globalPos())
			return

	def _pickColor(self, pos):
		pixmap = QtGui.QPixmap.grabWindow(QtGui.QApplication.desktop().winId(), pos.x(), pos.y(), 1, 1)
		img = pixmap.toImage()
		self.setColor(QtGui.QColor(img.pixel(0,0)))

	def eventFilter(self, source, event):
		if source is self.spinColEdit and event.type() in (QtCore.QEvent.Close, QtCore.QEvent.Hide, QtCore.QEvent.HideToParent):
			self.previewPanel.setChecked(False)
			self.previewPanel.setText("▶")
		return QtGui.QWidget.eventFilter(self, source, event)

	def _toggleHsv(self, checked):
		if checked:
			self.spinColEdit.show()
			really_here = self.mapToGlobal(self.rect().bottomRight())
			bottom_margin = self.layout().contentsMargins().bottom()
			bottom_corner= really_here.x()-self.spinColEdit.width()
			pop_here = really_here.y()+self.height()/2-bottom_margin
			print(bottom_corner, pop_here, self.height(), really_here.y(), bottom_margin)
			self.spinColEdit.move(bottom_corner, pop_here)
			self.previewPanel.setText("▼")
		else:
			print("e")
			self.spinColEdit.hide()
			self.previewPanel.setText("▶")

	def _updatePreview(self, color):
		#palette = QtGui.QPalette(QtGui.QApplication.palette())
		#palette.setColor(QtGui.QPalette.Background, color)
		#self.previewPanel.setPalette(palette)
		px=QtGui.QPixmap(128,128)
		px.fill(self._color)
		self.previewPanel.setIcon(QtGui.QIcon(px))

	def color(self):
		return self._color
	
	def setColor(self, color):
		self._color = color
		self.colorChanged.emit(color)

	color = QtCore.pyqtProperty('QColor', fget=color, fset=setColor)

if __name__ == "__main__":
	app=QtGui.QApplication([])
	#dip=QSpinSlider()
	a=QtGui.QWidget()
	layout=QtGui.QVBoxLayout(a)
	stuff=QColorEdit()
	#stuff2=QColorEdit()
	#stuff3=QColorEdit()
	layout.addWidget(stuff)
	#layout.addWidget(stuff2)
	#layout.addWidget(stuff3)
	#dip.show()
	a.show()
	exit(app.exec())
