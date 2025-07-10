from PySide6.QtWidgets import (QApplication, QStyleFactory, QMainWindow, QWidget, QVBoxLayout,
							QPushButton, QHBoxLayout, QStackedWidget, QFrame, QLineEdit, QMessageBox, QComboBox,
							QSlider, QCheckBox, QGroupBox, QCalendarWidget, QLabel, QFileDialog, QPlainTextEdit,
							QSystemTrayIcon, QMenu, QListWidget, QListWidgetItem, QSpacerItem,
							QSizePolicy, QFrame, QDateTimeEdit, QGraphicsDropShadowEffect, QCalendarWidget,
							QScrollBar, QStyledItemDelegate, QTableView, QInputDialog, QHeaderView, QScrollArea,
							QDialog, QTextEdit, QStyleOptionViewItem, QStyle, QAbstractItemView, QGraphicsSimpleTextItem,
          					QGraphicsView, QGraphicsScene, QGraphicsRectItem, QSplitter, QGraphicsLineItem, QGraphicsItemGroup,QToolTip,QGraphicsItem,QDateEdit)
from PySide6.QtCore import (QPropertyAnimation, QEasingCurve, Qt, QDate, QTime, QDateTime, Signal, Slot, QSize, QObject,
							QPoint, QTimer, QEvent, QPointF, QPersistentModelIndex, QRect, QModelIndex, QFile, QRectF,
							QFileInfo, QLineF,QCoreApplication)
from PySide6.QtGui import (QIcon, QAction, QPixmap, QColor, QLinearGradient, QPainter, QMouseEvent,
						   QPainter, QFontMetrics, QTextCharFormat, QPen, QCursor, QFont, QPalette, QBrush,
						   QImageReader,QShortcut,QKeySequence, QTextOption)
import logging
import sys
import os
import tkinter as tk
from tkinter import filedialog
from datetime import datetime, timedelta
import platform
import time
from collections import defaultdict
import json
