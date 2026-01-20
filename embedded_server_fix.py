import os
import shutil
import subprocess

def create_file(path, content):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Created: {path}")

def clean_old_files():
    # تنظيف شامل لضمان عدم وجود بقايا من نظام API القديم
    paths = [
        "app/src/main/java/org/alituama/mytube/core",
        "app/src/main/java/org/alituama/mytube/utils",
        "app/src/main/java/org/alituama/mytube/strategy",
        "app/src/main/java/org/alituama/mytube/ui"
    ]
    for p in paths:
        if os.path.exists(p): shutil.rmtree(p)
    print("🧹 Workspace cleaned for Local Server Mode.")

# ==========================================
# 1. تصميم الأيقونة (السهم السيرياني)
# ==========================================
icon_background = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#0D0D0D"
        android:pathData="M0,0h108v108h-108z" />
</vector>
"""

icon_foreground = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:strokeWidth="3"
        android:strokeColor="#D4AF37"
        android:fillColor="#00000000"
        android:strokeLineJoin="round"
        android:strokeLineCap="round"
        android:pathData="M38,45 L38,15 L70,15 L70,45 L88,45 L54,85 L20,45 Z" />
    <path
        android:fillColor="#D4AF37"
        android:pathData="M54,35 a3,3 0 1,0 6,0 a3,3 0 1,0 -6,0" />
</vector>
"""

