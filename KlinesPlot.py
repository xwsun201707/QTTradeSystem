# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from Ui_KlinesPlot import Ui_Form

import sys, datetime
import pyqtgraph as pg
import tushare as ts
import numpy as np
from collections import deque

########################################################################
# 键盘鼠标功能
########################################################################
class KeyWraper(QtWidgets.QWidget):
    """键盘鼠标功能支持的元类"""

    # 初始化
    # ----------------------------------------------------------------------
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

    # 重载方法keyPressEvent(self,event),即按键按下事件方法
    # ----------------------------------------------------------------------
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up:
            self.onUp()
        elif event.key() == QtCore.Qt.Key_Down:
            self.onDown()
        elif event.key() == QtCore.Qt.Key_Left:
            self.onLeft()
        elif event.key() == QtCore.Qt.Key_Right:
            self.onRight()
        elif event.key() == QtCore.Qt.Key_PageUp:
            self.onPre()
        elif event.key() == QtCore.Qt.Key_PageDown:
            self.onNxt()

    # 重载方法mousePressEvent(self,event),即鼠标点击事件方法
    # ----------------------------------------------------------------------
    def mousePressEvent(self, event):

        if event.button() == QtCore.Qt.RightButton:
            self.onRClick(event.pos())
        elif event.button() == QtCore.Qt.LeftButton:
            self.onLClick(event.pos())

    # 重载方法mouseReleaseEvent(self,event),即鼠标点击事件方法
    # ----------------------------------------------------------------------
    def mouseReleaseEvent(self, event):

        if event.button() == QtCore.Qt.RightButton:
            self.onRRelease(event.pos())
        elif event.button() == QtCore.Qt.LeftButton:
            self.onLRelease(event.pos())
        self.releaseMouse()

    # 重载方法wheelEvent(self,event),即滚轮事件方法
    # ----------------------------------------------------------------------
    def wheelEvent(self, event):

        if event.delta() > 0:
            self.onUp()
        else:
            self.onDown()

    # 重载方法dragMoveEvent(self,event),即拖动事件方法
    # ----------------------------------------------------------------------
    def paintEvent(self, event):
        self.onPaint()

    # PgDown键
    # ----------------------------------------------------------------------
    def onNxt(self):
        pass

    # PgUp键
    # ----------------------------------------------------------------------
    def onPre(self):
        pass

    # 向上键和滚轮向上
    # ----------------------------------------------------------------------
    def onUp(self):
        pass

    # 向下键和滚轮向下
    # ----------------------------------------------------------------------
    def onDown(self):
        pass

    # 向左键
    # ----------------------------------------------------------------------
    def onLeft(self):
        pass

    # 向右键
    # ----------------------------------------------------------------------
    def onRight(self):
        pass

    # 鼠标左单击
    # ----------------------------------------------------------------------
    def onLClick(self, pos):
        pass

    # 鼠标右单击
    # ----------------------------------------------------------------------
    def onRClick(self, pos):
        pass

    # 鼠标左释放
    # ----------------------------------------------------------------------
    def onLRelease(self, pos):
        pass

    # 鼠标右释放
    # ----------------------------------------------------------------------
    def onRRelease(self, pos):
        pass

    # 画图
    # ----------------------------------------------------------------------
    def onPaint(self):
        pass


