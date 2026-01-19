import os
import subprocess

# ==========================================
# 1. إصلاح gradle.properties (تنظيف شامل)
# ==========================================
gradle_props_content = """org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
kotlin.code.style=official
"""

print("🔧 Fixing gradle.properties...")
with open("gradle.properties", "w", encoding="utf-8") as f:
    f.write(gradle_props_content)

# ==========================================
# 2. إصلاح app/build.gradle.kts
# ==========================================
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
    
    // مكتبة التحميل
    implementation("io.github.junkfood02.youtubedl-android:library:0.17.2")
    implementation("io.github.junkfood02.youtubedl-android:ffmpeg:0.17.2") 
    
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
}
"""

print("🔧 Fixing app/build.gradle.kts...")
with open("app/build.gradle.kts", "w", encoding="utf-8") as f:
    f.write(app_build_gradle_content)

# ==========================================
# 3. إصلاح activity_main.xml (إزالة الأيقونة الخاصة)
# ==========================================
# التغيير هنا: استبدلنا ic_menu_paste_holo_light بـ ic_menu_edit
layout_xml_content = """<?xml version="1.0" encoding="utf-8"?>
<androidx.cardview.widget.CardView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:cardCornerRadius="24dp"
    app:cardBackgroundColor="#1F1F1F"
    app:cardElevation="8dp">

    <androidx.constraintlayout.widget.ConstraintLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:padding="20dp">

        <TextView
            android:id="@+id/tvTitle"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="MyTube Downloader"
            android:textColor="#FFFFFF"
            android:textSize="22sp"
            android:textStyle="bold"
            app:layout_constraintStart_toStartOf="parent"
            app:layout_constraintTop_toTopOf="parent" />

        <com.google.android.material.textfield.TextInputLayout
            android:id="@+id/inputLayout"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_marginTop="16dp"
            android:hint="YouTube Link"
            android:textColorHint="#AAAAAA"
            style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
            app:boxStrokeColor="#FF0000"
            app:hintTextColor="#FF0000"
            app:endIconMode="clear_text"
            app:startIconDrawable="@android:drawable/ic_menu_edit"
            app:layout_constraintEnd_toEndOf="parent"
            app:layout_constraintStart_toStartOf="parent"
            app:layout_constraintTop_toBottomOf="@id/tvTitle">

            <com.google.android.material.textfield.TextInputEditText
                android:id="@+id/etUrl"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:textColor="#FFFFFF"
                android:inputType="textUri" />
        </com.google.android.material.textfield.TextInputLayout>

        <Button
            android:id="@+id/btnFetch"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="10dp"
            android:text="Fetch Formats"
            android:textColor="#FFFFFF"
            android:textStyle="bold"
            android:backgroundTint="#FF0000"
            app:layout_constraintTop_toBottomOf="@id/inputLayout" />

        <TextView
            android:id="@+id/tvStatus"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="15dp"
            android:text="Ready to download"
            android:textColor="#AAAAAA"
            android:textSize="14sp"
            app:layout_constraintStart_toStartOf="parent"
            app:layout_constraintTop_toBottomOf="@id/btnFetch" />

        <TextView
            android:id="@+id/tvCredits"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="25dp"
            android:text="By Ali Tuama"
            android:textSize="14sp"
            android:textStyle="bold"
            app:layout_constraintBottom_toBottomOf="parent"
            app:layout_constraintEnd_toEndOf="parent"
            app:layout_constraintStart_toStartOf="parent"
            app:layout_constraintTop_toBottomOf="@id/tvStatus" />

    </androidx.constraintlayout.widget.ConstraintLayout>
</androidx.cardview.widget.CardView>
"""

print("🔧 Fixing activity_main.xml (Removing private icon)...")
os.makedirs("app/src/main/res/layout", exist_ok=True)
with open("app/src/main/res/layout/activity_main.xml", "w", encoding="utf-8") as f:
    f.write(layout_xml_content)

# ==========================================
# 4. إعادة كتابة ملف Workflow لضمان النجاح
# ==========================================
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

print("🔧 updating .github/workflows/android.yml...")
os.makedirs(".github/workflows", exist_ok=True)
with open(".github/workflows/android.yml", "w", encoding="utf-8") as f:
    f.write(workflow_content)

# ==========================================
# 5. رفع التغييرات
# ==========================================
print("🚀 Pushing fixes to GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Final Fix: Remove private resources and fix Gradle"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ Done! This build should pass.")
except subprocess.CalledProcessError as e:
    print(f"❌ Git Error: {e}")
