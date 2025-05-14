from PySide6.QtWidgets import (QApplication, QStyleFactory, QMainWindow, QWidget, QVBoxLayout,
							   QPushButton, QHBoxLayout, QStackedWidget, QFrame, QLineEdit, QMessageBox, QComboBox,
							   QSlider, QCheckBox, QGroupBox, QCalendarWidget, QLabel, QFileDialog, QPlainTextEdit,
							   QSystemTrayIcon, QMenu,  QListWidget, QListWidgetItem, QSpacerItem,
							   QSizePolicy, QFrame, QDateTimeEdit, QGraphicsDropShadowEffect,
              QCalendarWidget,
QScrollBar,
    QStyledItemDelegate,
    QTableView,
    QInputDialog,
    QHeaderView,
    QScrollArea,QDialog, QTextEdit, QStyleOptionViewItem)
from PySide6.QtCore import (QPropertyAnimation, QEasingCurve, Qt, QDate, QTime, QDateTime, Signal, Slot, QSize, QObject,
							QPoint, QTimer, QEvent, QPointF, QPersistentModelIndex, QRect)
from PySide6.QtGui import QFont, QIcon, QAction, QPixmap, QColor, QLinearGradient, QPainter, QMouseEvent,\
QPainter, QFontMetrics, QTextCharFormat, QPen, QCursor
import logging
import sys
import os
import json
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import platform
import time
from collections import defaultdict
