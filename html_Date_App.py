import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, pyqtSlot, QTimer, QObject, QEventLoop
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

    @pyqtSlot(str)
    def updateName(self, value):
        self.main_window.questions[0]["correctAns"] = value

    @pyqtSlot(str)
    def updateYear(self, value):
        self.main_window.questions[1]["correctAns"] = value

    @pyqtSlot(str)
    def updateMonth(self, value):
        self.main_window.questions[2]["correctAns"] = value

    @pyqtSlot(str)
    def updateDay(self, value):
        self.main_window.questions[3]["correctAns"] = value


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
        self.browser.page().setWebChannel(self.channel)
        self.setCentralWidget(self.browser)
        self.speech_engine = QTextToSpeech(self)
        self.model = whisper.load_model("base")
        self.result_correct = False
        self.attempts_made = 0
        self.questions = [
            {
                "askStr": "請問你叫什麼名字？",
                "waitTime": 2000,
                "recordTmp": "/tmp/output.wav",
                "correctAns": "柯文哲",
                "errorAlarm": "你的名字不對，請問你叫什麼名字？",
                "max_attempts": 5
            },
            {
                "askStr": "請問你的民國出生年？",
                "waitTime": 2000,
                "recordTmp": "/tmp/outputY.wav",
                "correctAns": "八十",
                "errorAlarm": "你的民國出生年不對，請問你的民國出生年？",
                "max_attempts": 5
            },
            {
                "askStr": "請問你的出生月份？",
                "waitTime": 2000,
                "recordTmp": "/tmp/outputM.wav",
                "correctAns": "十",
                "errorAlarm": "你的出生月份不對，請問你的出生月份？",
                "max_attempts": 5
            },
            {
                "askStr": "請問你的出生日？",
                "waitTime": 2000,
                "recordTmp": "/tmp/outputD.wav",
                "correctAns": "八",
                "errorAlarm": "你的出生日不對，請問你的出生日？",
                "max_attempts": 5
            }
        ]
        # 初始化 QWebChannel 和註冊 Python 對象供 JavaScript 使用



    @pyqtSlot()
    def onPress(self):
        for question in self.questions:
            success = self.AskAnswer(**question)
            if not success:
                break
        if success:
            self.speech_engine.say("請領藥")
            self.browser.page().runJavaScript('document.getElementById("result").textContent = "辨識結果： 正確" ;')

    def AskAnswer(self, askStr, waitTime, recordTmp, correctAns, errorAlarm, max_attempts):
        self.speech_engine.say(askStr)
        self.attempts_made = 0
        self.max_attempts = max_attempts
        print("70:"+askStr)
        self.result_correct = False  # Initialize result_correct to False
    
        loop = QEventLoop()  # Create a local event loop
        QTimer.singleShot(waitTime, lambda: self.recordAudio(recordTmp, correctAns, errorAlarm, loop))
        loop.exec_()  # This will block until loop.quit() is called
    
        return self.result_correct


    def recordAudio(self, recordTmp, correctAns, errorAlarm,  loop):
        fs = 44100
        seconds = 3
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
        sd.wait()
        myrecording_int16 = (myrecording * (2**15 - 1)).astype(np.int16)
        wavio.write(recordTmp, myrecording_int16, fs)
        result = self.model.transcribe(recordTmp, language="chinese" ,initial_prompt=correctAns)
        print(result)
        print(result["text"])
        self.browser.page().runJavaScript('document.getElementById("result").textContent = "辨識結果：" + "{}";'.format(result["text"]))
        
        print(correctAns)
        self.result_correct = correctAns in result["text"]
        print(self.result_correct)

        if self.result_correct:
            print("Correct answer.")

            self.attempts_made = 0  # Reset the attempts for the next question
            loop.quit()
        else:
            self.attempts_made += 1
            if self.attempts_made < self.max_attempts:
                print("Wrong answer. Trying again...")
                self.speech_engine.say(errorAlarm)
                QTimer.singleShot(2000, lambda: self.recordAudio(recordTmp, correctAns, errorAlarm, loop))  # Try again after a delay
            else:
                print("Maximum attempts reached. Moving to next question.")
                self.attempts_made = 0  # Reset the attempts for the next question
                loop.quit() 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
	