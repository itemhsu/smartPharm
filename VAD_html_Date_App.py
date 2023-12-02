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
import webrtcvad
import wave


class RealTimeVAD:
    def __init__(self, mode=3, frame_duration=30, sampling_rate=16000):
        self.vad = webrtcvad.Vad(mode)
        self.frame_duration = frame_duration  # in milliseconds
        self.sampling_rate = sampling_rate
        self.frame_size = int(sampling_rate * frame_duration / 1000)
        self.frames = []  # Store frames with detected speech

    def is_speech(self, frame):
        return self.vad.is_speech(frame.tobytes(), self.sampling_rate)

    def start_stream(self):
        with sd.InputStream(samplerate=self.sampling_rate, channels=1, dtype='int16') as stream:
            print("Starting real-time VAD. Speak into the microphone...")
            was_speech = False
            iniSatus = True 
            while True:
                frame, _ = stream.read(self.frame_size)
                if self.is_speech(frame):
                    print("Speech detected!")
                    if iniSatus: #靜默之後 ， 才開始錄音
                        print("recording!")
                        self.frames.append(frame)
                        was_speech = True
                else:
                    iniSatus = True #靜默偵測
                    print("Silence...")
                    if was_speech:
                        break

    def until_silent(self):
        with sd.InputStream(samplerate=self.sampling_rate, channels=1, dtype='int16') as stream:
            print("until silent...")
            status=0# 0 silence , 1 speak , 2 silence
            IIR=1.0
            count=0
            while True:
                frame, _ = stream.read(self.frame_size)
                if self.is_speech(frame):
                    IIR=IIR*0.8+0.2
                else:
                    IIR=IIR*0.8+0
                print("IIR=", IIR)
                if IIR > 0.1:
                    print("wait speach complete!")

                else:
                    print("Silence...")
                    break

    def save_to_wav(self, filename='detected_speech.wav'):
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # Assuming int16 format
            wf.setframerate(self.sampling_rate)
            wf.writeframes(b''.join(self.frames))


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
                "waitTime": 0,
                "recordTmp": "/tmp/output.wav",
                "correctAns": "柯文哲",
                "errorAlarm": "你的名字不對，請問你叫什麼名字？",
                "max_attempts": 5
            },
            {
                "askStr": "請問你的民國出生年？",
                "waitTime": 0,
                "recordTmp": "/tmp/outputY.wav",
                "correctAns": "八十",
                "errorAlarm": "你的民國出生年不對，請問你的民國出生年？",
                "max_attempts": 5
            },
            {
                "askStr": "請問你的出生月份？",
                "waitTime": 0,
                "recordTmp": "/tmp/outputM.wav",
                "correctAns": "十",
                "errorAlarm": "你的出生月份不對，請問你的出生月份？",
                "max_attempts": 5
            },
            {
                "askStr": "請問你的出生日？",
                "waitTime": 0,
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

    def untilSilent(self):
        real_time_vad = RealTimeVAD()
        real_time_vad.until_silent()



    def AskAnswer(self, askStr, waitTime, recordTmp, correctAns, errorAlarm, max_attempts):
        self.speech_engine.say(askStr)
        
        self.untilSilent()
        

        self.attempts_made = 0
        self.max_attempts = max_attempts
        
        self.result_correct = False  # Initialize result_correct to False
    
        loop = QEventLoop()  # Create a local event loop
        QTimer.singleShot(waitTime, lambda: self.recordAudio(recordTmp, correctAns, errorAlarm, loop))
        loop.exec_()  # This will block until loop.quit() is called
    
        return self.result_correct



    def recordAudio(self, recordTmp, correctAns, errorAlarm, loop):
        real_time_vad = RealTimeVAD()
        real_time_vad.start_stream()
        real_time_vad.save_to_wav(recordTmp)

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
                self.untilSilent()
                QTimer.singleShot(0, lambda: self.recordAudio(recordTmp, correctAns, errorAlarm, loop))  # Try again after a delay
            else:
                print("Maximum attempts reached. Moving to next question.")
                self.attempts_made = 0  # Reset the attempts for the next question
                loop.quit() 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
	