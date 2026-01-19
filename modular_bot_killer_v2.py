import os
import shutil
import subprocess  # ✅ تمت إضافتها لضمان عمل أوامر Git

# ==========================================
# أدوات النظام
# ==========================================
def create_file(path, content):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Created Module: {path}")

def clean_structure():
    # تنظيف الكود القديم لضمان عدم التعارض
    paths_to_clean = [
        "app/src/main/java/org/alituama/mytube/MainActivity.kt",
        "app/src/main/java/org/alituama/mytube/core",
        "app/src/main/java/org/alituama/mytube/utils",
        "app/src/main/java/org/alituama/mytube/ui",
        "app/src/main/java/org/alituama/mytube/strategy"
    ]
    for p in paths_to_clean:
        if os.path.exists(p):
            if os.path.isdir(p): shutil.rmtree(p)
            else: os.remove(p)
    print("🧹 Old architecture cleaned.")

# ==========================================
# 1. إعداد Gradle
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
        versionCode = 5
        versionName = "5.0"
        
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
    
    // استخدام النسخة 0.17.2 المستقرة
    implementation("io.github.junkfood02.youtubedl-android:library:0.17.2")
    implementation("io.github.junkfood02.youtubedl-android:ffmpeg:0.17.2") 
    
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
}
"""

# ==========================================
# 2. ملف: Utils/PermissionHelper.kt
# ==========================================
permission_helper_code = """package org.alituama.mytube.utils

import android.Manifest
import android.app.Activity
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

object PermissionHelper {
    private const val REQ_CODE = 100

