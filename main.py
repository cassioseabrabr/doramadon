name: Build DoramaDown APK

on:
  push:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v3

    - name: Install system dependencies
      run: |
        sudo apt update
        sudo apt install -y git zip unzip openjdk-17-jdk python3-pip
        pip install buildozer cython

    - name: Accept Android SDK licenses
      run: |
        yes | sdkmanager --licenses || true

    - name: Build APK
      run: |
        buildozer android debug

    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: doramadown-apk
        path: bin/*.apk
