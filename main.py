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

    - name: Setup Android SDK with accepted licenses
      run: |
        export ANDROID_HOME=$HOME/.buildozer/android/platform/android-sdk
        mkdir -p $ANDROID_HOME/licenses
        echo -e "\n24333f8a63b6825ea9c5514f83c2829b004d1fee" > $ANDROID_HOME/licenses/android-sdk-license
        echo -e "\n84831b9409646a918e30573bab4c9c91346d8abd" > $ANDROID_HOME/licenses/android-sdk-preview-license
        echo -e "\nd975f751698a77b662f1254ddbeed3901e976f5a" >> $ANDROID_HOME/licenses/android-sdk-license
        mkdir -p ~/.android
        echo "count=0" > ~/.android/repositories.cfg

    - name: Build APK
      run: |
        buildozer android debug 2>&1
      timeout-minutes: 60

    - name: Upload APK
      uses: actions/upload-artifact@v4
      with:
        name: DoramaDown-APK
        path: bin/*.apk
