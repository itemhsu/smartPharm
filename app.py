import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QLabel, QWidget
from PyQt5.QtTextToSpeech import QTextToSpeech
from PyQt5.QtCore import QTimer
import time
import sounddevice as sd
import wavio
import numpy as np
import whisper

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()

        # GUI Layout and Elements
        self.setWindowTitle("智能藥箱給藥系統")
        self.setGeometry(100, 100, 400, 200)

        self.layout = QVBoxLayout()
        self.label = QLabel("藥包上的姓名", self)
        self.label.setMaximumHeight(self.label.fontMetrics().height())
        
        self.layout.addWidget(self.label)
        self.text_edit = QLineEdit(self)
        self.layout.addWidget(self.text_edit)

        self.button = QPushButton("領藥", self)
        self.button.clicked.connect(self.onPress)
        self.layout.addWidget(self.button)
        self.labelOut = QLabel("辨識結果：＿", self)
        self.labelOut.setMaximumHeight(self.labelOut.fontMetrics().height())
        self.layout.addWidget(self.labelOut)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Initialize QtTextToSpeech
        self.speech_engine = QTextToSpeech(self)
        self.model = whisper.load_model("base")

        
    def onPress(self):
        # Speak using QtTextToSpeech
        self.speech_engine.say("請問你叫什麼名字？")
        
        # If you want to wait for the speech to finish before proceeding (optional):
        #while self.speech_engine.state() == QTextToSpeech.State.Speaking:
        #    print(self.speech_engine.state())
        #    time.sleep(0.1)
        QTimer.singleShot(2000, self.recordAudio) 
        #time.sleep(5)  # wait for 5 seconds
        #print("Recording start")

        #self.recordAudio()

    def recordAudio(self):
        fs = 44100  # Sample rate
        seconds = 3  # Duration of recording

        print("Recording...")
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
        sd.wait()  # Wait until recording is finished
        print("Record ok")
        myrecording_int16 = (myrecording * (2**15 - 1)).astype(np.int16)
        wavio.write("output.wav", myrecording_int16, fs)  # save as WAV file
        currectName=self.text_edit.text()
        result = self.model.transcribe("output.wav",  language="chinese", initial_prompt=currectName)
        print(result["text"])
        clamName=result["text"]
        self.labelOut.setText("辨識結果："+ result["text"])
        if currectName in clamName:
            self.speech_engine.say(currectName+"請領藥")
        else:
            self.speech_engine.say("你的名字不對，請再試一次")
            


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

