import os
import subprocess

def create_file(path, content):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Created: {path}")

# ==========================================
# 1. تصميم الأيقونة الجديدة (نجمة مفرغة غامضة)
# ==========================================
# الخلفية: رمادي فحمي داكن جداً (Mysterious Dark)
icon_background = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#121212"
        android:pathData="M0,0h108v108h-108z" />
    <!-- نقش خفيف جداً في الخلفية لإعطاء عمق -->
    <path
        android:fillColor="#1F1F1F"
        android:pathData="M54,0 L108,54 L54,108 L0,54 Z" />
</vector>
"""

# الأمامية: نجمة ذهبية مفرغة (Stroke Only)
icon_foreground = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    
    <!-- النجمة الثمانية المفرغة (حواف فقط) -->
    <path
        android:strokeWidth="2.5"
        android:strokeColor="#FFD700"
        android:fillColor="#00000000"
        android:pathData="M54,12 L62,38 L88,38 L68,54 L76,80 L54,66 L32,80 L40,54 L20,38 L46,38 Z" />
        
    <!-- دائرة غامضة في الوسط (العين) -->
    <path
        android:fillColor="#FFD700"
        android:pathData="M54,51 a3,3 0 1,0 6,0 a3,3 0 1,0 -6,0" />
        
    <!-- خطوط إشعاعية رفيعة جداً -->
    <path
        android:strokeWidth="0.5"
        android:strokeColor="#FFC107"
        android:pathData="M54,12 L54,5 M54,103 L54,96 M12,54 L5,54 M103,54 L96,54" />
</vector>
"""

# ==========================================
# 2. ملف Gradle (التأكد من المكتبات)
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
        versionCode = 12
        versionName = "12.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = true
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
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
}
"""

# ==========================================
# 3. MainActivity (نظام التبديل بين السيرفرات)
# ==========================================
main_activity_code = """package org.alituama.mytube

