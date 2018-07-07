""" Run the rocket game on Qt.
"""

import time
import math

from qtpy import QtWidgets, QtCore, QtGui

from rocket import BaseRocketGame


class QtRocketGame(BaseRocketGame, QtWidgets.QWidget):
    """ Rocket game with Qt providing a drawing canvas and user input.
    """
    
    def __init__(self):
        QtWidgets.QWidget.__init__(self, None)
        BaseRocketGame.__init__(self)
        self.setWindowTitle("Rocket, written in Rust, compiled to WASM, running in Python, with Qt")
        self.resize(640, 480)
        
        self._lasttime = time.time()
        self._highscore = 0
    
    def run(self):
        self.show()
        QtWidgets.qApp.exec_()
    
    def paintEvent(self, event):
        self._painter = QtGui.QPainter()
        self._painter.begin(self)
        self._painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        progress = time.time() - self._lasttime
        self._lasttime = time.time()
        self.wam.exports.update(progress)
        self.wam.exports.draw()
        
        self._painter.end()
        self.update()  # Request a new paint event
    
    ## Events going into the WASM module
    
    def resizeEvent(self, event):
        self.wam.exports.resize(self.width(), self.height())
    
    def keyPressEvent(self, event):
        self._toggleKey(event, True)
    
    def keyReleaseEvent(self, event):
        self._toggleKey(event, False)
    
    def _toggleKey(self, event, b):
        if event.key() == QtCore.Qt.Key_Space:
            self.wam.exports.toggle_shoot(b)
        elif event.key() == QtCore.Qt.Key_Left:
            self.wam.exports.toggle_turn_left(b)
        elif event.key() == QtCore.Qt.Key_Right:
            self.wam.exports.toggle_turn_right(b)
        elif event.key() == QtCore.Qt.Key_Up:
            self.wam.exports.toggle_boost(b)
    
    ## Events generated by WASM module
    
    def wasm_clear_screen(self) -> None:  # [] -> []
        pass  # not needed, we start with a blanc canvas each iteration
    
    def wasm_draw_bullet(self, x: float, y: float) -> None:  # [(0, 'f64'), (1, 'f64')] -> []
        self._painter.setBrush(QtGui.QColor('#0f0'))
        self._painter.drawEllipse(x, y, 3, 3)
    
    def wasm_draw_enemy(self, x: float, y: float) -> None:  # [(0, 'f64'), (1, 'f64')] -> []
        self._painter.setBrush(QtGui.QColor('#ff0'))
        self._painter.drawEllipse(x, y, 14, 14)
    
    def wasm_draw_particle(self, x: float, y: float, a: float) -> None: # [(0, 'f64'), (1, 'f64'), (2, 'f64')] -> []
        self._painter.setBrush(QtGui.QColor('#f04'))
        self._painter.drawEllipse(x, y, 2, 2)
    
    def wasm_draw_player(self, x: float, y: float, a: float) -> None:  # [(0, 'f64'), (1, 'f64'), (2, 'f64')] -> []
        p = QtGui.QPainterPath()
        self._painter.save()
        self._painter.translate(x, y)
        self._painter.rotate(a*180/math.pi-90)
        self._painter.translate(-x, -y)
        p.moveTo(x, y + 12); p.lineTo(x - 6, y - 6); p.lineTo(x + 6, y - 6); p.lineTo(x, y + 12)
        self._painter.fillPath(p, QtGui.QBrush(QtGui.QColor("#00f")))
        self._painter.restore()
    
    def wasm_draw_score(self, score: float) -> None:  #  env.draw_score:    [(0, 'f64')] -> []
        score = int(score)
        self._highscore = max(self._highscore, score)
        self._painter.drawText(0, 20, f'Score: {score}, HighScore: {self._highscore}')


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    game = QtRocketGame()
    game.run()
