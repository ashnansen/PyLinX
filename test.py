'''
Some PySide stuff - disorganized
'''
import sys
# from PySide import QtCore, QtGui, QtUiTools
# 
# 
# 
# # def loadUiWidget(uifilename, parent=None):
# #     loader = QtUiTools.QUiLoader()
# #     uifile = QtCore.QFile(uifilename)
# #     uifile.open(QtCore.QFile.ReadOnly)
# #     ui = loader.load(uifile, parent)
# #     uifile.close()
# #     return ui
# # 
# # 
# # if __name__ == "__main__":
# #     import sys
# #     app = QtGui.QApplication(sys.argv)
# #     MainWindow = loadUiWidget("PyLinX_v0.ui")
# #     MainWindow.show()
# #     sys.exit(app.exec_())
#  
# class BQUiLoader(QtUiTools.QUiLoader):
#     def __init__(self, baseinstance):
#         #QtUiTools.QUiLoader.__init__(self)
#         super(BQUiLoader, self).__init__(baseinstance)
#         self.baseinstance = baseinstance
#   
# #     def createWidget(self, className, parent=None, name=""):
# #         widget = QtUiTools.QUiLoader.createWidget(self, className, parent, name)
# #         if parent is None:
# #             return self.baseinstance
# #         else:
# #             setattr(self.baseinstance, name, widget)
# #             return widget
# 
# 
# 
#     def createWidget(self, className, parent = None, name = ""):
#         if className in QtUiTools.QUiLoader.availableWidgets(self):
#             widget = QtUiTools.QUiLoader.createWidget(self, className, parent, name)
#         else:
#             if hasattr(self.baseinstance, "customWidgets"):
#                 if className in self.baseinstance.customWidgets.keys():
#                     widget = self.baseinstance.customWidgets[className](parent)
#                 else:
#                     raise KeyError("Unknown widget '%s'" % className)
#             else:
#                 raise AttributeError("Trying to load custom widget '%s', but base\
#                     instance '%s' does not specify custom widgets." % (className,\
#                     repr(self.baseinstance)))
#         
#         if self.baseinstance is not None:
#             setattr(self.baseinstance, name, widget)
#         
#         return widget
# 
# 
#  
# class MyWidget(QtGui.QWidget, QtCore.QObject):
#     def __init__(self, parent = None):
#         super(QtGui.QWidget, self).__init__(parent)
#         loader = BQUiLoader(None)
#         file = QtCore.QFile("PyLinX_v0.ui")
#         file.open(QtCore.QFile.ReadOnly)
#         myWidget = loader.load(file, self)
#         file.close()
#  
#         layout = QtGui.QVBoxLayout()
#         layout.addWidget(myWidget)
#         self.setLayout(layout)
#         self.show()
#          
# if __name__ == "__main__":
#     import sys
#     app = QtGui.QApplication(sys.argv)
#     myWindow = MyWidget()
#     sys.exit(app.exec_())
#      
#      
#  
# # 
# # def loadUi(uifile, baseinstance=None):
# #     loader = MyQUiLoader(baseinstance)
# #     ui = loader.load(uifile)
# #     QtCore.QMetaObject.connectSlotsByName(ui)
# #     return ui
# 
# # import sys
# # from PySide import QtGui
# #  
# # app = QtGui.QApplication(sys.argv)
# #  
# # win = QtGui.QWidget()
# #  
# # win.resize(320, 240)  
# # win.setWindowTitle("Hello, World!") 
# # win.show()
# #  
# # sys.exit(app.exec_())

'''
Interactive svg
'''

