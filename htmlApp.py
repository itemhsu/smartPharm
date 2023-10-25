import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, pyqtSlot, QTimer, QObject
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtTextToSpeech import QTextToSpeech
import sounddevice as sd
import wavio
import numpy as np
import whisper

class JavaScriptBridge(QObject):
    def __init__(self, parent=None):
        super(JavaScriptBridge, self).__init__(parent)
        self.main_window = parent

    @pyqtSlot()
    def onPress(self):
        self.main_window.onPress()

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()

        self.setWindowTitle("智能藥箱給藥系統")
        self.setGeometry(100, 100, 400, 200)
        self.channel = QWebChannel()
        self.browser = QWebEngineView(self)
        self.browser.page().setWebChannel(self.channel)
        self.js_bridge = JavaScriptBridge(self)
        self.channel.registerObject('pyObj', self.js_bridge)
        self.browser.load(QUrl.fromLocalFile(os.path.abspath("main.html")))
        self.setCentralWidget(self.browser)
        self.speech_engine = QTextToSpeech(self)
        self.model = whisper.load_model("base")

    @pyqtSlot()
    def onPress(self):
        self.speech_engine.say("請問你叫什麼名字？")
        QTimer.singleShot(2000, self.recordAudio)

    def get_name_from_input(self):
        js_code = 'document.getElementById("nameInput").value;'
        self.browser.page().runJavaScript(js_code, self.on_name_fetched)

    def on_name_fetched(self, name):
        self.currectName = name
        result = self.model.transcribe("/tmp/output.wav", language="chinese", initial_prompt=self.currectName)
        clamName = result["text"]
        self.browser.page().runJavaScript('document.getElementById("result").textContent = "辨識結果：" + "{}";'.format(clamName))
        if self.currectName in clamName:
            self.speech_engine.say(self.currectName + "請領藥")
        else:
            self.speech_engine.say("你的名字不對，請再試一次")

    def recordAudio(self):
        fs = 44100
        seconds = 3
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
        sd.wait()
        myrecording_int16 = (myrecording * (2**15 - 1)).astype(np.int16)
        wavio.write("/tmp/output.wav", myrecording_int16, fs)
        self.get_name_from_input()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
	