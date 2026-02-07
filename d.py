import os
import subprocess

# تحديث ملف GitHub Action
github_action_yaml = """name: Build APK

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'
    
    - name: Setup Android SDK
      uses: android-actions/setup-android@v3
    
    - name: Grant execute permission for gradlew
      run: chmod +x gradlew
    
    - name: Build Debug APK
      run: ./gradlew assembleDebug
    
    - name: Upload APK
      uses: actions/upload-artifact@v4
      with:
        name: app-debug-apk
        path: app/build/outputs/apk/debug/app-debug.apk
"""

# إنشاء الملف
with open(".github/workflows/android.yml", "w", encoding="utf-8") as f:
    f.write(github_action_yaml)

print("✅ تم تحديث ملف GitHub Action")

# Git operations
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Fix: Update GitHub Actions versions"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ تم الرفع إلى GitHub")
except subprocess.CalledProcessError as e:
    print(f"❌ خطأ في Git: {e}")