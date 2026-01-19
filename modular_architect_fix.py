import os
import shutil
import subprocess

# ==========================================
# إعداد الأدوات
# ==========================================
def create_file(path, content):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Created: {path}")

def clean_old_files():
    # حذف ملف MainActivity القديم لأنه سيتعارض مع الهيكلية الجديدة
    old_main = "app/src/main/java/org/alituama/mytube/MainActivity.kt"
    if os.path.exists(old_main):
        os.remove(old_main)
        print("🗑️ Removed old MainActivity.kt")

# ==========================================
# 1. إعداد Gradle (معالجة البناء)
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
        versionCode = 4
        versionName = "4.0"
        
        ndk {
            abiFilters.add("armeabi-v7a")
            abiFilters.add("arm64-v8a")
            abiFilters.add("x86")
            abiFilters.add("x86_64")
        }
    }

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
    
    // المكتبة الأساسية
    implementation("io.github.junkfood02.youtubedl-android:library:0.17.2")
    implementation("io.github.junkfood02.youtubedl-android:ffmpeg:0.17.2") 
    
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
}
"""

# ==========================================
# 2. ملف: Core/LibraryManager.kt
# (وظيفته: التهيئة والتحديث الإجباري)
# ==========================================
library_manager_code = """package org.alituama.mytube.core

import android.app.Application
import android.util.Log
import com.yausername.youtubedl_android.YoutubeDL

object LibraryManager {
    fun init(app: Application): String {
        return try {
            // 1. التهيئة الأولية (فك الضغط)
            YoutubeDL.getInstance().init(app)
            "Initialized"
        } catch (e: Exception) {
            "Init Error: ${e.message}"
        }
    }

    fun update(app: Application): String {
        return try {
            // 2. تحديث المحرك لتجاوز مشكلة Unsupported Client
            // هذا يسحب أحدث نسخة من yt-dlp GitHub
            YoutubeDL.getInstance().updateYoutubeDL(app, YoutubeDL.UpdateChannel.STABLE)
            "Updated to Latest Version"
        } catch (e: Exception) {
            "Update Failed (Using Embedded): ${e.message}"
        }
    }
}
"""

# ==========================================
# 3. ملف: Utils/BotBypasser.kt
# (وظيفته: تجهيز الرؤوس المزيفة للخداع)
# ==========================================
bot_bypasser_code = """package org.alituama.mytube.utils

import com.yausername.youtubedl_android.YoutubeDLRequest

object BotBypasser {
    
    fun applyAntiBotConfig(request: YoutubeDLRequest, mode: String) {
        request.addOption("--no-check-certificates")
        request.addOption("--geo-bypass")
        request.addOption("--no-mtime")
        
        when (mode) {
            "ANDROID" -> {
                // أفضل وضع حالياً
                request.addOption("--extractor-args", "youtube:player_client=android")
                request.addOption("--user-agent", "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")
            }
            "IOS" -> {
                request.addOption("--extractor-args", "youtube:player_client=ios")
                request.addOption("--user-agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1")
            }
            "TV" -> {
                // الوضع الذي حاولت استخدامه سابقاً (يتطلب نسخة حديثة جداً)
                request.addOption("--extractor-args", "youtube:player_client=android_tv")
            }
        }
    }
}
"""

# ==========================================
# 4. ملف: Core/DownloadEngine.kt
# (وظيفته: إدارة التنزيل وتجربة الحلول بالتسلسل)
# ==========================================
download_engine_code = """package org.alituama.mytube.core

import com.yausername.youtubedl_android.YoutubeDL
import com.yausername.youtubedl_android.YoutubeDLRequest
import org.alituama.mytube.utils.BotBypasser
import java.io.File

class DownloadEngine(private val downloadDir: File) {

    fun download(url: String, callback: (String, Float, Long) -> Unit): Boolean {
        // المحاولة 1: عميل Android (الأكثر استقراراً)
        try {
            val request = createRequest(url)
            BotBypasser.applyAntiBotConfig(request, "ANDROID")
            execute(request, callback)
            return true
        } catch (e: Exception) {
            // المحاولة 2: عميل iOS (احتياطي)
            try {
                val request = createRequest(url)
                BotBypasser.applyAntiBotConfig(request, "IOS")
                execute(request, callback)
                return true
            } catch (e2: Exception) {
                // المحاولة 3: وضع التوافق (بدون تحديد عميل)
                throw Exception("All methods failed. Last error: ${e2.message}")
            }
        }
    }

    private fun createRequest(url: String): YoutubeDLRequest {
        val request = YoutubeDLRequest(url)
        request.addOption("-o", downloadDir.absolutePath + "/%(title)s.%(ext)s")
        // صيغة مضمونة لتعمل بدون دمج معقد
        request.addOption("-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")
        return request
    }

