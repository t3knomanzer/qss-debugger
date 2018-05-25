# *********************************************************************
# +++ IMPORTS
# *********************************************************************
import os
import subprocess
import hashlib

from PySide import QtGui, QtCore


# *********************************************************************
# +++ CLASS
# *********************************************************************
class VisualTreePainter(QtGui.QWidget):
    # =====================================================================
    # +++ CONSTRUCTOR
    # =====================================================================
    def __init__(self, parent=None):
        super(VisualTreePainter, self).__init__(parent)
        self._current_items = []

        # -- Style
        self._color_widget_rect = QtGui.QColor(255, 0, 0, 64)
        self._color_widget_content_rect = QtGui.QColor(255, 255, 255, 64)

        self._brush_widget_rect = QtGui.QBrush(self._color_widget_rect)
        self._brush_widget_content_rect = QtGui.QBrush(self._color_widget_content_rect)

        self._text_font = QtGui.QFont("Arial", 8)
        self._margin_label_height = 24

        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

    # ====================================================================
    # +++ PROPERTIES
    # =====================================================================
    @property
    def current_items(self):
        return self._current_items

    @current_items.setter
    def current_items(self, items):
        self._current_items = items
        self.update()

    # ====================================================================
    # +++ OVERRIDES
    # =====================================================================
    def paintEvent(self, event):
        self.setFixedSize(self.parent().size())

        painter = QtGui.QPainter(self)
        painter.setPen(QtCore.Qt.NoPen)

        for item in self._current_items:
            if not isinstance(item, QtGui.QWidget):
                return

            # Reset painter
            painter.setPen(QtCore.Qt.NoPen)

            # Widget Rect
            # This property holds the internal geometry of the widget excluding any window frame.
            # The rect property equals:
            # PySide.QtCore.QRect (0, 0, PySide.QtGui.QWidget.width() , PySide.QtGui.QWidget.height() ).
            item_rect = QtCore.QRect(item.rect())
            top_left = item.mapTo(self.parent(), item_rect.topLeft())
            bottom_right = item.mapTo(self.parent(), item_rect.bottomRight())

            item_rect.setTopLeft(top_left)
            item_rect.setBottomRight(bottom_right)

            painter.setBrush(self._brush_widget_rect)
            painter.drawRect(item_rect)

            # Content Rect
            # Returns the area inside the widget's margins.
            content_rect = QtCore.QRect(item.contentsRect())
            top_left = item.mapTo(self.parent(), content_rect.topLeft())
            bottom_right = item.mapTo(self.parent(), content_rect.bottomRight())

            content_rect.setTopLeft(top_left)
            content_rect.setBottomRight(bottom_right)

            painter.setBrush(self._brush_widget_content_rect)
            painter.drawRect(content_rect)

            # Margin Indicators
            margin_pen = QtGui.QPen(QtGui.QColor(255, 255, 255))
            margin_pen.setWidth(1)

            painter.setPen(margin_pen)
            painter.setFont(self._text_font)

            # Left margin
            content_left = QtCore.QPointF(content_rect.left(), item_rect.center().y())
            item_left = QtCore.QPointF(item_rect.left(), item_rect.center().y())
            margin_left = abs(content_rect.left() - item_rect.left())

            label_left_rect = QtCore.QRectF(content_left.x() + 2,
                                            content_left.y() - self._margin_label_height / 2.0,
                                            content_rect.width() / 2.0,
                                            self._margin_label_height)

            painter.drawLine(item_left, content_left)
            painter.drawText(label_left_rect, QtCore.Qt.AlignVCenter, str(margin_left))

            # Right margin
            content_right = QtCore.QPointF(content_rect.right(), item_rect.center().y())
            item_right = QtCore.QPointF(item_rect.right(), item_rect.center().y())
            margin_right = abs(content_rect.right() - item_rect.right())

            label_right_rect = QtCore.QRectF(content_right.x() - content_rect.width() / 2.0 - 2,
                                             content_right.y() - self._margin_label_height / 2.0,
                                             content_rect.width() / 2.0,
                                             self._margin_label_height)

            painter.drawLine(item_right, content_right)
            painter.drawText(label_right_rect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight, str(margin_right))

            # Top margin
            content_top = QtCore.QPointF(item_rect.center().x(), content_rect.top())
            item_top = QtCore.QPointF(item_rect.center().x(), item_rect.top())
            margin_top = abs(content_rect.top() - item_rect.top())

            label_top_rect = QtCore.QRectF(content_top.x() - (content_rect.width() / 2.0) / 2.0,
                                           content_top.y() + 2.0,
                                           content_rect.width() / 2.0,
                                           self._margin_label_height)

            painter.drawLine(item_top, content_top)
            painter.drawText(label_top_rect, QtCore.Qt.AlignHCenter, str(margin_top))

            # Bottom margin
            content_bottom = QtCore.QPointF(item_rect.center().x(), content_rect.bottom())
            item_bottom = QtCore.QPointF(item_rect.center().x(), item_rect.bottom())
            margin_bottom = abs(content_rect.bottom() - item_rect.bottom())

            label_bottom_rect = QtCore.QRectF(content_bottom.x() - (content_rect.width() / 2.0) / 2.0,
                                              content_bottom.y() - self._margin_label_height - 2.0,
                                              content_rect.width() / 2.0,
                                              self._margin_label_height)

            painter.drawLine(item_bottom, content_bottom)
            painter.drawText(label_bottom_rect, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom, str(margin_bottom))

            # Draw Center
            line_length = 2.0
            vertical_x = item_rect.center().x()
            vertical_y0 = item_rect.center().y() - line_length
            vertical_y1 = item_rect.center().y() + line_length

            horizontal_y = item_rect.center().y()
            horizontal_x0 = item_rect.center().x() - line_length
            horizontal_x1 = item_rect.center().x() + line_length

            painter.drawLine(QtCore.QPointF(vertical_x, vertical_y0),
                             QtCore.QPointF(vertical_x, vertical_y1))

            painter.drawLine(QtCore.QPointF(horizontal_x0, horizontal_y),
                             QtCore.QPointF(horizontal_x1, horizontal_y))

        return
