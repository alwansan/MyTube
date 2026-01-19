import os
import subprocess

# ==========================================
# دالة مساعدة
# ==========================================
def create_file(path, content):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Updated: {path}")

# ==========================================
# 1. تحديث build.gradle.kts (إجبار تضمين الملفات)
# ==========================================
# التغيير المهم: إضافة ndk abiFilters و isUniversalApk
# هذا يجعل الـ APK كبيراً قليلاً لكنه يحتوي على كل شيء ولا يحتاج للإنترنت
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
        
        // 🔴 هام جداً: إجبار Gradle على تضمين ملفات التشغيل لكل المعالجات
        ndk {
            abiFilters.add("armeabi-v7a")
            abiFilters.add("arm64-v8a")
            abiFilters.add("x86")
            abiFilters.add("x86_64")
        }
    }

    // منع تقسيم الـ APK لضمان وجود كل الملفات في ملف واحد
    splits {
        abi {
            isEnable = false
            reset()
            include("armeabi-v7a", "arm64-v8a", "x86", "x86_64")
            isUniversalApk = true
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
    
    // هذه المكتبات تحتوي على الملفات المدمجة (Offline Bundle)
    implementation("io.github.junkfood02.youtubedl-android:library:0.17.2")
    implementation("io.github.junkfood02.youtubedl-android:ffmpeg:0.17.2") 
    
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
}
"""

# ==========================================
# 2. تحديث MainActivity.kt (إظهار الخطأ الحقيقي)
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

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val etUrl = findViewById<TextInputEditText>(R.id.etUrl)
        val btnFetch = findViewById<Button>(R.id.btnFetch)
        tvStatus = findViewById(R.id.tvStatus)
        val tvCredits = findViewById<TextView>(R.id.tvCredits)

        animateCredits(tvCredits)
        checkAndRequestPermissions()

        // 🟢 التهيئة الفورية عند فتح التطبيق
        // هذه العملية لا تحمل شيئاً، فقط تفك الضغط
        initLibrary()

        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            val sharedText = intent.getStringExtra(Intent.EXTRA_TEXT)
            if (sharedText != null) {
                etUrl.setText(sharedText)
            }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) {
                startDownload(url)
            } else {
                val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                val clipData = clipboard.primaryClip
                if (clipData != null && clipData.itemCount > 0) {
                    val pasteText = clipData.getItemAt(0).text.toString()
                    etUrl.setText(pasteText)
                    startDownload(pasteText)
                }
            }
        }
    }

    private fun initLibrary() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // هذا الأمر يفك ضغط الملفات المدمجة فقط
                YoutubeDL.getInstance().init(application)
                withContext(Dispatchers.Main) {
                    tvStatus.text = "Ready (Offline Mode)"
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvStatus.text = "Error: Library Init Failed"
                    showErrorDialog("Failed to extract built-in files.\\nError: ${e.message}\\nMake sure the APK includes native libs.")
                }
            }
        }
    }

    private fun showErrorDialog(msg: String) {
        AlertDialog.Builder(this)
            .setTitle("Initialization Error")
            .setMessage(msg)
            .setPositiveButton("OK", null)
            .show()
    }

    private fun startDownload(url: String) {
        tvStatus.text = "Processing..."
        
        val downloadDir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        if (!downloadDir.exists()) downloadDir.mkdirs()

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val request = YoutubeDLRequest(url)
                request.addOption("-o", downloadDir.absolutePath + "/%(title)s.%(ext)s")
                request.addOption("-f", "bestvideo+bestaudio/best")
                
                withContext(Dispatchers.Main) {
                    tvStatus.text = "Downloading..."
                }

                YoutubeDL.getInstance().execute(request, null) { progress, eta, line ->
                    runOnUiThread {
                        tvStatus.text = "$progress% | ETA: $eta s"
                    }
                }

                withContext(Dispatchers.Main) {
                    tvStatus.text = "✅ Done! Check Downloads"
                    Toast.makeText(this@MainActivity, "Saved!", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvStatus.text = "Failed"
                    showErrorDialog("Download Error:\\n${e.message}")
                }
            }
        }
    }

    private fun checkAndRequestPermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), PERMISSION_REQUEST_CODE)
            }
        }
        if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.Q) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.WRITE_EXTERNAL_STORAGE), PERMISSION_REQUEST_CODE)
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

if __name__ == "__main__":
    create_file("app/build.gradle.kts", build_gradle_content)
    create_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", kotlin_content)
    
    print("\n🚀 Pushing Offline-Ready Update...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Force Universal APK (Offline Ready)"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! The new APK will be larger but will include ALL necessary files.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