# ==========================================
# 2. Gradle (إعداد المحرك المحلي الثقيل)
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
        versionCode = 15
        versionName = "15.0"
        
        // ضروري جداً لعمل المحرك المحلي على كل الهواتف
        ndk {
            abiFilters.add("armeabi-v7a")
            abiFilters.add("arm64-v8a")
            abiFilters.add("x86")
            abiFilters.add("x86_64")
        }
    }

    packaging {
        jniLibs {
            useLegacyPackaging = true // يمنع ضغط ملفات السيرفر
        }
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false // تعطيل التصغير لضمان عمل كود البايثون
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    kotlinOptions { jvmTarget = "1.8" }
    buildFeatures { viewBinding = true }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    
    // محرك yt-dlp المدمج (السيرفر المحلي)
    // نستخدم مكتبة junkfood02 لأنها تدعم بايثون 3.8+ المدمج
    implementation("io.github.junkfood02.youtubedl-android:library:0.17.2")
    implementation("io.github.junkfood02.youtubedl-android:ffmpeg:0.17.2") 
    
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
}
"""

# ==========================================
# 3. MainActivity (مشغل السيرفر المحلي)
# ==========================================
main_activity_code = """package org.alituama.mytube

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
import android.text.Editable
import android.text.TextWatcher
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
    private lateinit var etUrl: TextInputEditText
    private lateinit var tvCredits: TextView
    private var isServerRunning = false
    private var lastUrl = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        tvStatus = findViewById(R.id.tvStatus)
        tvCredits = findViewById(R.id.tvCredits)
        val btnFetch = findViewById<Button>(R.id.btnFetch)

        startAnimations()
        checkPermissions()

        // 1. تشغيل السيرفر المحلي عند الفتح
        bootLocalServer()

        etUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val url = s.toString().trim()
                if (url.length > 10 && (url.contains("http") || url.contains("youtu")) && url != lastUrl) {
                    processLocalRequest(url)
                }
            }
        })

        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { etUrl.setText(it) }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) processLocalRequest(url)
            else checkClipboard()
        }
    }

    private fun bootLocalServer() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                withContext(Dispatchers.Main) { tvStatus.text = "Booting Local Server..." }
                
                // هذه الخطوة تقوم بفك ضغط ملفات بايثون و ffmpeg داخل الهاتف
                YoutubeDL.getInstance().init(application)
                
                // محاولة تحديث السيرفر الداخلي إذا توفر نت (اختياري)
                try {
                    YoutubeDL.getInstance().updateYoutubeDL(application, YoutubeDL.UpdateChannel.STABLE)
                } catch (e: Exception) {
                    Log.w("Server", "Offline mode active")
                }

                isServerRunning = true
                withContext(Dispatchers.Main) { 
                    tvStatus.text = "Server Ready (Local)"
                    if (etUrl.text.toString().contains("http")) {
                        processLocalRequest(etUrl.text.toString())
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) { 
                    tvStatus.text = "Server Boot Failed"
                    showError("Could not start local engine.\\nReason: ${e.message}")
                }
            }
        }
    }

    private fun processLocalRequest(url: String) {
        if (!isServerRunning) {
            Toast.makeText(this, "Waiting for server...", Toast.LENGTH_SHORT).show()
            return
        }
        
        lastUrl = url
        tvStatus.setTextColor(Color.LTGRAY)
        tvStatus.text = "Processing Locally..."
        
        val downloadDir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        if (!downloadDir.exists()) downloadDir.mkdirs()

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val request = YoutubeDLRequest(url)
                request.addOption("-o", downloadDir.absolutePath + "/%(title)s.%(ext)s")
                
                // =======================================================
                // 🛑 إعدادات السيرفر المحلي لتجاوز الحظر (2026)
                // =======================================================
                
                // 1. استخدام عميل أندرويد الرسمي (API)
                // هذا يمنع يوتيوب من طلب جافا سكريبت أو التحقق من البوت
                request.addOption("--extractor-args", "youtube:player_client=android")
                
                // 2. إجبار تخطي فحص JS (لأنه غير موجود في بيئة بايثون الأندرويد)
                request.addOption("--extractor-args", "youtube:player_skip=js")
                
                // 3. صيغة الفيديو (MP4)
                request.addOption("-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")
                
                // 4. إعدادات الشبكة
                request.addOption("--no-check-certificates")
                request.addOption("--geo-bypass")
                
                // 5. User Agent حقيقي لهاتف أندرويد
                request.addOption("--user-agent", "com.google.android.youtube/19.09.37 (Linux; Android 14) gzip")

                withContext(Dispatchers.Main) { tvStatus.text = "Downloading..." }

                YoutubeDL.getInstance().execute(request, null) { progress, eta, line ->
                    val p = progress.toInt()
                    val e = eta.toInt()
                    runOnUiThread { 
                        tvStatus.text = "DL: $p% | ETA: ${e}s" 
                    }
                }

                withContext(Dispatchers.Main) {
                    tvStatus.setTextColor(Color.GREEN)
                    tvStatus.text = "✅ Done (Local)"
                    Toast.makeText(this@MainActivity, "Saved to Downloads/MyTube", Toast.LENGTH_LONG).show()
                    etUrl.text?.clear()
                    lastUrl = ""
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvStatus.setTextColor(Color.RED)
                    tvStatus.text = "Failed"
                    showError("Local Server Error:\\n${e.message}")
                }
            }
        }
    }

    private fun startAnimations() {
        val colorAnim = ObjectAnimator.ofInt(tvCredits, "textColor",
            Color.parseColor("#D4AF37"), 
            Color.parseColor("#262626"), 
            Color.parseColor("#D4AF37"))
        colorAnim.setDuration(4000)
        colorAnim.setEvaluator(ArgbEvaluator())
        colorAnim.repeatCount = ObjectAnimator.INFINITE
        colorAnim.start()
    }

    private fun checkPermissions() {
        if (Build.VERSION.SDK_INT >= 33 && ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != 0) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), 100)
        }
        if (Build.VERSION.SDK_INT <= 29 && ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != 0) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.WRITE_EXTERNAL_STORAGE), 101)
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

if __name__ == "__main__":
    clean_old_files()
    
    # إنشاء الملفات
    create_file("app/src/main/res/drawable/ic_launcher_background.xml", icon_background)
    create_file("app/src/main/res/drawable/ic_launcher_foreground.xml", icon_foreground)
    create_file("app/build.gradle.kts", build_gradle_content)
    create_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", main_activity_code)
    
    print("\n🚀 Pushing Embedded Server Solution...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Final Solution: Embedded Local Server (No API Dependency)"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! App will now contain its own engine.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
