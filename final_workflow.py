import os

# محتوى ملف البناء الصحيح 100%
yaml_content = """name: Build Android APK

on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

jobs:
  build:
    name: Build APK
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v3
        with:
          gradle-version: '8.5'

      - name: Accept Android Licenses
        run: |
          yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --licenses || true

      - name: Build Debug APK
        run: gradle assembleDebug --stacktrace

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: MyTube-APK
          path: app/build/outputs/apk/debug/app-debug.apk
"""

# التأكد من المجلد
os.makedirs(".github/workflows", exist_ok=True)

# كتابة الملف
with open(".github/workflows/build.yml", "w") as f:
    f.write(yaml_content)

print("✅ تم إنشاء ملف البناء الجديد بصيغة سليمة 100%")