# 
# import sys
# from PyQt4 import QtCore, QtGui, QtSvg
# from PyQt4.QtWebKit import QGraphicsWebView
# if __name__ == "__main__":
#     app = QtGui.QApplication(sys.argv)
# 
#     scene = QtGui.QGraphicsScene()
#     view = QtGui.QGraphicsView(scene)
# 
#     br = QtSvg.QGraphicsSvgItem("your_interactive_svg.svg").boundingRect()
# 
#     webview = QGraphicsWebView()
#     webview.load(QtCore.QUrl("C:\your_interactive_svg.svg"))
#     webview.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
#     webview.setCacheMode(QtGui.QGraphicsItem.NoCache)
#     webview.resize(br.width(), br.height())
# 
#     scene.addItem(webview)
#     view.resize(br.width()+10, br.height()+10)
#     view.show()
#     sys.exit(app.exec_())
#     
'''
drag and drop
'''
    
#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial

This is a simple drag and drop example. 

author: Jan Bodnar
website: zetcode.com
last edited: October 2013
"""

# import sys
# from PyQt4 import QtGui
# 
# 
# class Button(QtGui.QPushButton):
#   
#     def __init__(self, title, parent):
#         super(Button, self).__init__(title, parent)
#         
#         self.setAcceptDrops(True)
# 
#     def dragEnterEvent(self, e):
#       
#         if e.mimeData().hasFormat('text/plain'):
#             e.accept()
#             
#         else:
#             e.ignore() 
# 
#     def dropEvent(self, e):
#         
#         self.setText(e.mimeData().text()) 
# 
# 
# class Example(QtGui.QWidget):
#   
#     def __init__(self):
#         super(Example, self).__init__()
#         
#         self.initUI()
#         
#     def initUI(self):
# 
#         edit = QtGui.QLineEdit('', self)
#         edit.setDragEnabled(True)
#         edit.move(30, 65)
# 
#         button = Button("Button", self)
#         button.move(190, 65)
#         
#         self.setWindowTitle('Simple Drag & Drop')
#         self.setGeometry(300, 300, 300, 150)
#         self.show()
# 
# 
# def main():
#   
#     app = QtGui.QApplication([])
#     ex = Example()
#     app.exec_()  
#   
# 
# if __name__ == '__main__':
#     main()  

#!/usr/bin/env python

############################################################################
##
## Copyright (C) 2006-2006 Trolltech ASA. All rights reserved.
##
## This file is part of the example classes of the Qt Toolkit.
##
## Licensees holding a valid Qt License Agreement may use this file in
## accordance with the rights, responsibilities and obligations
## contained therein.  Please consult your licensing agreement or
## contact sales@trolltech.com if any conditions of this licensing
## agreement are not clear to you.
##
## Further information about Qt licensing is available at:
## http://www.trolltech.com/products/qt/licensing.html or by
## contacting info@trolltech.com.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

'''
Qt Graphics-View Example
'''

# from PyQt4 import QtCore, QtGui
# 
# #import dragdroprobot_rc
# 
# 
# class ColorItem(QtGui.QGraphicsItem):
#     n = 0
# 
#     def __init__(self):
#         super(ColorItem, self).__init__()
# 
#         self.color = QtGui.QColor(QtCore.qrand() % 256, QtCore.qrand() % 256,
#                 QtCore.qrand() % 256)
# 
#         self.setToolTip(
#             "QColor(%d, %d, %d)\nClick and drag this color onto the robot!" % 
#               (self.color.red(), self.color.green(), self.color.blue())
#         )
#         self.setCursor(QtCore.Qt.OpenHandCursor)
#     
#     def boundingRect(self):
#         return QtCore.QRectF(-15.5, -15.5, 34, 34)
# 
#     def paint(self, painter, option, widget):
#         painter.setPen(QtCore.Qt.NoPen)
#         painter.setBrush(QtCore.Qt.darkGray)
#         painter.drawEllipse(-12, -12, 30, 30)
#         painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
#         painter.setBrush(QtGui.QBrush(self.color))
#         painter.drawEllipse(-15, -15, 30, 30)
# 
#     def mousePressEvent(self, event):
#         if event.button() != QtCore.Qt.LeftButton:
#             event.ignore()
#             return
# 
#         self.setCursor(QtCore.Qt.ClosedHandCursor)
# 
#     def mouseMoveEvent(self, event):
#         if QtCore.QLineF(QtCore.QPointF(event.screenPos()), QtCore.QPointF(event.buttonDownScreenPos(QtCore.Qt.LeftButton))).length() < QtGui.QApplication.startDragDistance():
#             return
# 
#         drag = QtGui.QDrag(event.widget())
#         mime = QtCore.QMimeData()
#         drag.setMimeData(mime)
# 
#         ColorItem.n += 1
#         if ColorItem.n > 2 and QtCore.qrand() % 3 == 0:
#             image = QtGui.QImage(':/images/head.png')
#             mime.setImageData(image)
#             drag.setPixmap(QtGui.QPixmap.fromImage(image).scaled(30,40))
#             drag.setHotSpot(QtCore.QPoint(15, 30))
#         else:
#             mime.setColorData(self.color)
#             mime.setText("#%02x%02x%02x" % (self.color.red(), self.color.green(), self.color.blue()))
# 
#             pixmap = QtGui.QPixmap(34, 34)
#             pixmap.fill(QtCore.Qt.white)
# 
#             painter = QtGui.QPainter(pixmap)
#             painter.translate(15, 15)
#             painter.setRenderHint(QtGui.QPainter.Antialiasing)
#             self.paint(painter, None, None)
#             painter.end()
# 
#             pixmap.setMask(pixmap.createHeuristicMask())
# 
#             drag.setPixmap(pixmap)
#             drag.setHotSpot(QtCore.QPoint(15, 20))
# 
#         drag.exec_()
#         self.setCursor(QtCore.Qt.OpenHandCursor)
# 
#     def mouseReleaseEvent(self, event):
#         self.setCursor(QtCore.Qt.OpenHandCursor)
# 
# 
# class RobotPart(QtGui.QGraphicsItem):
#     def __init__(self, parent=None):
#         super(RobotPart, self).__init__(parent)
# 
#         self.color = QtGui.QColor(QtCore.Qt.lightGray)
#         self.pixmap = None
#         self.dragOver = False
# 
#         self.setAcceptDrops(True)
# 
#     def dragEnterEvent(self, event):
#         if event.mimeData().hasColor() or \
#           (isinstance(self, RobotHead) and event.mimeData().hasImage()):
#             event.setAccepted(True)
#             self.dragOver = True
#             self.update()
#         else:
#             event.setAccepted(False)
# 
#     def dragLeaveEvent(self, event):
#         self.dragOver = False
#         self.update()
#  
#     def dropEvent(self, event):
#         self.dragOver = False
#         if event.mimeData().hasColor():
#             self.color = QtGui.QColor(event.mimeData().colorData())
#         elif event.mimeData().hasImage():
#             self.pixmap = QtGui.QPixmap(event.mimeData().imageData())
# 
#         self.update()
# 
# 
# class RobotHead(RobotPart):
#     def boundingRect(self):
#         return QtCore.QRectF(-15, -50, 30, 50)
# 
#     def paint(self, painter, option, widget=None):
#         if not self.pixmap:
#             painter.setBrush(self.dragOver and self.color.light(130) 
#                                             or self.color)
#             painter.drawRoundedRect(-10, -30, 20, 30, 25, 25,
#                     QtCore.Qt.RelativeSize)
#             painter.setBrush(QtCore.Qt.white)
#             painter.drawEllipse(-7, -3 - 20, 7, 7)
#             painter.drawEllipse(0, -3 - 20, 7, 7)
#             painter.setBrush(QtCore.Qt.black)
#             painter.drawEllipse(-5, -1 - 20, 2, 2)
#             painter.drawEllipse(2, -1 - 20, 2, 2)
#             painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
#             painter.setBrush(QtCore.Qt.NoBrush)
#             painter.drawArc(-6, -2 - 20, 12, 15, 190 * 16, 160 * 16)
#         else:
#             painter.scale(.2272, .2824)
#             painter.drawPixmap(QtCore.QPointF(-15*4.4, -50*3.54), self.pixmap)
# 
# 
# class RobotTorso(RobotPart):
#     def boundingRect(self):
#         return QtCore.QRectF(-30, -20, 60, 60)
# 
#     def paint(self, painter, option, widget=None):
#         painter.setBrush(self.dragOver and self.color.light(130) 
#                                         or self.color)
#         painter.drawRoundedRect(-20, -20, 40, 60, 25, 25,
#                 QtCore.Qt.RelativeSize)
#         painter.drawEllipse(-25, -20, 20, 20)
#         painter.drawEllipse(5, -20, 20, 20)
#         painter.drawEllipse(-20, 22, 20, 20)
#         painter.drawEllipse(0, 22, 20, 20)
# 
# 
# class RobotLimb(RobotPart):
#     def boundingRect(self):
#         return QtCore.QRectF(-5, -5, 40, 10)
# 
#     def paint(self, painter, option, widget=None):
#         painter.setBrush(self.dragOver and self.color.light(130) or self.color)
#         painter.drawRoundedRect(self.boundingRect(), 50, 50,
#                 QtCore.Qt.RelativeSize)
#         painter.drawEllipse(-5, -5, 10, 10)
# 
# 
# class Robot(RobotPart):
#     def __init__(self):
#         super(Robot, self).__init__()
# 
#         self.torsoItem         = RobotTorso(self)
#         self.headItem          = RobotHead(self.torsoItem)
#         self.upperLeftArmItem  = RobotLimb(self.torsoItem)
#         self.lowerLeftArmItem  = RobotLimb(self.upperLeftArmItem)
#         self.upperRightArmItem = RobotLimb(self.torsoItem)
#         self.lowerRightArmItem = RobotLimb(self.upperRightArmItem)
#         self.upperRightLegItem = RobotLimb(self.torsoItem)
#         self.lowerRightLegItem = RobotLimb(self.upperRightLegItem)
#         self.upperLeftLegItem  = RobotLimb(self.torsoItem)
#         self.lowerLeftLegItem  = RobotLimb(self.upperLeftLegItem)
# 
#         self.timeline = QtCore.QTimeLine()
#         settings = [
#         #             item               position    rotation at
#         #                                 x    y    time 0  /  1
#             ( self.headItem,              0,  -18,      20,   -20 ),
#             ( self.upperLeftArmItem,    -15,  -10,     190,   180 ),
#             ( self.lowerLeftArmItem,     30,    0,      50,    10 ),
#             ( self.upperRightArmItem,    15,  -10,     300,   310 ),
#             ( self.lowerRightArmItem,    30,    0,       0,   -70 ),
#             ( self.upperRightLegItem,    10,   32,      40,   120 ),
#             ( self.lowerRightLegItem,    30,    0,      10,    50 ),
#             ( self.upperLeftLegItem,    -10,   32,     150,    80 ),
#             ( self.lowerLeftLegItem,     30,    0,      70,    10 ),
#             ( self.torsoItem,             0,    0,       5,   -20 )
#         ]
#         self.animations = []
#         for item, pos_x, pos_y, rotation1, rotation2 in settings: 
#             item.setPos(pos_x,pos_y)
#             animation = QtGui.QGraphicsItemAnimation()
#             animation.setItem(item)
#             animation.setTimeLine(self.timeline)
#             animation.setRotationAt(0, rotation1)
#             animation.setRotationAt(1, rotation2)
#             self.animations.append(animation)
#         self.animations[0].setScaleAt(1, 1.1, 1.1)
#     
#         self.timeline.setUpdateInterval(1000 / 25)
#         self.timeline.setCurveShape(QtCore.QTimeLine.SineCurve)
#         self.timeline.setLoopCount(0)
#         self.timeline.setDuration(2000)
#         self.timeline.start()
# 
#     def boundingRect(self):
#         return QtCore.QRectF()
# 
#     def paint(self, painter, option, widget=None):
#         pass
# 
# 
# if __name__== '__main__':
# 
#     import sys
#     import math
# 
#     app = QtGui.QApplication(sys.argv)
# 
#     QtCore.qsrand(QtCore.QTime(0, 0, 0).secsTo(QtCore.QTime.currentTime()))
# 
#     scene = QtGui.QGraphicsScene(-200, -200, 400, 400)
# 
#     for i in range(10):
#         item = ColorItem()
#         angle = i*6.28 / 10.0
#         item.setPos(math.sin(angle)*150, math.cos(angle)*150)
#         scene.addItem(item)
# 
#     robot = Robot()
#     robot.scale(1.4, 1.4)
#     robot.setPos(0, -20)
#     scene.addItem(robot)
# 
#     view = QtGui.QGraphicsView(scene)
#     view.setRenderHint(QtGui.QPainter.Antialiasing)
#     view.setViewportUpdateMode(QtGui.QGraphicsView.BoundingRectViewportUpdate)
#     view.setBackgroundBrush(QtGui.QColor(230, 200, 167))
#     view.setWindowTitle("Drag and Drop Robot")
#     view.show()
# 
#     sys.exit(app.exec_())

#!/usr/bin/env python

# -*- coding: utf-8 -*-
#!/usr/bin/env python

'''
Simple GUI
'''
# from PyQt4 import QtGui, QtCore
# 
# class Images(QtGui.QScrollArea):
#     def __init__(self, images):
#         super(Images, self).__init__()
# 
#         self.content = QtGui.QWidget()
#         self.layout = QtGui.QGridLayout(self.content)
#         self.layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
#         col = 0
#         for image in images:
#             thumb = QtGui.QLabel()
#             thumb.setPixmap(QtGui.QPixmap(image))
#             self.layout.addWidget(thumb, 0, col)
#             col += 1
# 
#         self.setWidget(self.content)
#         self.setMinimumWidth(self.content.sizeHint().width())
#         self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
# 
# app = QtGui.QApplication([])
# 
# window = QtGui.QWidget()
# layout = QtGui.QVBoxLayout(window)
# scroll_area = Images(['hallo.png','hallo.png','hallo.png','hallo.png'])
# layout.addWidget(scroll_area)
# window.show()
# 
# app.exec_()

#!/usr/bin/env python

#############################################################################
##
## Copyright (C) 2005-2005 Trolltech AS. All rights reserved.
##
## This file is part of the example classes of the Qt Toolkit.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following information to ensure GNU
## General Public Licensing requirements will be met:
## http://www.trolltech.com/products/qt/opensource.html
##
## If you are unsure which license is appropriate for your use, please
## review the following information:
## http://www.trolltech.com/products/qt/licensing.html or contact the
## sales department at sales@trolltech.com.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
#############################################################################
'''
Bildbetrachter
'''
# from PyQt4 import QtCore, QtGui
# 
# 
# class ImageViewer(QtGui.QMainWindow):
#     def __init__(self):
#         super(ImageViewer, self).__init__()
# 
#         self.printer = QtGui.QPrinter()
#         self.scaleFactor = 0.0
# 
#         self.imageLabel = QtGui.QLabel()
#         self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
#         self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored,
#                 QtGui.QSizePolicy.Ignored)
#         self.imageLabel.setScaledContents(True)
# 
#         self.scrollArea = QtGui.QScrollArea()
#         self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
#         self.scrollArea.setWidget(self.imageLabel)
#         self.setCentralWidget(self.scrollArea)
# 
#         self.createActions()
#         self.createMenus()
# 
#         self.setWindowTitle("Image Viewer")
#         self.resize(500, 400)
# 
#     def open(self):
#         fileName = QtGui.QFileDialog.getOpenFileName(self, "Open File",
#                 QtCore.QDir.currentPath())
#         if fileName:
#             image = QtGui.QImage(fileName)
#             if image.isNull():
#                 QtGui.QMessageBox.information(self, "Image Viewer",
#                         "Cannot load %s." % fileName)
#                 return
# 
#             self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image))
#             self.scaleFactor = 1.0
# 
#             self.printAct.setEnabled(True)
#             self.fitToWindowAct.setEnabled(True)
#             self.updateActions()
# 
#             if not self.fitToWindowAct.isChecked():
#                 self.imageLabel.adjustSize()
# 
#     def print_(self):
#         dialog = QtGui.QPrintDialog(self.printer, self)
#         if dialog.exec_():
#             painter = QtGui.QPainter(self.printer)
#             rect = painter.viewport()
#             size = self.imageLabel.pixmap().size()
#             size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
#             painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
#             painter.setWindow(self.imageLabel.pixmap().rect())
#             painter.drawPixmap(0, 0, self.imageLabel.pixmap())
# 
#     def zoomIn(self):
#         self.scaleImage(1.25)
# 
#     def zoomOut(self):
#         self.scaleImage(0.8)
# 
#     def normalSize(self):
#         self.imageLabel.adjustSize()
#         self.scaleFactor = 1.0
# 
#     def fitToWindow(self):
#         fitToWindow = self.fitToWindowAct.isChecked()
#         self.scrollArea.setWidgetResizable(fitToWindow)
#         if not fitToWindow:
#             self.normalSize()
# 
#         self.updateActions()
# 
#     def about(self):
#         QtGui.QMessageBox.about(self, "About Image Viewer",
#                 "<p>The <b>Image Viewer</b> example shows how to combine "
#                 "QLabel and QScrollArea to display an image. QLabel is "
#                 "typically used for displaying text, but it can also display "
#                 "an image. QScrollArea provides a scrolling view around "
#                 "another widget. If the child widget exceeds the size of the "
#                 "frame, QScrollArea automatically provides scroll bars.</p>"
#                 "<p>The example demonstrates how QLabel's ability to scale "
#                 "its contents (QLabel.scaledContents), and QScrollArea's "
#                 "ability to automatically resize its contents "
#                 "(QScrollArea.widgetResizable), can be used to implement "
#                 "zooming and scaling features.</p>"
#                 "<p>In addition the example shows how to use QPainter to "
#                 "print an image.</p>")
# 
#     def createActions(self):
#         self.openAct = QtGui.QAction("&Open...", self, shortcut="Ctrl+O",
#                 triggered=self.open)
# 
#         self.printAct = QtGui.QAction("&Print...", self, shortcut="Ctrl+P",
#                 enabled=False, triggered=self.print_)
# 
#         self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
#                 triggered=self.close)
# 
#         self.zoomInAct = QtGui.QAction("Zoom &In (25%)", self,
#                 shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)
# 
#         self.zoomOutAct = QtGui.QAction("Zoom &Out (25%)", self,
#                 shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)
# 
#         self.normalSizeAct = QtGui.QAction("&Normal Size", self,
#                 shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)
# 
#         self.fitToWindowAct = QtGui.QAction("&Fit to Window", self,
#                 enabled=False, checkable=True, shortcut="Ctrl+F",
#                 triggered=self.fitToWindow)
# 
#         self.aboutAct = QtGui.QAction("&About", self, triggered=self.about)
# 
#         self.aboutQtAct = QtGui.QAction("About &Qt", self,
#                 triggered=QtGui.qApp.aboutQt)
# 
#     def createMenus(self):
#         self.fileMenu = QtGui.QMenu("&File", self)
#         self.fileMenu.addAction(self.openAct)
#         self.fileMenu.addAction(self.printAct)
#         self.fileMenu.addSeparator()
#         self.fileMenu.addAction(self.exitAct)
# 
#         self.viewMenu = QtGui.QMenu("&View", self)
#         self.viewMenu.addAction(self.zoomInAct)
#         self.viewMenu.addAction(self.zoomOutAct)
#         self.viewMenu.addAction(self.normalSizeAct)
#         self.viewMenu.addSeparator()
#         self.viewMenu.addAction(self.fitToWindowAct)
# 
#         self.helpMenu = QtGui.QMenu("&Help", self)
#         self.helpMenu.addAction(self.aboutAct)
#         self.helpMenu.addAction(self.aboutQtAct)
# 
#         self.menuBar().addMenu(self.fileMenu)
#         self.menuBar().addMenu(self.viewMenu)
#         self.menuBar().addMenu(self.helpMenu)
# 
#     def updateActions(self):
#         self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
#         self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
#         self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())
# 
#     def scaleImage(self, factor):
#         self.scaleFactor *= factor
#         self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())
# 
#         self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
#         self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)
# 
#         self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
#         self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)
# 
#     def adjustScrollBar(self, scrollBar, factor):
#         scrollBar.setValue(int(factor * scrollBar.value()
#                                 + ((factor - 1) * scrollBar.pageStep()/2)))
# 
# 
# if __name__ == '__main__':
# 
#     import sys
# 
#     app = QtGui.QApplication(sys.argv)
#     imageViewer = ImageViewer()
#     imageViewer.show()
#     sys.exit(app.exec_())

'''
Diamond example
'''

# class First(object):
#     def __init__(self):
#         print "first"
#         self.test = "test"
# 
# class Second(First):
#     def __init__(self):
#         super(Second, self).__init__()
#         print "second"
# 
# class Third(First):
#     def __init__(self):
#         super(Third,self).__init__()
#         print "third"
# 
# class Fourth(Second, Third):
#     def __init__(self):
#         super(Fourth, self).__init__()
#         print "that's it"
#         
# fourth = Fourth()
# print "Ende!"

'''
Font size
'''

# from PyQt4 import QtGui, QtCore
# 
# class Window(QtGui.QWidget):
#     def __init__(self):
#         QtGui.QWidget.__init__(self)
#         self.setAutoFillBackground(True)
#         self.setBackgroundRole(QtGui.QPalette.Mid)
#         self.setLayout(QtGui.QFormLayout(self))
#         self.fonts = QtGui.QFontComboBox(self)
#         self.fonts.currentFontChanged.connect(self.handleFontChanged)
#         self.layout().addRow('font:', self.fonts)
#         for text in (
#             u'H\u2082SO\u2084 + Be',
#             u'jib leaf jib leaf',
#             ):
#             for label in ('boundingRect', 'width', 'size'):
#                 field = QtGui.QLabel(text, self)
#                 field.setStyleSheet('background-color: yellow')
#                 field.setAlignment(QtCore.Qt.AlignCenter)
#                 self.layout().addRow(label, field)
#         self.handleFontChanged(self.font())
# 
#     def handleFontChanged(self, font):
#         layout = self.layout()
#         font.setPointSize(20)
#         metrics = QtGui.QFontMetrics(font)
#         for index in range(1, layout.rowCount()):
#             field = layout.itemAt(index, QtGui.QFormLayout.FieldRole).widget()
#             label = layout.itemAt(index, QtGui.QFormLayout.LabelRole).widget()
#             method = label.text().split(' ')[0]
#             text = field.text()
#             if method == 'width':
#                 width = metrics.width(text)
#             elif method == 'size':
#                 width = metrics.size(field.alignment(), text).width()
#             else:
#                 width = metrics.boundingRect(text).width()
#             field.setFixedWidth(width)
#             field.setFont(font)
#             label.setText('%s (%d):' % (method, width))
# 
# if __name__ == '__main__':
# 
#     import sys
#     app = QtGui.QApplication(sys.argv)
#     window = Window()
#     window.show()
#     sys.exit(app.exec_())



def calcMain():
    
    global DataDictionary
    
    Variable_3 = DataDictionary["Variable_3"]
    Variable_1 = DataDictionary["Variable_1"]
    Variable_2 = DataDictionary["Variable_2"]
    
    Variable_3 = Variable_1 + Variable_2
    
    DataDictionary["Variable_3"] = Variable_3
    DataDictionary["Variable_1"] = Variable_1
    DataDictionary["Variable_2"] = Variable_2
    