########################################################################
# 选择缩放功能支持
########################################################################
class CustomViewBox(pg.ViewBox):
    # ----------------------------------------------------------------------
    def __init__(self, parent, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
        self.parent = parent
        # 拖动放大模式
        # self.setMouseMode(self.RectMode)

    ## 右键自适应
    # ----------------------------------------------------------------------
    def mouseClickEvent(self, ev):

        if ev.button() == QtCore.Qt.RightButton:
            self.autoRange()

    # 重载方法mousePressEvent(self,event),即鼠标点击事件方法
    # ----------------------------------------------------------------------
    def mousePressEvent(self, event):

        pg.ViewBox.mousePressEvent(self, event)

    # 重载方法mouseDragEvent(self,event),即拖动事件方法
    def mouseDragEvent(self, ev, axis=None):
        # if ev.start==True and ev.finish==False: ##判断拖拽事件是否结束
        pos = ev.pos()
        lastPos = ev.lastPos()
        dif = pos - lastPos

        rect = self.sceneBoundingRect()

        pianyi = dif.x() * self.parent.countK * 2 / rect.width()

        self.parent.index -= int(pianyi)
        self.parent.index = max(self.parent.index, 60)
        xMax = self.parent.index + self.parent.countK  ##
        xMin = self.parent.index - self.parent.countK
        if xMin < 0:
            xMin = 0

        # self.parent.plotAll(False, xMin, xMax) #注释原因：拖动事件不需要先绘制图形界面

        pg.ViewBox.mouseDragEvent(self, ev, axis)
    # ## 重载方法resizeEvent(self, ev)

    def resizeEvent(self, ev):
        self.linkedXChanged()
        self.linkedYChanged()
        self.updateAutoRange()
        self.updateViewRange()
        self._matrixNeedsUpdate = True
        self.sigStateChanged.emit(self)
        self.background.setRect(self.rect())
        self.sigResized.emit(self)
        self.parent.refreshHeight()


########################################################################
# 时间序列，横坐标支持
########################################################################
class MyStringAxis(pg.AxisItem):
    """时间序列横坐标支持"""

    # 初始化
    # ----------------------------------------------------------------------
    def __init__(self, xdict, *args, **kwargs):
        pg.AxisItem.__init__(self, *args, **kwargs)
        self.minVal = 0
        self.maxVal = 0
        self.xdict = xdict
        self.x_values = np.asarray(xdict.keys())
        self.x_strings = xdict.values()
        self.setPen(color=(255, 255, 255, 255), width=0.8)
        self.setStyle(tickFont=QFont("Roman times", 10, QFont.Bold), autoExpandTextSpace=True)

    # 更新坐标映射表
    # ----------------------------------------------------------------------
    def update_xdict(self, xdict):
        self.xdict.update(xdict)
        self.x_values = np.asarray(self.xdict.keys())
        self.x_strings = self.xdict.values()

    # 将原始横坐标转换为时间字符串,第一个坐标包含日期
    # ----------------------------------------------------------------------
    def tickStrings(self, values, scale, spacing):
        strings = []
        for v in values:
            vs = v * scale
            if vs in self.x_values:
                vstr = self.x_strings[np.abs(self.x_values - vs).argmin()]
                if (isinstance(vstr, (str))):
                    vstr = vstr
                else:
                    vstr = vstr.strftime('%Y-%m-%d %H:%M:%S')
            else:
                vstr = ""
            strings.append(vstr)
        return strings


########################################################################
# K线图形对象
########################################################################
class CandlestickItem(pg.GraphicsObject):
    """K线图形对象"""

    # 初始化
    # ----------------------------------------------------------------------
    def __init__(self, data):

        """初始化"""
        pg.GraphicsObject.__init__(self)

        # 数据格式: [ (time, open, close, low, high),...]
        self.data = data
        # 只重画部分图形，大大提高界面更新速度
        self.setFlag(self.ItemUsesExtendedStyleOption)
        # 画笔和画刷
        w = 0.4
        self.offset = 0
        self.low = 0
        self.high = 1
        self.picture = QtGui.QPicture()
        self.pictures = []
        self.bPen = pg.mkPen(color=(0, 240, 240, 255), width=w * 2)
        self.bBrush = pg.mkBrush((0, 240, 240, 255))
        self.rPen = pg.mkPen(color=(255, 60, 60, 255), width=w * 2)
        self.rBrush = pg.mkBrush((255, 60, 60, 255))
        self.rBrush.setStyle(Qt.NoBrush)
        # 刷新K线
        self.generatePicture(self.data)

    # 画K线
    # ----------------------------------------------------------------------
    def generatePicture(self, data=None, redraw=False):
        """重新生成图形对象"""
        # 重画或者只更新最后一个K线
        if redraw:
            self.pictures = []
        elif self.pictures:
            self.pictures.pop()
        w = 0.4
        bPen = self.bPen
        bBrush = self.bBrush
        rPen = self.rPen
        rBrush = self.rBrush
        low, high = (data[0]['low'], data[0]['high']) if len(data) > 0 else (0, 1)
        for (t, open0, close0, low0, high0) in data:
            if t >= len(self.pictures):

                tShift = t

                low, high = (min(low, low0), max(high, high0))
                picture = QtGui.QPicture()
                p = QtGui.QPainter(picture)
                # # 下跌蓝色（实心）, 上涨红色（空心）
                pen, brush, pmin, pmax = (bPen, bBrush, close0, open0) \
                    if open0 > close0 else (rPen, rBrush, open0, close0)
                p.setPen(pen)
                p.setBrush(brush)
                # 画K线方块和上下影线
                if pmin > low0:
                    p.drawLine(QtCore.QPointF(tShift, low0), QtCore.QPointF(tShift, pmin))
                if high0 > pmax:
                    p.drawLine(QtCore.QPointF(tShift, pmax), QtCore.QPointF(tShift, high0))
                p.drawRect(QtCore.QRectF(tShift - w, open0, w * 2, close0 - open0))
                # if open0 == close0:
                #     p.drawRect(QtCore.QPointF(tShift - w, open0), QtCore.QPointF(tShift + w, close0))
                # else:
                #     p.drawRect(QtCore.QRectF(tShift - w, open0, w * 2, close0 - open0))
                # if pmin > low0:
                #     p.drawLine(QtCore.QPointF(tShift, low0), QtCore.QPointF(tShift, pmin))
                # if high0 > pmax:
                #     p.drawLine(QtCore.QPointF(tShift, pmax), QtCore.QPointF(tShift, high0))
                p.end()

                self.pictures.append(picture)
        self.low, self.high = low, high

    # 手动重画
    # ----------------------------------------------------------------------
    def update(self):
        if not self.scene() is None:
            self.scene().update()

    # 自动重画
    # ----------------------------------------------------------------------
    def paint(self, p, o, w):
        rect = o.exposedRect
        xmin, xmax = (max(0, int(rect.left())), min(len(self.pictures), int(rect.right())))

        [p.drawPicture(0, 0, pic) for pic in self.pictures[xmin:xmax]]

    # 定义边界
    # ----------------------------------------------------------------------
    def boundingRect(self):
        return QtCore.QRectF(0, self.low, len(self.pictures), (self.high - self.low))









class KLineWidget(Ui_Form):
    """用于显示价格走势图"""

    # 保存K线数据的列表和Numpy Array对象
    listBar = []
    listVol = []
    listHigh = []
    listLow = []
    listSig = []
    listOpenInterest = []
    arrows = []

    # 是否完成了历史数据的读取
    initCompleted = False    
    
    def __init__(self, parent = None, name=None):
        self.parent = parent
        self.name = name        
        super(KLineWidget, self).__init__()
        self.setupUi(Form)
        
        # 当前序号
        self.index = None  # 下标
        self.countK = 60  # 显示的Ｋ线范围
        self.oldsize=0#rectd的hieght

        # 缓存数据
        self.datas = []
        self.listBar = []
        self.listVol = []
        self.listHigh = []
        self.listLow = []
        self.listSig = []
        self.listOpenInterest = []
        self.arrows = []
        self.sars = []
        self.sarDatas = None

        self.curveOI1=None
        self.curveOI2=None
        self.curveOI3=None

        self.upperline = []
        self.midline= []
        self.downline = []

        # 所有K线上信号图
        self.allColor = deque(['blue', 'green', 'yellow', 'white'])
        self.sigData = {}
        self.sigColor = {}
        self.sigPlots = {}

        # 初始化完成
        self.initCompleted = False

        # 调用函数
        self.initUi()

    def addUpper(self,up):
        self.upperline = up
        self.curveOI1 = pg.PlotDataItem()
        self.curveOI1.setData(y=self.upperline)

        if self.curveOI1:
            self.pwKL.removeItem(self.curveOI1)

        self.pwKL.addItem(self.curveOI1)


    def addMid(self,mid):
        if self.curveOI2:
            self.pwKL.removeItem(self.curveOI2)
        self.midline = mid
        self.curveOI2 = pg.PlotDataItem()
        self.curveOI2.setData(y=self.midline)
        self.pwKL.addItem(self.curveOI2)

    def addDown(self,down):
        if self.curveOI3:
            self.pwKL.removeItem(self.curveOI3)

        self.downline = down
        self.curveOI3 = pg.PlotDataItem()
        self.curveOI3.setData(y=self.downline)
        self.pwKL.addItem(self.curveOI3)  
        
    # ----------------------------------------------------------------------
    #  初始化相关
    # ----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        # 主图
        self.pw = pg.PlotWidget()
        # 界面布局
        self.lay_KL.setContentsMargins(10, 10, 10, 10)
        self.lay_KL.setSpacing(0)
        self.lay_KL.setBorder(color=(255, 255, 255, 255), width=0.8)
        self.lay_KL.setZValue(0)
        self.lay_KL.setMinimumHeight(140)
        self.KLtitle = self.lay_KL.addLabel(u'')
        self.pw.setCentralItem(self.lay_KL)
        # 设置横坐标
        xdict = {}
        self.axisTime = MyStringAxis(xdict, orientation='bottom')
        # 初始化子图
        self.initplotKline()
        self.initplotVol()
        self.initplotOI()
        # 注册十字光标
        self.crosshair = Crosshair(self.pw, self)
        # 设置界面
        self.vb = QtWidgets.QVBoxLayout()
        self.vb.addWidget(self.pw)
        self.setLayout(self.vb)
        # 初始化完成
        self.initCompleted = True
        self.oldsize=self.rect().height()

        self.customBox = {}

    # ----------------------------------------------------------------------
    def makePI(self, name):
        """生成PlotItem对象"""
        vb = CustomViewBox(self)
        plotItem = pg.PlotItem(viewBox=vb, name=name, axisItems={'bottom': self.axisTime})
        plotItem.setMenuEnabled(False)
        plotItem.setClipToView(True)
        plotItem.hideAxis('left')
        plotItem.showAxis('right')
        plotItem.setDownsampling(mode='peak')
        plotItem.setRange(xRange=(0, 1), yRange=(0, 1))
        plotItem.getAxis('right').setWidth(60)
        plotItem.getAxis('right').setStyle(tickFont=QFont("Roman times", 10, QFont.Bold))
        plotItem.getAxis('right').setPen(color=(255, 255, 255, 255), width=0.8)
        plotItem.showGrid(True, True)
        plotItem.hideButtons()

        return plotItem

    # ----------------------------------------------------------------------
    def initplotVol(self):
        """初始化成交量子图"""
        self.pwVol = self.makePI('PlotVol' + self.name)
        self.volume = CandlestickItem(self.listVol)
        self.pwVol.addItem(self.volume)
        self.pwVol.setMaximumHeight((self.rect().height()-30)/4)
        self.pwVol.setMinimumHeight(12)
        self.pwVol.setXLink('PlotOI' + self.name)
        self.pwVol.hideAxis('bottom')
        self.lay_KL.nextRow()
        self.lay_KL.addItem(self.pwVol)
        self.lay_KL.adjustSize()


    # ----------------------------------------------------------------------
    def initplotKline(self):
        """初始化K线子图"""
        self.pwKL = self.makePI('PlotKL' + self.name)
        self.candle = CandlestickItem(self.listBar)
        self.pwKL.addItem(self.candle)
        self.pwKL.setXLink('PlotOI' + self.name)
        self.pwKL.hideAxis('bottom')
        self.pwKL.setMinimumHeight((self.rect().height()-30)/3)

        self.lay_KL.nextRow()
        self.lay_KL.addItem(self.pwKL)

    # ----------------------------------------------------------------------
    def initplotOI(self):
        """初始化持仓量子图"""
        self.pwOI = self.makePI('PlotOI' + self.name)
        self.curveOI = self.pwOI.plot()
        self.pwOI.setMaximumHeight((self.rect().height() - 30) / 4)
        self.pwOI.setMinimumHeight(20)

        self.lay_KL.nextRow()
        self.lay_KL.addItem(self.pwOI)

    # ----------------------------------------------------------------------
    #  画图相关
    # ----------------------------------------------------------------------
    def plotVol(self, redraw=False, xmin=0, xmax=-1):
        """重画成交量子图"""
        if self.initCompleted:
            self.volume.generatePicture(self.listVol[xmin:xmax], redraw)  # 画成交量子图

    # ----------------------------------------------------------------------
    def plotKline(self, redraw=False, xmin=0, xmax=-1):
        """重画K线子图"""
        if self.initCompleted:
            self.candle.generatePicture(self.listBar[xmin:xmax], redraw)  # 画K线
            self.plotMark()  # 显示开平仓信号位置

    # ----------------------------------------------------------------------
    def plotOI(self, xmin=0, xmax=-1):
        """重画持仓量子图"""
        if self.initCompleted:
            # self.curveOI.setData(self.listOpenInterest[xmin:xmax]+[0], symbol='o', name="OpenInterest")
            self.curveOI.setData(self.listOpenInterest[xmin:xmax] + [0],
                                 name="OpenInterest" + self.name)  # 去除symbol='o'

    def updateIndicatorSar(self, sarDatas, startIndex):
        """更新sar指标   startIndex  从0到 len -1"""
        if len(sarDatas) == 0:
            return
        self.sarDatas=sarDatas

        while (len(self.sars) > (startIndex - 1)):
            sar = self.sars[-1]
            self.pwKL.removeItem(sar)
            self.sars.remove(sar)

        for i in range(startIndex, len(sarDatas)):
            arrow = pg.ArrowItem(pos=(i, sarDatas[i]), angle=90, tipAngle=5, headLen=2, tailWidth=4, pen={'width': 1},
                                 brush=(0, 0, 255))

            defaultOpts = {
                'pxMode': True,
                'angle': -150,  ## If the angle is 0, the arrow points left
                'pos': (0, 0),
                'headLen': 10,
                'tipAngle': 10,
                'baseAngle': 0,
                'tailLen': None,
                'tailWidth': 3,
                'pen': (200, 200, 200),
                'brush': (255, 0, 0),
            }
            # arrow.setStyle(defaultOpts)

            self.pwKL.addItem(arrow)
            self.sars.append(arrow)

    def addIndicatorSar(self, sarDatas):
        """增加sar指标"""
        if len(sarDatas) == 0:
            return
        self.sarDatas = sarDatas
        for sar in self.sars:
            self.pwKL.removeItem(sar)
        # 画信号
        for i in range(len(sarDatas)):
            # arrow = pg.ArrowItem(pos=(i, sarDatas[i]),headLen=10,  angle=90, brush=(0, 0, 255))
            arrow = pg.ArrowItem(pos=(i, sarDatas[i]), angle=90, tipAngle=5, headLen=2, tailWidth=4, pen={'width': 1},
                                 brush=(0, 0, 255))

            defaultOpts = {
                'pxMode': True,
                'angle': -150,  ## If the angle is 0, the arrow points left
                'pos': (0, 0),
                'headLen': 10,
                'tipAngle': 10,
                'baseAngle': 0,
                'tailLen': None,
                'tailWidth': 3,
                'pen': (200, 200, 200),
                'brush': (255, 0, 0),
            }
            # arrow.setStyle(defaultOpts)

            self.pwKL.addItem(arrow)
            self.sars.append(arrow)

    # ----------------------------------------------------------------------
    def addSig(self, sig):
        """新增信号图"""
        if sig in self.sigPlots:
            self.pwKL.removeItem(self.sigPlots[sig])
        self.sigPlots[sig] = self.pwKL.plot()
        self.sigColor[sig] = self.allColor[0]
        self.allColor.append(self.allColor.popleft())

    # ----------------------------------------------------------------------
    def showSig(self, datas):
        """刷新信号图"""
        for sig in self.sigPlots:
            self.sigData[sig] = datas[sig]

        [self.sigPlots[sig].setData(datas[sig], pen=self.sigColor[sig][0], name=sig) \
         for sig in self.sigPlots]  # if sig in datas]

    # ----------------------------------------------------------------------
    def plotMark(self):
        """显示开平仓信号"""
        # 检查是否有数据
        if len(self.datas) == 0:
            return
        for arrow in self.arrows:
            self.pwKL.removeItem(arrow)
        # 画买卖信号
        for i in range(len(self.listSig)):
            # 无信号
            if self.listSig[i] == None:
                continue
            # 买信号
            elif self.listSig[i] != None:
                direction = self.listSig[i]["direction"]
                offset = self.listSig[i]["offset"]
                price = self.listSig[i]["price"]

                if direction == "空" and offset == "开仓":
                    # arrow = pg.ArrowItem(pos=(i, price),  angle=-90, brush=(255, 0, 0))
                    arrow = pg.ArrowItem(pos=(i, price), angle=180, tipAngle=60, headLen=8, tailLen=3, tailWidth=5,
                                         pen={'color': 'w', 'width': 1}, brush='r')
                elif direction == "多" and offset == "开仓":
                    # arrow = pg.ArrowItem(pos=(i, price),  angle=90, brush=(255, 0, 0))
                    arrow = pg.ArrowItem(pos=(i, price), angle=180, tipAngle=60, headLen=8, tailLen=3, tailWidth=5,
                                         pen={'color': 'w', 'width': 1}, brush='b')
                elif direction == "空" and offset == "平仓":
                    # arrow = pg.ArrowItem(pos=(i, price),  angle=-90, brush=(0, 0, 255))
                    arrow = pg.ArrowItem(pos=(i, price), angle=0, tipAngle=40, headLen=8, tailLen=None, tailWidth=8,
                                         pen={'color': 'w', 'width': 1}, brush='y')
                elif direction == "多" and offset == "平仓":
                    # arrow = pg.ArrowItem(pos=(i, price),  angle=90, brush=(0, 0, 255))
                    arrow = pg.ArrowItem(pos=(i, price), angle=0, tipAngle=40, headLen=8, tailLen=None, tailWidth=8,
                                         pen={'color': 'w', 'width': 1}, brush='y')
            self.pwKL.addItem(arrow)
            self.arrows.append(arrow)

    # ----------------------------------------------------------------------
    def updateAll(self):
        """
        手动更新所有K线图形，K线播放模式下需要
        """
        datas = self.datas
        self.volume.update()
        self.candle.update()

        def update(view, low, high):
            vRange = view.viewRange()
            xmin = max(0, int(vRange[0][0]))
            xmax = max(0, int(vRange[0][1]))
            xmax = min(xmax, len(datas))
            if len(datas) > 0 and xmax > xmin:
                ymin = min(datas[xmin:xmax][low])
                ymax = max(datas[xmin:xmax][high])
                if  ymin and ymax:
                   view.setRange(yRange=(ymin, ymax))
            else:
                view.setRange(yRange=(0, 1))

        update(self.pwKL.getViewBox(), 'low', 'high')
        update(self.pwVol.getViewBox(), 'volume', 'volume')
        #update(self.pwOI.getViewBox(), 'openInterest', 'openInterest')
        update(self.curveOI.getViewBox(), 'openInterest', 'openInterest')

    # ----------------------------------------------------------------------
    def plotAll(self, redraw=True, xMin=0, xMax=-1):
        """
        重画所有界面
        redraw ：False=重画最后一根K线; True=重画所有
        xMin,xMax : 数据范围
        """
        # xMax = len(self.datas) if xMax < 0 else xMax
        # self.countK = xMax-xMin
        # self.index = int((xMax+xMin)/2)
        if redraw:
            xmax = len(self.datas) if xMax < 0 else xMax
            xmin=max(0,xmax-self.countK)
            self.index = int((xmax + xmin) / 2)
        self.pwOI.setLimits(xMin=xMin, xMax=xMax)
        self.pwKL.setLimits(xMin=xMin, xMax=xMax)
        self.pwVol.setLimits(xMin=xMin, xMax=xMax)
        self.plotKline(redraw, xMin, xMax)  # K线图
        self.plotVol(redraw, xMin, xMax)  # K线副图，成交量
        self.plotOI(0, len(self.datas))  # K线副图，持仓量
        self.refresh()

    def refreshHeight(self):
       # super.__init__(QResizeEvent)
        # 如果窗口最大化，不修改比例，防御性设计
        # if self.isMaximized():
        #     return
       if len(self.datas)!=0:
            height =self.rect().height()
            if height!=self.oldsize:
                self.oldsize=height
                height=(height-30)/4

                self.pwKL.setMinimumHeight(height * 2-24)
                self.pwVol.setMaximumHeight(height)
                self.pwVol.setMinimumHeight(12)
                self.pwOI.setMaximumHeight(height)
                self.pwOI.setMinimumHeight(12)

                #print height


    # ----------------------------------------------------------------------
    def refresh(self):
        """
        刷新三个子图的现实范围
        """
        datas = self.datas
        minutes = int(self.countK / 2)
        xmin = max(0, self.index - minutes)
        xmax = xmin + 2 * minutes
        self.pwOI.setRange(xRange=(xmin, xmax))
        self.pwKL.setRange(xRange=(xmin, xmax))
        self.pwVol.setRange(xRange=(xmin, xmax))

    # ----------------------------------------------------------------------
    #  快捷键相关
    # ----------------------------------------------------------------------
    def onNxt(self):
        """跳转到下一个开平仓点"""
        if len(self.listSig) > 0 and not self.index is None:
            datalen = len(self.listSig)
            self.index += 1
            while self.index < datalen and self.listSig[self.index] == 0:
                self.index += 1
            self.refresh()
            x = self.index
            y = self.datas[x]['close']
            self.crosshair.signal.emit((x, y))

    # ----------------------------------------------------------------------
    def onPre(self):
        """跳转到上一个开平仓点"""
        if len(self.listSig) > 0 and not self.index is None:
            self.index -= 1
            while self.index > 0 and self.listSig[self.index] == 0:
                self.index -= 1
            self.refresh()
            x = self.index
            y = self.datas[x]['close']
            self.crosshair.signal.emit((x, y))

    # ----------------------------------------------------------------------
    def onDown(self):
        """放大显示区间"""
        self.countK = min(len(self.datas), int(self.countK * 1.2) + 1)
        self.refresh()
        if len(self.datas) > 0:
            x = self.index - self.countK / 2 + 2 if int(
                self.crosshair.xAxis) < self.index - self.countK / 2 + 2 else int(self.crosshair.xAxis)
            x = self.index + self.countK / 2 - 2 if x > self.index + self.countK / 2 - 2 else x
            x=min(x,len(self.datas)-1)
            y = self.datas[x][2]
            # y = self.datas[x]['close']
            self.crosshair.signal.emit((x, y))

    # ----------------------------------------------------------------------
    def onUp(self):
        """缩小显示区间"""
        # self.countK = max(3,int(self.countK/1.2)-1)
        self.countK = max(20, int(self.countK / 1.2) - 1)  # 最小显示k线范围20
        self.refresh()
        if len(self.datas) > 0:
            x = self.index - self.countK / 2 + 2 if int(
                self.crosshair.xAxis) < self.index - self.countK / 2 + 2 else int(self.crosshair.xAxis)
            x = self.index + self.countK / 2 - 2 if x > self.index + self.countK / 2 - 2 else x
            x = min(x, len(self.datas)-1)
            y = self.datas[x]['close']
            self.crosshair.signal.emit((x, y))

    # ----------------------------------------------------------------------
    def onLeft(self):
        """向左移动"""
        if len(self.datas) > 0 and int(self.crosshair.xAxis) > 2:
            x = int(self.crosshair.xAxis) - 1
            y = self.datas[x]['close']
            if x <= self.index - self.countK / 2 + 2 and self.index > 1:
                self.index -= 1
                self.refresh()
            self.crosshair.signal.emit((x, y))

    # ----------------------------------------------------------------------
    def onRight(self):
        """向右移动"""
        if len(self.datas) > 0 and int(self.crosshair.xAxis) < len(self.datas) - 1:
            x = int(self.crosshair.xAxis) + 1
            y = self.datas[x]['close']
            if x >= self.index + int(self.countK / 2) - 2:
                self.index += 1
                self.refresh()
            self.crosshair.signal.emit((x, y))

    # ----------------------------------------------------------------------
    # 界面回调相关
    # ----------------------------------------------------------------------
    def onPaint(self):
        """界面刷新回调"""
        view = self.pwKL.getViewBox()
        vRange = view.viewRange()
        # xmin = max(0,int(vRange[0][0]))
        # xmax = max(0,int(vRange[0][1]))
        # self.index  = int((xmin+xmax)/2)+1

    # ----------------------------------------------------------------------
    def resignData(self, datas):
        """更新数据，用于Y坐标自适应"""
        self.crosshair.datas = datas

        def viewXRangeChanged(low, high, self):
            vRange = self.viewRange()
            xmin = max(0, int(vRange[0][0]))
            xmax = max(0, int(vRange[0][1]))
            xmax = min(xmax, len(datas))
            if len(datas) > 0 and xmax > xmin:
                ymin = min(datas[xmin:xmax][low])
                ymax = max(datas[xmin:xmax][high])
                if ymin and ymax:
                   self.setRange(yRange=(ymin, ymax))
            else:
                self.setRange(yRange=(0, 1))

        view = self.pwKL.getViewBox()
        view.sigXRangeChanged.connect(partial(viewXRangeChanged, 'low', 'high'))
        view = self.pwVol.getViewBox()
        view.sigXRangeChanged.connect(partial(viewXRangeChanged, 'volume', 'volume'))

        view = self.pwOI.getViewBox()
        view.sigXRangeChanged.connect(partial(viewXRangeChanged, 'openInterest', 'openInterest'))

    # ----------------------------------------------------------------------
    # 数据相关
    # ----------------------------------------------------------------------
    def clearData(self):
        """清空数据"""
        # 清空数据，重新画图
        self.time_index = []
        self.listBar = []
        self.listVol = []
        self.listLow = []
        self.listHigh = []
        self.listOpenInterest = []
        self.listSig = []
        self.sigData = {}
        self.arrows = []
        self.datas = None
        self.sarDatas=None

    # ----------------------------------------------------------------------
    def updateSig(self, sig):
        """刷新买卖信号"""
        self.listSig = sig
        self.plotMark()
    # ----------------------------------------------------------------------
    def onBar(self, bar, nWindow=20):
        """
        新增K线数据,K线播放模式
        nWindow : 最大数据窗口
        """
        # 是否需要更新K线
        newBar = False if len(self.datas) > 0 and bar.datetime == self.datas[-1].datetime else True
        nrecords = len(self.datas) if newBar else len(self.datas) - 1
        bar.openInterest = np.random.randint(0,
                                             3) if bar.openInterest == np.inf or bar.openInterest == -np.inf else bar.openInterest
        recordVol = (nrecords, bar.volume, 0, 0, bar.volume) if bar.close < bar.open else (
        nrecords, 0, bar.volume, 0, bar.volume)
        if newBar and any(self.datas):
            self.datas.resize(nrecords + 1, refcheck=0)
            self.listBar.resize(nrecords + 1, refcheck=0)
            self.listVol.resize(nrecords + 1, refcheck=0)
        elif any(self.datas):
            self.listLow.pop()
            self.listHigh.pop()
            self.listOpenInterest.pop()
        if any(self.datas):
            self.datas[-1] = (bar.datetime, bar.open, bar.close, bar.low, bar.high, bar.volume, bar.openInterest)
            self.listBar[-1] = (nrecords, bar.open, bar.close, bar.low, bar.high)
            self.listVol[-1] = recordVol
        else:
            self.datas = np.rec.array(
                [(datetime, bar.open, bar.close, bar.low, bar.high, bar.volume, bar.openInterest)], \
                names=('datetime', 'open', 'close', 'low', 'high', 'volume', 'openInterest'))
            self.listBar = np.rec.array([(nrecords, bar.open, bar.close, bar.low, bar.high)], \
                                        names=('datetime', 'open', 'close', 'low', 'high'))
            self.listVol = np.rec.array([recordVol], names=('datetime', 'open', 'close', 'low', 'high'))
            self.resignData(self.datas)
        self.axisTime.update_xdict({nrecords: bar.datetime})
        self.listLow.append(bar.low)
        self.listHigh.append(bar.high)
        self.listOpenInterest.append(bar.openInterest)
        # if newBar:
        #     xMax = nrecords + 1
        #     xMin = max(0, xMax - self.countK)  # 最小显示区间
        #     self.index=int(xMax+xMin)/2

        # if self.pwKL.getViewBox().mousePress == True:
        # print("sssssssssss")

        # if self.pwKL.getViewBox().mousePress == False: ##self.mousePress==false,不在执行刷新操作



        xMax = self.index + self.countK
        xMin = self.index - self.countK
        #xMin=(0,xMin)
        if xMin<0:
            xMin=0

        if not newBar:
            self.updateAll()

        self.plotAll(False, xMin, xMax)
        self.crosshair.signal.emit((None, None))

    # ----------------------------------------------------------------------
    def loadData(self, datas):
        """
        载入pandas.DataFrame数据
        datas : 数据格式，cols : datetime, open, close, low, high
        """
        # 设置中心点时间
        self.index = 0

        # 绑定数据，更新横坐标映射，更新Y轴自适应函数，更新十字光标映射
        datas['time_int'] = np.array(range(len(datas.index)))
        self.datas = datas[['open', 'close', 'low', 'high', 'volume', 'openInterest']].to_records()
        self.axisTime.xdict = {}
        xdict = dict(enumerate(datas.index.tolist()))
        self.axisTime.update_xdict(xdict)
        self.resignData(self.datas)
        # 更新画图用到的数据
        self.listBar = datas[['time_int', 'open', 'close', 'low', 'high']].to_records(False)
        self.listHigh = list(datas['high'])
        self.listLow = list(datas['low'])
        self.listOpenInterest = list(datas['openInterest'])
        # 成交量颜色和涨跌同步，K线方向由涨跌决定
        datas0 = pd.DataFrame()
        datas0['open'] = datas.apply(lambda x: 0 if x['close'] >= x['open'] else x['volume'], axis=1)
        datas0['close'] = datas.apply(lambda x: 0 if x['close'] < x['open'] else x['volume'], axis=1)
        datas0['low'] = datas0['open']
        datas0['high'] = datas0['close']
        datas0['time_int'] = np.array(range(len(datas.index)))
        self.listVol = datas0[['time_int', 'open', 'close', 'low', 'high']].to_records(False)
        # 调用画图函数
        self.plotAll(True, 0, len(self.datas))

    def loadDataBar(self, datas):
        """
        载入pandas.DataFrame数据
        datas : 数据格式，'symbol','vtSymbol','exchange','open','high','low','close','date','time1','datetime','volume','openInterest'
        """
        print(datas)
        self.index = 0

        # 绑定数据，更新横坐标映射，更新Y轴自适应函数，更新十字光标映射
        datas['time_int'] = np.array(range(len(datas.index)))

        self.datas = datas[['datetime', 'open', 'close', 'low', 'high', 'volume', 'openInterest']].to_records(False)
        # self.datas = datas[['symbol','vtSymbol','exchange','open','high','low','close','date','time1','datetime','volume','openInterest']].to_records()
        self.axisTime.xdict = {}
        # xdict = dict(enumerate(datas.index.tolist()))
        xdict = dict(enumerate(datas['datetime'].tolist()))
        self.axisTime.update_xdict(xdict)
        self.resignData(self.datas)
        # 更新画图用到的数据
        self.listBar = datas[['time_int', 'open', 'close', 'low', 'high']].to_records(False)
        self.listHigh = list(datas['high'])
        self.listLow = list(datas['low'])
        self.listOpenInterest = list(datas['openInterest'])
        # 成交量颜色和涨跌同步，K线方向由涨跌决定
        datas0 = pd.DataFrame()
        datas0['open'] = datas.apply(lambda x: 0 if x['close'] >= x['open'] else x['volume'], axis=1)
        datas0['close'] = datas.apply(lambda x: 0 if x['close'] < x['open'] else x['volume'], axis=1)
        datas0['low'] = datas0['open']
        datas0['high'] = datas0['close']
        datas0['time_int'] = np.array(range(len(datas.index)))
        self.listVol = datas0[['time_int', 'open', 'close', 'low', 'high']].to_records(False)
        # 调用画图函数
        self.plotAll(True, 0, len(self.datas))

    ##VtBarData 结构
    def loadDataBarArray(self, record):
        txtData = pd.DataFrame.from_records(record, index="datetime")
        # txtData = txtData.rename(columns = {0:'symbol', 1:"vtSymbol",2:"exchange",3:"open",4:"high",5:"low",6:"close",7:"date",8:"time",9:"datetime",10:"volume",11:"openInterest"})

        self.loadData(txtData)        
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = KLineWidget()
    Form.show()
    sys.exit(app.exec_())
