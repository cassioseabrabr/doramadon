name: Build DoramaDown APK

on:
  push:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Java
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "17"

      - name: Install system dependencies
        run: |
          sudo apt update
          sudo apt install -y \
            git zip unzip autoconf libtool pkg-config zlib1g-dev \
            libncurses5-dev libncursesw5-dev cmake libffi-dev libssl-dev \
            build-essential ccache libltdl-dev

      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install buildozer cython virtualenv

      - name: Build APK
        run: |
          buildozer android debug --accept-sdk-license

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: doramadown-apk
          path: bin/*.apk