import android.Manifest
import android.animation.ArgbEvaluator
import android.animation.ObjectAnimator
import android.app.DownloadManager
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.os.Handler
import android.os.Looper
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
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class MainActivity : AppCompatActivity() {

    private lateinit var tvStatus: TextView
    private lateinit var etUrl: TextInputEditText
    private lateinit var tvCredits: TextView
    private var isProcessing = false
    private var lastProcessedUrl = ""
    
    // قائمة السيرفرات البديلة (تتجاوز الحظر)
    // هذه السيرفرات لا تطلب JWT وعادة ما تكون مفتوحة
    private val instances = listOf(
        "https://cobalt.kwiatekmiki.pl",
        "https://cobalt.synced.vip",
        "https://api.cobalt.tools" // الرسمي كاحتياط أخير
    )
    
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        tvStatus = findViewById(R.id.tvStatus)
        tvCredits = findViewById(R.id.tvCredits)
        val btnFetch = findViewById<Button>(R.id.btnFetch)

        startAnimations()
        checkPermissions()

        etUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val url = s.toString().trim()
                if (url.length > 10 && (url.contains("http") || url.contains("youtu")) && url != lastProcessedUrl) {
                    processWithFailover(url)
                }
            }
        })

        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { etUrl.setText(it) }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) processWithFailover(url)
            else checkClipboard()
        }
        
        tvStatus.text = "Ready"
    }

    // المنطق الجديد: التبديل بين السيرفرات
    private fun processWithFailover(url: String) {
        if (isProcessing) return
        isProcessing = true
        lastProcessedUrl = url
        tvStatus.setTextColor(Color.LTGRAY)
        tvStatus.text = "Searching..."

        lifecycleScope.launch(Dispatchers.IO) {
            var success = false
            var lastError = ""

            for (baseUrl in instances) {
                try {
                    withContext(Dispatchers.Main) { tvStatus.text = "Trying Server..." }
                    
                    val apiUrl = "$baseUrl/api/json" // مسار v7/v10 المتوافق
                    
                    val jsonBody = JSONObject()
                    jsonBody.put("url", url)
                    jsonBody.put("vQuality", "720")
                    jsonBody.put("filenamePattern", "basic")

                    val request = Request.Builder()
                        .url(apiUrl)
                        .post(jsonBody.toString().toRequestBody("application/json".toMediaType()))
                        .header("Accept", "application/json")
                        .header("Content-Type", "application/json")
                        .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
                        .build()

                    val response = client.newCall(request).execute()
                    val responseStr = response.body?.string()

                    if (response.isSuccessful && responseStr != null) {
                        val json = JSONObject(responseStr)
                        val status = json.optString("status")
                        
                        if (status == "stream" || status == "redirect" || status == "tunnel") {
                            val downloadUrl = json.optString("url")
                            withContext(Dispatchers.Main) { startSystemDownload(downloadUrl) }
                            success = true
                            break
                        } else if (status == "picker") {
                            val picker = json.optJSONArray("picker")
                            if (picker != null && picker.length() > 0) {
                                val firstUrl = picker.getJSONObject(0).optString("url")
                                withContext(Dispatchers.Main) { startSystemDownload(firstUrl) }
                                success = true
                                break
                            }
                        } else {
                            // إذا كان الخطأ JWT أو Auth، اعتبره فشل وانتقل للسيرفر التالي
                            val err = json.optString("text")
                            if (err.contains("jwt") || err.contains("auth")) {
                                throw Exception("Auth Required")
                            }
                        }
                    } else {
                        // إذا كان الرد 401 أو 403، انتقل للسيرفر التالي
                        if (response.code == 401 || response.code == 403) {
                            throw Exception("Auth Block")
                        }
                    }
                } catch (e: Exception) {
                    lastError = e.message ?: "Connect Error"
                    continue // الانتقال للسيرفر التالي في القائمة
                }
            }

            if (!success) {
                withContext(Dispatchers.Main) {
                    isProcessing = false
                    lastProcessedUrl = ""
                    tvStatus.setTextColor(Color.RED)
                    tvStatus.text = "Busy Servers"
                    showError("All servers are busy or require auth.\\nLast Error: $lastError")
                }
            }
        }
    }

    private fun startSystemDownload(url: String) {
        try {
            tvStatus.text = "Downloading..."
            val request = DownloadManager.Request(Uri.parse(url))
            request.setTitle("MyTube Download")
            request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, "MyTube/video_${System.currentTimeMillis()}.mp4")
            
            val dm = getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
            dm.enqueue(request)

            tvStatus.setTextColor(Color.GREEN)
            tvStatus.text = "✅ Started"
            Toast.makeText(this, "Started! Check Notifications.", Toast.LENGTH_LONG).show()
            
            Handler(Looper.getMainLooper()).postDelayed({ 
                tvStatus.text = "Ready"
                etUrl.text?.clear()
                isProcessing = false
                lastProcessedUrl = ""
            }, 3000)

        } catch (e: Exception) {
            isProcessing = false
            showError("System Error: ${e.message}")
        }
    }

    private fun startAnimations() {
        // أنيميشن ذهبي ورمادي
        val colorAnim = ObjectAnimator.ofInt(tvCredits, "textColor",
            Color.parseColor("#FFD700"), 
            Color.parseColor("#616161"), 
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
    # 1. تحديث الأيقونات
    create_file("app/src/main/res/drawable/ic_launcher_background.xml", icon_background)
    create_file("app/src/main/res/drawable/ic_launcher_foreground.xml", icon_foreground)
    
    # 2. تحديث Gradle
    create_file("app/build.gradle.kts", build_gradle_content)
    
    # 3. تحديث الكود
    create_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", main_activity_code)
    
    print("\n🚀 Pushing 2026 Fixes: Hollow Star + Multi-Server Failover...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Final 2026 Fix: Hollow Syriac Star + Server Rotation"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! Download should work now.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
