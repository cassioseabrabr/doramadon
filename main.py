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

    - name: Install dependencies
      run: |
        sudo apt update
        sudo apt install -y git zip unzip openjdk-17-jdk python3-pip
        pip install --upgrade pip
        pip install buildozer cython

    - name: Build APK
      run: |
        buildozer android debug --accept-sdk-license

    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: doramadown-apk
        path: bin/*.apk
