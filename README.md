# smartPharm
This is a smart pharm box controller

# Setup
## install requirement python package
```
brew install mbedtls
pip3 install wavio
pip3 install -U openai-whisper
pip3 install PyQT5
pip3 install sounddevice
pip3 install PyQtWebEngine
```
## Mac OSX setting
### 1. Apple -> System Settings ... -> Accessibility
<img width="734" alt="image" src="https://github.com/itemhsu/smartPharm/assets/25599185/e38556cd-8467-4624-a7e8-d639f36cd81d">

### 2. Accessibility -> System speech language -> Chinese 
<img width="710" alt="image" src="https://github.com/itemhsu/smartPharm/assets/25599185/64311aae-4cfc-42f6-951c-a1338c2cd0b6">

### 3. package
#### 3.0 run
```
python html_Date_App.py
```
#### 3.1 pyinstall 1st time to create app.spec
```
pyinstaller --onefile --windowed html_Date_App.py --icon=pharm.icns

```

#### 3.2 pyinstall add more data in app.spec
```
a = Analysis(
    ['html_Date_App.py'],
    pathex=[],
    binaries=[],
    datas=[('/Users/hsuyueht/Library/Python/3.9/lib/python/site-packages/whisper/assets/mel_filters.npz', 'whisper/assets/'), ('/Users/hsuyueht/Library/Python/3.9/lib/python/site-packages/whisper/assets/multilingual.tiktoken', 'whisper/assets/')],
```
#### 3.3 pyinstall with exist *.spec
```
pyinstaller html_Date_App.spec
```
### wtach log
```
log show --predicate 'process == "app"' --last 1h
```