    fun checkAndRequest(activity: Activity) {
        val permissions = mutableListOf<String>()
        
        if (Build.VERSION.SDK_INT >= 33) {
            if (ContextCompat.checkSelfPermission(activity, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                permissions.add(Manifest.permission.POST_NOTIFICATIONS)
            }
        }
        
        if (Build.VERSION.SDK_INT <= 29) {
            if (ContextCompat.checkSelfPermission(activity, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                permissions.add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
            }
        }

        if (permissions.isNotEmpty()) {
            ActivityCompat.requestPermissions(activity, permissions.toTypedArray(), REQ_CODE)
        }
    }
}
"""

# ==========================================
# 3. ملف: Core/LibraryManager.kt
# ==========================================
library_manager_code = """package org.alituama.mytube.core

import android.app.Application
import android.util.Log
import com.yausername.youtubedl_android.YoutubeDL

object LibraryManager {
    fun initialize(app: Application): Boolean {
        return try {
            YoutubeDL.getInstance().init(app)
            try {
                YoutubeDL.getInstance().updateYoutubeDL(app, YoutubeDL.UpdateChannel.STABLE)
            } catch (e: Exception) {
                Log.w("MyTube", "Update failed, using embedded version")
            }
            true
        } catch (e: Exception) {
            Log.e("MyTube", "Init failed", e)
            false
        }
    }
}
"""

# ==========================================
# 4. ملف: Strategy/AntiBotStrategy.kt
# ==========================================
anti_bot_code = """package org.alituama.mytube.strategy

import com.yausername.youtubedl_android.YoutubeDLRequest

enum class ClientMode {
    ANDROID_MUSIC,
    ANDROID_MAIN,
    IOS,
    TV_EMBEDDED
}

object AntiBotStrategy {
    
    fun configureRequest(request: YoutubeDLRequest, mode: ClientMode) {
        request.addOption("--no-check-certificates")
        request.addOption("--geo-bypass")
        request.addOption("--no-mtime")
        request.addOption("--compat-options", "no-youtube-unavailable-videos")

        when (mode) {
            ClientMode.ANDROID_MUSIC -> {
                request.addOption("--extractor-args", "youtube:player_client=android_music")
                request.addOption("--user-agent", "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")
            }
            ClientMode.ANDROID_MAIN -> {
                request.addOption("--extractor-args", "youtube:player_client=android")
            }
            ClientMode.IOS -> {
                request.addOption("--extractor-args", "youtube:player_client=ios")
            }
            ClientMode.TV_EMBEDDED -> {
                request.addOption("--extractor-args", "youtube:player_client=android_tv")
            }
        }
    }
}
"""

# ==========================================
# 5. ملف: Core/DownloadManager.kt
# ==========================================
download_manager_code = """package org.alituama.mytube.core

import com.yausername.youtubedl_android.YoutubeDL
import com.yausername.youtubedl_android.YoutubeDLRequest
import org.alituama.mytube.strategy.AntiBotStrategy
import org.alituama.mytube.strategy.ClientMode
import java.io.File

class DownloadManager(private val saveDir: File) {

    fun startDownload(url: String, onProgress: (String) -> Unit, onSuccess: () -> Unit, onError: (String) -> Unit) {
        
        val strategies = listOf(
            ClientMode.ANDROID_MUSIC,
            ClientMode.ANDROID_MAIN,
            ClientMode.IOS,
            ClientMode.TV_EMBEDDED
        )

        var lastError = ""

        for (mode in strategies) {
            try {
                onProgress("Trying Strategy: ${mode.name}...")
                
                val request = YoutubeDLRequest(url)
                request.addOption("-o", saveDir.absolutePath + "/%(title)s.%(ext)s")
                request.addOption("-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")
                
                AntiBotStrategy.configureRequest(request, mode)

                YoutubeDL.getInstance().execute(request, null) { progress, eta, _ ->
                    onProgress("$progress% | ETA: $eta s")
                }
                
                onSuccess()
                return 

            } catch (e: Exception) {
                lastError = e.message ?: "Unknown Error"
                continue
            }
        }
        
        onError("All strategies failed. Last error: $lastError")
    }
}
"""

# ==========================================
# 6. ملف: UI/MainActivity.kt
# ==========================================
main_activity_code = """package org.alituama.mytube.ui

import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.os.Environment
import android.text.Editable
import android.text.TextWatcher
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.google.android.material.textfield.TextInputEditText
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.alituama.mytube.R
import org.alituama.mytube.core.DownloadManager
import org.alituama.mytube.core.LibraryManager
import org.alituama.mytube.utils.PermissionHelper
import java.io.File

class MainActivity : AppCompatActivity() {

    private lateinit var tvStatus: TextView
    private lateinit var etUrl: TextInputEditText
    private var isEngineReady = false
    private var lastProcessedUrl = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        tvStatus = findViewById(R.id.tvStatus)
        val btnFetch = findViewById<Button>(R.id.btnFetch)

        PermissionHelper.checkAndRequest(this)

        lifecycleScope.launch(Dispatchers.IO) {
            withContext(Dispatchers.Main) { tvStatus.text = "Initializing Engine..." }
            isEngineReady = LibraryManager.initialize(application)
            withContext(Dispatchers.Main) { 
                tvStatus.text = if (isEngineReady) "Ready" else "Engine Error"
                if (etUrl.text.toString().contains("youtu")) executeDownload(etUrl.text.toString())
            }
        }

        etUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val url = s.toString().trim()
                if (url.contains("youtu") && url != lastProcessedUrl && isEngineReady) {
                    lastProcessedUrl = url
                    executeDownload(url)
                }
            }
        })

        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { etUrl.setText(it) }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) executeDownload(url)
            else checkClipboard()
        }
    }

    private fun executeDownload(url: String) {
        if (!isEngineReady) return

        val dir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        if (!dir.exists()) dir.mkdirs()

        val manager = DownloadManager(dir)

        lifecycleScope.launch(Dispatchers.IO) {
            manager.startDownload(
                url = url,
                onProgress = { msg ->
                    runOnUiThread { tvStatus.text = msg }
                },
                onSuccess = {
                    runOnUiThread {
                        tvStatus.text = "✅ Download Complete"
                        Toast.makeText(this@MainActivity, "Saved to Downloads", Toast.LENGTH_LONG).show()
                        etUrl.text?.clear()
                        lastProcessedUrl = ""
                    }
                },
                onError = { error ->
                    runOnUiThread {
                        tvStatus.text = "Failed"
                        showError(error)
                    }
                }
            )
        }
    }

    private fun checkClipboard() {
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clip = clipboard.primaryClip
        if (clip != null && clip.itemCount > 0) {
            etUrl.setText(clip.getItemAt(0).text.toString())
        }
    }

    private fun showError(msg: String) {
        AlertDialog.Builder(this)
            .setTitle("Report")
            .setMessage(msg)
            .setPositiveButton("OK", null)
            .show()
    }
}
"""

# ==========================================
# 7. ملف: AndroidManifest.xml
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
# تنفيذ العملية والرفع
# ==========================================
clean_structure()
create_file("app/build.gradle.kts", build_gradle_content)
create_file("app/src/main/java/org/alituama/mytube/utils/PermissionHelper.kt", permission_helper_code)
create_file("app/src/main/java/org/alituama/mytube/core/LibraryManager.kt", library_manager_code)
create_file("app/src/main/java/org/alituama/mytube/strategy/AntiBotStrategy.kt", anti_bot_code)
create_file("app/src/main/java/org/alituama/mytube/core/DownloadManager.kt", download_manager_code)
create_file("app/src/main/java/org/alituama/mytube/ui/MainActivity.kt", main_activity_code)
create_file("app/src/main/AndroidManifest.xml", manifest_content)

print("\n🚀 Pushing Modular Architecture to GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Architecture: Modular Design + Fixed Script Import"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ Pushed successfully!")
except Exception as e:
    print(f"❌ Git Error: {e}")
