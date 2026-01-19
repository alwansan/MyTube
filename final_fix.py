import os

# محتوى ملف البناء المضمون
workflow_content = """name: Build Android APK

on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Code
      uses: actions/checkout@v3

    - name: Set up JDK 17
      uses: actions/setup-java@v3
      with:
        java-version: '17'
        distribution: 'temurin'

    # 🟢 الخطوة السحرية: تثبيت Gradle 8.2 يدوياً في السيرفر
    - name: Setup Gradle
      uses: gradle/gradle-build-action@v2
      with:
        gradle-version: 8.2

    # الآن الأمر سيعمل لأننا ثبتناه في الخطوة السابقة
    - name: Build APK
      run: gradle assembleDebug --no-daemon --stacktrace

    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: MyTube-APK
        path: app/build/outputs/apk/debug/app-debug.apk
"""

# كتابة الملف
with open(".github/workflows/build.yml", "w") as f:
    f.write(workflow_content)

print("✅ تم تحديث ملف البناء ليعمل بدون ملفات wrapper!")