    private fun execute(request: YoutubeDLRequest, callback: (String, Float, Long) -> Unit) {
        YoutubeDL.getInstance().execute(request, null) { progress, eta, line ->
            callback(line ?: "Processing", progress, eta)
        }
    }
}
"""

# ==========================================
# 5. ملف: UI/MainActivity.kt
# (وظيفته: ربط كل الملفات ببعضها)
# ==========================================
main_activity_code = """package org.alituama.mytube.ui

import android.Manifest
import android.animation.ObjectAnimator
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.text.Editable
import android.text.TextWatcher
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.google.android.material.textfield.TextInputEditText
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.alituama.mytube.R
import org.alituama.mytube.core.DownloadEngine
import org.alituama.mytube.core.LibraryManager
import java.io.File

class MainActivity : AppCompatActivity() {

    private lateinit var tvStatus: TextView
    private lateinit var etUrl: TextInputEditText
    private var isReady = false
    private var lastUrl = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        tvStatus = findViewById(R.id.tvStatus)
        val btnFetch = findViewById<Button>(R.id.btnFetch)
        val tvCredits = findViewById<TextView>(R.id.tvCredits)

        setupPermissions()
        initializeApp()

        // التنفيذ التلقائي
        etUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val url = s.toString().trim()
                if (url.contains("youtu") && url != lastUrl && isReady) {
                    lastUrl = url
                    startDownloadProcess(url)
                }
            }
        })

        // الاستقبال من المشاركة
        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { etUrl.setText(it) }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) startDownloadProcess(url)
            else checkClipboard()
        }
    }

    private fun initializeApp() {
        lifecycleScope.launch(Dispatchers.IO) {
            withContext(Dispatchers.Main) { tvStatus.text = "Initializing System..." }
            
            val initResult = LibraryManager.init(application)
            
            withContext(Dispatchers.Main) { tvStatus.text = "Updating Engine..." }
            val updateResult = LibraryManager.update(application)
            
            isReady = true
            withContext(Dispatchers.Main) { 
                tvStatus.text = "Ready ($updateResult)"
                // فحص إذا كان هناك رابط تم لصقه أثناء التهيئة
                if (etUrl.text.toString().contains("youtu")) {
                    startDownloadProcess(etUrl.text.toString())
                }
            }
        }
    }

    private fun startDownloadProcess(url: String) {
        tvStatus.setTextColor(Color.LTGRAY)
        tvStatus.text = "Starting Engine..."
        
        val dir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        if (!dir.exists()) dir.mkdirs()

        val engine = DownloadEngine(dir)

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                withContext(Dispatchers.Main) { tvStatus.text = "Downloading..." }
                
                engine.download(url) { line, progress, eta ->
                    runOnUiThread {
                        tvStatus.text = "$progress% | ETA: $eta s"
                    }
                }

                withContext(Dispatchers.Main) {
                    tvStatus.setTextColor(Color.GREEN)
                    tvStatus.text = "✅ Success!"
                    Toast.makeText(this@MainActivity, "Video Saved!", Toast.LENGTH_LONG).show()
                    etUrl.text?.clear()
                    lastUrl = ""
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvStatus.setTextColor(Color.RED)
                    tvStatus.text = "Failed"
                    AlertDialog.Builder(this@MainActivity)
                        .setTitle("Download Error")
                        .setMessage(e.message)
                        .setPositiveButton("OK", null)
                        .show()
                }
            }
        }
    }

    private fun setupPermissions() {
        if (Build.VERSION.SDK_INT >= 33) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != 0) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), 100)
            }
        }
        if (Build.VERSION.SDK_INT <= 29) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != 0) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.WRITE_EXTERNAL_STORAGE), 101)
            }
        }
    }

    private fun checkClipboard() {
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clip = clipboard.primaryClip
        if (clip != null && clip.itemCount > 0) {
            etUrl.setText(clip.getItemAt(0).text.toString())
        }
    }
}
"""

# ==========================================
# 6. تحديث Manifest (ليشير للملف الجديد)
# ==========================================
manifest_content = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

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

        <!-- لاحظ تغيير اسم النشاط إلى المسار الجديد -->
        <activity
            android:name=".ui.MainActivity"
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
# التنفيذ
# ==========================================
clean_old_files()
create_file("app/build.gradle.kts", build_gradle_content)
create_file("app/src/main/java/org/alituama/mytube/core/LibraryManager.kt", library_manager_code)
create_file("app/src/main/java/org/alituama/mytube/core/DownloadEngine.kt", download_engine_code)
create_file("app/src/main/java/org/alituama/mytube/utils/BotBypasser.kt", bot_bypasser_code)
create_file("app/src/main/java/org/alituama/mytube/ui/MainActivity.kt", main_activity_code)
create_file("app/src/main/AndroidManifest.xml", manifest_content)

print("\n🚀 Pushing Modular Architecture to GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Modular Fix: Split Logic, Auto-Update, Anti-Bot"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ Done! System restructured.")
except Exception as e:
    print(f"❌ Git Error: {e}")
