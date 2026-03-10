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
        pip install cython==0.29.3
