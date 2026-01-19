import os
import subprocess

def create_file(path, content):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Executed: {path}")

# ==========================================
# 1. تحديث Gradle (تثبيت البنية التحتية)
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
        versionCode = 3
        versionName = "3.0"
        
        // إجبار النظام على دمج كل المكتبات داخل الـ APK
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
    
    // المكتبة التي تحتوي على الملفات التنفيذية
    implementation("io.github.junkfood02.youtubedl-android:library:0.17.2")
    implementation("io.github.junkfood02.youtubedl-android:ffmpeg:0.17.2") 
    
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
}
"""

# ==========================================
# 2. كود MainActivity (خدعة التلفزيون الذكي)
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
    private var lastUrlProcessed = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        val btnFetch = findViewById<Button>(R.id.btnFetch)
        tvStatus = findViewById(R.id.tvStatus)
        val tvCredits = findViewById<TextView>(R.id.tvCredits)

        animateCredits(tvCredits)
        requestPermissionsSafely()
        
        // تهيئة فورية
        initEngine()

        // التنزيل التلقائي عند اللصق
        etUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val url = s.toString().trim()
                if ((url.contains("youtu.be") || url.contains("youtube.com")) && url != lastUrlProcessed) {
                    if (isLibraryReady) {
                        lastUrlProcessed = url
                        startDownload(url)
                    }
                }
            }
        })

        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { etUrl.setText(it) }
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

    private fun initEngine() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // الخطوة 1: فك الضغط (المفروض ينجح بسبب legacyPackaging)
                YoutubeDL.getInstance().init(application)
                
                // الخطوة 2: تحديث إجباري للمحرك
                withContext(Dispatchers.Main) { tvStatus.text = "Checking Engine..." }
                try {
                    YoutubeDL.getInstance().updateYoutubeDL(application, YoutubeDL.UpdateChannel.STABLE)
                } catch (e: Exception) {
                    Log.w("MyTube", "Update failed, using embedded version")
                }

                isLibraryReady = true
                withContext(Dispatchers.Main) { 
                    tvStatus.text = "Ready (TV Mode)"
                    if (etUrl.text.toString().contains("youtu")) {
                        startDownload(etUrl.text.toString())
                    }
                }
            } catch (e: Exception) {
                // إذا فشل كل شيء، نعيد المحاولة
                isLibraryReady = true 
                withContext(Dispatchers.Main) { 
                    tvStatus.text = "Engine Warning (Trying anyway)" 
                }
            }
        }
    }

    private fun startDownload(url: String) {
        tvStatus.setTextColor(Color.LTGRAY) 
        tvStatus.text = "Processing (TV Mode)..."
        
        val downloadDir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        if (!downloadDir.exists()) downloadDir.mkdirs()

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val request = YoutubeDLRequest(url)
                
                // ==========================================================
                // ☢️ الحل النووي: وضع التلفزيون (ANDROID_TV) ☢️
                // هذا الوضع لا يطلب JS ولا يتحقق من البوت
                // ==========================================================
                request.addOption("--extractor-args", "youtube:player_client=android_tv")
                
                // تعطيل التحقق من الشهادات (يحل مشاكل الاتصال)
                request.addOption("--no-check-certificates")
                
                // اختيار أفضل صيغة تلقائياً (لحل مشكلة best pre-merged)
                request.addOption("-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")
                
                // حفظ الملف
                request.addOption("-o", downloadDir.absolutePath + "/%(title)s.%(ext)s")

                withContext(Dispatchers.Main) { tvStatus.text = "Downloading..." }

                YoutubeDL.getInstance().execute(request, null) { progress, eta, line ->
                    runOnUiThread { tvStatus.text = "$progress% | ETA: $eta s" }
                }

                withContext(Dispatchers.Main) {
                    tvStatus.setTextColor(Color.GREEN)
                    tvStatus.text = "✅ Done! Saved in Downloads/MyTube"
                    Toast.makeText(this@MainActivity, "Download Complete!", Toast.LENGTH_LONG).show()
                    etUrl.text?.clear() 
                    lastUrlProcessed = ""
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    // إذا فشل وضع التلفزيون، نجرب وضع الويب القديم كخطة طوارئ
                    tvStatus.text = "Retrying (Legacy Mode)..."
                    retryLegacy(url, downloadDir, e.message ?: "")
                }
            }
        }
    }

    private fun retryLegacy(url: String, dir: File, error: String) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val request = YoutubeDLRequest(url)
                // استخدام عميل الويب العادي بدون تعقيدات
                request.addOption("--extractor-args", "youtube:player_client=web")
                request.addOption("-f", "best")
                request.addOption("-o", dir.absolutePath + "/%(title)s.%(ext)s")
                
                YoutubeDL.getInstance().execute(request, null) { progress, eta, line ->
                    runOnUiThread { tvStatus.text = "Legacy: $progress%" }
                }
                
                withContext(Dispatchers.Main) {
                     tvStatus.setTextColor(Color.GREEN)
                     tvStatus.text = "✅ Done (Legacy)"
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvStatus.setTextColor(Color.RED)
                    tvStatus.text = "Failed"
                    showErrorDialog("Both methods failed.\\n1. TV Mode: $error\\n2. Legacy: ${e.message}")
                }
            }
        }
    }

    private fun checkClipboard() {
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clipData = clipboard.primaryClip
        if (clipData != null && clipData.itemCount > 0) {
            val pasteText = clipData.getItemAt(0).text.toString()
            etUrl.setText(pasteText)
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
            .setTitle("Error Report")
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
    create_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", kotlin_content)
    
    print("\n🚀 Injecting Nuclear TV-Mode Fix...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Nuclear Fix: Use Android TV Client to bypass Bot Check"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! The app will now mimic a Smart TV.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
