import os
import subprocess

# ==========================================
# دالة مساعدة لإنشاء الملفات
# ==========================================
def create_file(path, content):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Updated: {path}")

# ==========================================
# 1. إصلاح Gradle (الحل الجذري لمشكلة Init)
# ==========================================
# التغيير الجوهري: إضافة packaging { jniLibs { useLegacyPackaging = true } }
# هذا يمنع ضغط ملفات النظام ويسمح للمكتبة باستخراجها بنجاح
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
        
        // إجبار النظام على دعم كل المعالجات
        ndk {
            abiFilters.add("armeabi-v7a")
            abiFilters.add("arm64-v8a")
            abiFilters.add("x86")
            abiFilters.add("x86_64")
        }
    }

    // الخلطة السحرية: منع ضغط ملفات المكتبة لتتمكن من العمل
    packaging {
        jniLibs {
            useLegacyPackaging = true
        }
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
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
    
    // استخدام النسخة الموثوقة 0.17.2
    implementation("io.github.junkfood02.youtubedl-android:library:0.17.2")
    implementation("io.github.junkfood02.youtubedl-android:ffmpeg:0.17.2") 
    
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
}
"""

# ==========================================
# 2. تحديث AndroidManifest (ضمان التصريح)
# ==========================================
manifest_content = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!-- تصريحات الإنترنت والتخزين -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@android:drawable/ic_menu_save"
        android:label="MyTube"
        android:requestLegacyExternalStorage="true"
        android:supportsRtl="true"
        android:theme="@style/Theme.MyTube.Dialog"
        tools:targetApi="31">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.MyTube.Dialog">
            
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>

            <intent-filter>
                <action android:name="android.intent.action.SEND" />
                <category android:name="android.intent.category.DEFAULT" />
                <data android:mimeType="text/plain" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""

# ==========================================
# 3. تحديث MainActivity (طلب الصلاحيات + التهيئة)
# ==========================================
kotlin_content = """package org.alituama.mytube

import android.Manifest
import android.animation.ArgbEvaluator
import android.animation.ObjectAnimator
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.util.Log
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.google.android.material.textfield.TextInputEditText
import com.yausername.youtubedl_android.YoutubeDL
import com.yausername.youtubedl_android.YoutubeDLRequest
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

class MainActivity : AppCompatActivity() {

    private lateinit var tvStatus: TextView
    private val PERMISSION_REQUEST_CODE = 100
    private var isInitialized = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val etUrl = findViewById<TextInputEditText>(R.id.etUrl)
        val btnFetch = findViewById<Button>(R.id.btnFetch)
        tvStatus = findViewById(R.id.tvStatus)
        val tvCredits = findViewById<TextView>(R.id.tvCredits)

        animateCredits(tvCredits)

        // 1. طلب الصلاحيات فوراً
        requestPermissionsSafely()

        // 2. محاولة التهيئة
        initLibrary()

        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { etUrl.setText(it) }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) {
                if (isInitialized) startDownload(url)
                else {
                    Toast.makeText(this, "Wait for initialization...", Toast.LENGTH_SHORT).show()
                    initLibrary()
                }
            } else {
                val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                val clipData = clipboard.primaryClip
                if (clipData != null && clipData.itemCount > 0) {
                    val pasteText = clipData.getItemAt(0).text.toString()
                    etUrl.setText(pasteText)
                }
            }
        }
    }

    private fun requestPermissionsSafely() {
        val permissions = mutableListOf<String>()

        // صلاحيات التخزين (مهمة للأندرويد القديم والجديد)
        if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.Q) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                permissions.add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
            }
        } else {
             // للأندرويد 11+ (Scoped Storage) - عادة لا نحتاج Write للملفات العامة ولكن للاحتياط
             // يمكن إضافة READ_MEDIA_VIDEO إذا كنا سنعرض فيديوهات، ولكن للتنزيل فقط لا داعي لتعقيد الأمور
        }

        // صلاحيات الإشعارات (أندرويد 13+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                permissions.add(Manifest.permission.POST_NOTIFICATIONS)
            }
        }

        if (permissions.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, permissions.toTypedArray(), PERMISSION_REQUEST_CODE)
        }
    }

    private fun initLibrary() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // التهيئة - يجب أن تنجح الآن بفضل إصلاح Gradle
                YoutubeDL.getInstance().init(application)
                isInitialized = true
                withContext(Dispatchers.Main) {
                    tvStatus.text = "Ready (Library Loaded)"
                }
            } catch (e: Exception) {
                Log.e("MyTube", "Init failed", e)
                withContext(Dispatchers.Main) {
                    tvStatus.text = "Init Error: ${e.message}"
                    showErrorDialog("Critical Error: Failed to load native libraries.\\nError: ${e.message}")
                }
            }
        }
    }

    private fun startDownload(url: String) {
        tvStatus.text = "Preparing..."
        
        // المسار العام
        val downloadDir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        if (!downloadDir.exists()) downloadDir.mkdirs()

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val request = YoutubeDLRequest(url)
                request.addOption("-o", downloadDir.absolutePath + "/%(title)s.%(ext)s")
                request.addOption("-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")
                
                withContext(Dispatchers.Main) { tvStatus.text = "Downloading..." }

                YoutubeDL.getInstance().execute(request, null) { progress, eta, line ->
                    runOnUiThread { tvStatus.text = "$progress% | ETA: $eta s" }
                }

                withContext(Dispatchers.Main) {
                    tvStatus.text = "✅ Done! Saved in Downloads/MyTube"
                    Toast.makeText(this@MainActivity, "Saved successfully!", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvStatus.text = "Failed"
                    showErrorDialog("Download Error:\\n${e.message}")
                }
            }
        }
    }

    private fun showErrorDialog(msg: String) {
        AlertDialog.Builder(this)
            .setTitle("Error")
            .setMessage(msg)
            .setPositiveButton("OK", null)
            .show()
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

if __name__ == "__main__":
    create_file("app/build.gradle.kts", build_gradle_content)
    create_file("app/src/main/AndroidManifest.xml", manifest_content)
    create_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", kotlin_content)
    
    print("\n🚀 Pushing Ultimate Fix to GitHub...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Ultimate Fix: Legacy Packaging & Permissions"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! This APK should work perfectly.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
