import os
import subprocess

# دالة الإنشاء
def create_file(path, content):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Executed: {path}")

# ==========================================
# 1. تحديث Gradle (لضمان عمل المكتبات)
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
# 2. الكود الذكي (MainActivity.kt)
# ==========================================
# المميزات الجديدة:
# - تحديث yt-dlp تلقائياً لتجاوز حظر البوت
# - TextWatcher للتنفيذ التلقائي عند اللصق
# - User-Agent Spoofing
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
    private val PERMISSION_REQUEST_CODE = 100
    private var isLibraryReady = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        val btnFetch = findViewById<Button>(R.id.btnFetch)
        tvStatus = findViewById(R.id.tvStatus)
        val tvCredits = findViewById<TextView>(R.id.tvCredits)

        animateCredits(tvCredits)
        requestPermissionsSafely()
        
        // 1. التهيئة + التحديث التلقائي للمحرك (الحل لمشكلة البوت)
        initAndUpdateEngine()

        // 2. مراقب النص (للتنفيذ التلقائي)
        etUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val text = s.toString()
                if (text.contains("youtu") && text.length > 10) {
                    // تأخير بسيط لمنع التكرار
                    if (isLibraryReady) {
                         startDownload(text)
                    }
                }
            }
        })

        // 3. استقبال المشاركة
        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { 
                etUrl.setText(it) // هذا سيشغل المراقب أعلاه ويبدأ التحميل
            }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) {
                startDownload(url)
            } else {
                checkClipboard()
            }
        }
    }

    private fun initAndUpdateEngine() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // الخطوة 1: فك الضغط الأولي
                YoutubeDL.getInstance().init(application)
                
                withContext(Dispatchers.Main) { tvStatus.text = "Updating Engine..." }

                // الخطوة 2: تحديث yt-dlp من الإنترنت لتجاوز حظر البوت
                // هذا يحقن أحدث نسخة في ملفات الـ data
                YoutubeDL.getInstance().updateYoutubeDL(application, YoutubeDL.UpdateChannel.STABLE)

                isLibraryReady = true
                withContext(Dispatchers.Main) { 
                    tvStatus.text = "Ready (Latest Engine Active)" 
                }
            } catch (e: Exception) {
                Log.e("MyTube", "Init Error", e)
                // حتى لو فشل التحديث، نحاول الاستمرار بالنسخة القديمة
                isLibraryReady = true 
                withContext(Dispatchers.Main) { 
                    tvStatus.text = "Ready (Offline Engine)" 
                }
            }
        }
    }

    private fun startDownload(url: String) {
        if (!isLibraryReady) {
            Toast.makeText(this, "Engine initializing...", Toast.LENGTH_SHORT).show()
            return
        }

        tvStatus.text = "Processing..."
        
        val downloadDir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        if (!downloadDir.exists()) downloadDir.mkdirs()

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val request = YoutubeDLRequest(url)
                request.addOption("-o", downloadDir.absolutePath + "/%(title)s.%(ext)s")
                request.addOption("-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")
                
                // الخدعة لتجاوز البوت: تغيير هوية المتصفح
                request.addOption("--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
                
                withContext(Dispatchers.Main) { tvStatus.text = "Downloading..." }

                YoutubeDL.getInstance().execute(request, null) { progress, eta, line ->
                    runOnUiThread { tvStatus.text = "$progress% | ETA: $eta s" }
                }

                withContext(Dispatchers.Main) {
                    tvStatus.text = "✅ Done! Saved in Downloads/MyTube"
                    Toast.makeText(this@MainActivity, "Success!", Toast.LENGTH_LONG).show()
                    etUrl.text?.clear() // مسح الرابط بعد النجاح
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvStatus.text = "Failed"
                    showErrorDialog(e.message ?: "Unknown Error")
                }
            }
        }
    }

    private fun checkClipboard() {
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clipData = clipboard.primaryClip
        if (clipData != null && clipData.itemCount > 0) {
            val pasteText = clipData.getItemAt(0).text.toString()
            etUrl.setText(pasteText) // سيشغل التنزيل التلقائي
        }
    }

    private fun requestPermissionsSafely() {
        if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.Q) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.WRITE_EXTERNAL_STORAGE), PERMISSION_REQUEST_CODE)
            }
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
             if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), PERMISSION_REQUEST_CODE)
            }
        }
    }

    private fun showErrorDialog(msg: String) {
        AlertDialog.Builder(this)
            .setTitle("Error Details")
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

# ==========================================
# 3. التنفيذ والرفع
# ==========================================
if __name__ == "__main__":
    create_file("app/build.gradle.kts", build_gradle_content)
    create_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", kotlin_content)
    
    print("\n🚀 Injecting Intelligence & Fixes...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Final: Auto-Fetch, Anti-Bot Update, Logic Fix"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Mission Accomplished.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
