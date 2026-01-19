import os
import subprocess
import urllib.request

# ==========================================
# دالة مساعدة لإنشاء الملفات
# ==========================================
def create_file(path, content):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Created/Updated: {path}")

# ==========================================
# 1. التأكد من وجود Gradle Wrapper (مهم جداً)
# ==========================================
def ensure_gradle_wrapper():
    print("🔄 Checking Gradle Wrapper...")
    wrapper_files = {
        "gradle/wrapper/gradle-wrapper.properties": """distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-8.2-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""",
    }
    
    # تحميل ملف jar إذا لم يكن موجوداً
    jar_path = "gradle/wrapper/gradle-wrapper.jar"
    if not os.path.exists(jar_path):
        os.makedirs("gradle/wrapper", exist_ok=True)
        print("   Downloading gradle-wrapper.jar...")
        try:
            url = "https://github.com/gradle/gradle/raw/v8.5.0/gradle/wrapper/gradle-wrapper.jar"
            urllib.request.urlretrieve(url, jar_path)
        except Exception as e:
            print(f"⚠️ Warning: Could not download wrapper jar: {e}")

    # تحميل سكربت gradlew
    gradlew_path = "gradlew"
    if not os.path.exists(gradlew_path):
        print("   Downloading gradlew script...")
        try:
            url = "https://raw.githubusercontent.com/gradle/gradle/v8.5.0/gradlew"
            urllib.request.urlretrieve(url, gradlew_path)
            os.chmod(gradlew_path, 0o755)
        except Exception as e:
            print(f"⚠️ Warning: Could not download gradlew: {e}")

    # كتابة ملف الخصائص
    for path, content in wrapper_files.items():
        create_file(path, content)

# ==========================================
# 2. إعدادات المشروع (gradle.properties)
# ==========================================
props_content = """
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
kotlin.code.style=official
"""

# ==========================================
# 3. إعدادات البناء (build.gradle.kts)
# ==========================================
build_gradle_content = """
plugins {
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
    
    // استخدام النسخة المستقرة المتوافقة
    implementation("io.github.junkfood02.youtubedl-android:library:0.17.2")
    implementation("io.github.junkfood02.youtubedl-android:ffmpeg:0.17.2")
    
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
}
"""

# ==========================================
# 4. ملف الواجهة (activity_main.xml) - تم إصلاح الأيقونة
# ==========================================
layout_content = """<?xml version="1.0" encoding="utf-8"?>
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

# ==========================================
# 5. ملف الكود (MainActivity.kt)
# ==========================================
kotlin_content = """package org.alituama.mytube

import android.animation.ArgbEvaluator
import android.animation.ObjectAnimator
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.os.Environment
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.google.android.material.textfield.TextInputEditText
import com.yausername.youtubedl_android.YoutubeDL
import com.yausername.youtubedl_android.YoutubeDLRequest
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        try {
            YoutubeDL.getInstance().init(application)
        } catch (e: Exception) {
            e.printStackTrace()
        }

        val etUrl = findViewById<TextInputEditText>(R.id.etUrl)
        val btnFetch = findViewById<Button>(R.id.btnFetch)
        val tvStatus = findViewById<TextView>(R.id.tvStatus)
        val tvCredits = findViewById<TextView>(R.id.tvCredits)

        animateCredits(tvCredits)

        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            val sharedText = intent.getStringExtra(Intent.EXTRA_TEXT)
            if (sharedText != null) {
                etUrl.setText(sharedText)
                startDownload(sharedText, tvStatus)
            }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) {
                startDownload(url, tvStatus)
            } else {
                val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                val clipData = clipboard.primaryClip
                if (clipData != null && clipData.itemCount > 0) {
                    val pasteText = clipData.getItemAt(0).text.toString()
                    etUrl.setText(pasteText)
                    startDownload(pasteText, tvStatus)
                }
            }
        }
    }

    private fun startDownload(url: String, statusView: TextView) {
        statusView.text = "Initializing..."
        
        val downloadDir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        if (!downloadDir.exists()) downloadDir.mkdirs()

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val request = YoutubeDLRequest(url)
                request.addOption("-o", downloadDir.absolutePath + "/%(title)s.%(ext)s")
                request.addOption("-f", "bestvideo+bestaudio/best") 
                
                withContext(Dispatchers.Main) {
                    statusView.text = "Downloading..."
                }

                YoutubeDL.getInstance().execute(request) { progress, eta ->
                    runOnUiThread {
                        statusView.text = "Progress: $progress% (ETA: $eta s)"
                    }
                }

                withContext(Dispatchers.Main) {
                    statusView.text = "Done! Check Downloads/MyTube"
                    Toast.makeText(this@MainActivity, "Saved!", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    statusView.text = "Error: " + e.message
                }
            }
        }
    }

    private fun animateCredits(view: TextView) {
        val colorAnim = ObjectAnimator.ofInt(view, "textColor",
            Color.RED, Color.YELLOW, Color.WHITE, Color.RED)
        colorAnim.setDuration(3000)
        colorAnim.setEvaluator(ArgbEvaluator())
        colorAnim.repeatCount = ObjectAnimator.INFINITE
        colorAnim.repeatMode = ObjectAnimator.RESTART
        colorAnim.start()
    }
}
"""

# ==========================================
# 6. ملف سير العمل (GitHub Actions)
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

# ==========================================
# التنفيذ
# ==========================================
if __name__ == "__main__":
    ensure_gradle_wrapper()
    create_file("gradle.properties", props_content)
    create_file("app/build.gradle.kts", build_gradle_content)
    create_file("app/src/main/res/layout/activity_main.xml", layout_content)
    create_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", kotlin_content)
    create_file(".github/workflows/android.yml", workflow_content)
    
    print("\n🚀 Pushing changes to GitHub...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Final Total Reset"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! Check GitHub Actions now.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
