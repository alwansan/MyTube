import os
import subprocess

# 1. تنظيف وإعادة كتابة gradle.properties بشكل صحيح تماماً
gradle_props_content = """org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
kotlin.code.style=official
"""

print("🔧 Re-creating gradle.properties...")
with open("gradle.properties", "w", encoding="utf-8") as f:
    f.write(gradle_props_content)


# 2. تنظيف وإصلاح app/build.gradle.kts (إزالة التكرار وضمان المكتبات)
app_build_gradle_content = """plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "org.alituama.mytube"
    compileSdk = 34

    defaultConfig {
        applicationId = "org.alituama.mytube"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = "1.8"
    }
    buildFeatures {
        viewBinding = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    
    // مكتبة التحميل (إصدار junkfood02 هو الأحدث والأكثر استقراراً حالياً)
    implementation("io.github.junkfood02.youtubedl-android:library:0.17.2")
    implementation("io.github.junkfood02.youtubedl-android:ffmpeg:0.17.2") 
    
    // للمعالجة في الخلفية
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
}
"""

print("🔧 Re-creating app/build.gradle.kts...")
with open("app/build.gradle.kts", "w", encoding="utf-8") as f:
    f.write(app_build_gradle_content)


# 3. إنشاء ملف Workflow مضمون (GitHub Actions)
# سنستخدم Java 17 و Gradle مهيأ مسبقاً
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
      uses: actions/checkout@v4

    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'
        cache: gradle

    - name: Grant execute permission for gradlew
      run: chmod +x gradlew

    - name: Build APK
      run: ./gradlew assembleDebug --stacktrace

    - name: Upload APK
      uses: actions/upload-artifact@v4
      with:
        name: MyTube-APK
        path: app/build/outputs/apk/debug/app-debug.apk
"""

os.makedirs(".github/workflows", exist_ok=True)
print("🔧 Re-creating .github/workflows/android.yml...")
with open(".github/workflows/android.yml", "w", encoding="utf-8") as f:
    f.write(workflow_content)


# 4. تنفيذ أوامر Git
print("🚀 Pushing fixes to GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Force Fix: Clean gradle.properties and dependencies"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ Done! Go check GitHub Actions tab.")
except subprocess.CalledProcessError as e:
    print(f"❌ Git Error: {e}")
    print("Try running: git push --force")

"""
