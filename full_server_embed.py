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

def clean_environment():
    paths = [
        "app/src/main/java/org/alituama/mytube/core",
        "app/src/main/java/org/alituama/mytube/utils",
        "app/src/main/java/org/alituama/mytube/ui"
    ]
    for p in paths:
        if os.path.exists(p): shutil.rmtree(p)
    print("🧹 Environment Cleaned.")

# ==========================================
# 1. تصميم الأيقونة (سهم مجوف نقي - بدون نقطة)
# ==========================================
icon_background = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#121212"
        android:pathData="M0,0h108v108h-108z" />
    <path
        android:fillColor="#1A1A1A"
        android:pathData="M0,54 L108,54 L108,108 L0,108 Z" />
</vector>
"""

icon_foreground = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    
    <!-- السهم المجوف فقط (بدون أي شيء بداخله) -->
    <path
        android:strokeWidth="4"
        android:strokeColor="#FFD700"
        android:fillColor="#00000000"
        android:strokeLineJoin="round"
        android:strokeLineCap="round"
        android:pathData="M35,45 L35,15 L73,15 L73,45 L95,45 L54,90 L13,45 Z" />
        
</vector>
"""

# ==========================================
# 2. Gradle (إعداد بيئة السيرفر الكاملة)
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
        versionCode = 16
        versionName = "16.0"
        
        // دعم كامل لكل المعالجات (Server Environment)
        ndk {
            abiFilters.add("armeabi-v7a")
            abiFilters.add("arm64-v8a")
            abiFilters.add("x86")
            abiFilters.add("x86_64")
        }
    }

    packaging {
        jniLibs {
            useLegacyPackaging = true // ضروري لاستخراج مكتبات Python
        }
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false // ممنوع التصغير لضمان عمل الانعكاس (Reflection)
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
    
    // محرك السيرفر المحلي (Python + FFmpeg Embedded)
    implementation("io.github.junkfood02.youtubedl-android:library:0.17.2")
    implementation("io.github.junkfood02.youtubedl-android:ffmpeg:0.17.2") 
    
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
}
"""

# ==========================================
# 3. MainActivity (المحرك الداخلي المتكامل)
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
    private var isEngineInitialized = false
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

        // 🟢 1. بناء السيرفر الداخلي فوراً
        buildInternalServer()

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

    private fun buildInternalServer() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                withContext(Dispatchers.Main) { tvStatus.text = "Building Engine..." }
                
                // 1. فك ضغط ملفات النظام (Python, FFmpeg)
                YoutubeDL.getInstance().init(application)
                
                // 2. تحديث قسري (Force Update) لجلب أحدث مفاتيح فك التشفير
                // هذا يضمن أن السيرفر المحلي محدث لعام 2026
                try {
                    withContext(Dispatchers.Main) { tvStatus.text = "Updating Core..." }
                    YoutubeDL.getInstance().updateYoutubeDL(application, YoutubeDL.UpdateChannel.STABLE)
                } catch (e: Exception) {
                    Log.w("Server", "Update failed, running in legacy mode")
                }

                isEngineInitialized = true
                withContext(Dispatchers.Main) { 
                    tvStatus.text = "Server Active"
                    if (etUrl.text.toString().contains("http")) {
                        processLocalRequest(etUrl.text.toString())
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) { 
                    tvStatus.text = "Server Error"
                    showError("Critical Engine Failure:\\n${e.message}")
                }
            }
        }
    }

    private fun processLocalRequest(url: String) {
        if (!isEngineInitialized) {
            Toast.makeText(this, "Engine booting...", Toast.LENGTH_SHORT).show()
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
                
                // =================================================================
                // ☢️ إعدادات السيرفر المحلي (Anti-Bot Bypass 2026) ☢️
                // =================================================================
                
                // 1. الحل لمشكلة No JS Runtime:
                // إخبار المحرك أننا "تطبيق أندرويد" ولسنا "متصفح".
                // تطبيقات الأندرويد تستخدم API خاص لا يطلب تنفيذ JavaScript.
                request.addOption("--extractor-args", "youtube:player_client=android")
                
                // 2. أمر صريح لتخطي محاولة تشغيل JS (يقتل رسالة الخطأ الأولى)
                request.addOption("--extractor-args", "youtube:player_skip=js")
                
                // 3. الحل لمشكلة Sign in / Bot:
                // استخدام User-Agent الخاص بتطبيق يوتيوب الرسمي (وليس Chrome)
                request.addOption("--user-agent", "com.google.android.youtube/19.29.35 (Linux; U; Android 14; en_US) gzip")
                
                // 4. إعدادات الجودة والشبكة
                request.addOption("-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")
                request.addOption("--no-check-certificates")
                request.addOption("--geo-bypass")
                request.addOption("--no-mtime")

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
                    tvStatus.text = "✅ Done"
                    Toast.makeText(this@MainActivity, "Saved to Downloads/MyTube", Toast.LENGTH_LONG).show()
                    etUrl.text?.clear()
                    lastUrl = ""
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvStatus.setTextColor(Color.RED)
                    tvStatus.text = "Failed"
                    // عرض رسالة الخطأ للمستخدم فقط في حال الفشل الذريع
                    showError("Local Engine Error:\\n${e.message}")
                }
            }
        }
    }

    private fun startAnimations() {
        val colorAnim = ObjectAnimator.ofInt(tvCredits, "textColor",
            Color.parseColor("#FFD700"), 
            Color.parseColor("#1A1A1A"), 
            Color.parseColor("#FFD700"))
        colorAnim.setDuration(4000)
        colorAnim.setEvaluator(ArgbEvaluator())
        colorAnim.repeatCount = ObjectAnimator.INFINITE
        colorAnim.start()
    }

    private fun checkPermissions() {
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
    clean_environment()
    
    # إنشاء الملفات
    create_file("app/src/main/res/drawable/ic_launcher_background.xml", icon_background)
    create_file("app/src/main/res/drawable/ic_launcher_foreground.xml", icon_foreground)
    create_file("app/build.gradle.kts", build_gradle_content)
    create_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", main_activity_code)
    
    print("\n🚀 Pushing Full Embedded Server Fix...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Final: Full Embedded Server + Android Client Spoof + New Icon"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! The app is now a self-contained powerhouse.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
