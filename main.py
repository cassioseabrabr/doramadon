name: Build DoramaDown APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install system dependencies
      run: |
        sudo apt-get update -qq
        sudo apt-get install -y -qq \
          python3-pip build-essential git \
          libssl-dev libffi-dev \
          libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
          libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
          zlib1g-dev openjdk-17-jdk unzip zip wget
        pip install --upgrade pip setuptools wheel
        pip install cython==0.29.37 buildozer

    - name: Install Android SDK manually
      run: |
        wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip -O cmdtools.zip
        mkdir -p $HOME/.buildozer/android/platform/android-sdk/cmdline-tools
        unzip -q cmdtools.zip -d $HOME/.buildozer/android/platform/android-sdk/cmdline-tools
        mv $HOME/.buildozer/android/platform/android-sdk/cmdline-tools/cmdline-tools \
           $HOME/.buildozer/android/platform/android-sdk/cmdline-tools/latest
        export PATH=$PATH:$HOME/.buildozer/android/platform/android-sdk/cmdline-tools/latest/bin
        yes | sdkmanager --licenses
        yes | sdkmanager "platforms;android-33" "build-tools;33.0.2" "platform-tools"
        mkdir -p ~/.android
        echo "count=0" > ~/.android/repositories.cfg

    - name: Build APK
      run: |
        export ANDROID_HOME=$HOME/.buildozer/android/platform/android-sdk
        buildozer android debug 2>&1
      timeout-minutes: 120

    - name: Upload APK
      uses: actions/upload-artifact@v4
      with:
        name: DoramaDown-APK
        path: bin/*.apk
