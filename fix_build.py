import os

# محتوى ملف البناء الجديد (المصحح)
new_workflow = """name: Build Android APK

on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up JDK 17
      uses: actions/setup-java@v3
      with:
        java-version: '17'
        distribution: 'temurin'

    - name: Setup Gradle
      uses: gradle/gradle-build-action@v2

    # هنا التغيير: نستخدم gradle الخاص بالسيرفر مباشرة
    - name: Build with Gradle
      run: gradle assembleDebug --no-daemon

    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: MyTube-APK
        path: app/build/outputs/apk/debug/app-debug.apk
"""

# كتابة الملف في مكانه الصحيح
workflow_path = ".github/workflows/build.yml"
with open(workflow_path, "w") as f:
    f.write(new_workflow)

print("✅ تم إصلاح ملف البناء بنجاح!")
