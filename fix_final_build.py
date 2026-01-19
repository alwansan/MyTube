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
# 1. تصميم الأيقونة (النجمة السيريانية الغامضة)
# ==========================================
icon_background = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#212121"
        android:pathData="M0,0h108v108h-108z" />
    <path
        android:fillColor="#000000"
        android:fillAlpha="0.4"
        android:pathData="M54,54 m-40,0 a40,40 0 1,0 80,0 a40,40 0 1,0 -80,0" />
</vector>
"""

icon_foreground = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <!-- النجمة الثمانية السيريانية -->
    <path
        android:fillColor="#FFC107"
        android:pathData="M54,10 L63,38 L92,38 L68,54 L77,82 L54,66 L31,82 L40,54 L16,38 L45,38 Z" />
    <!-- العين الغامضة في الوسط -->
    <path
        android:fillColor="#212121"
        android:pathData="M54,44 C60,44 64,48 64,53 C64,58 60,62 54,62 C48,62 44,58 44,53 C44,48 48,44 54,44 Z" />
    <!-- بؤرة العين -->
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M54,50 A3,3 0 1,1 54,56 A3,3 0 0,1 54,50" />
</vector>
"""

# ==========================================
# 2. ملف Gradle (إصلاح الاعتمادات المفقودة)
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
        versionCode = 11
        versionName = "11.0"
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
    
    // 🟢 المكتبة الضرورية التي كانت مفقودة وتسبب فشل البناء
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
}
"""

# ==========================================
# 3. MainActivity (تحديث لبروتوكول v10)
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
    
    private val client = OkHttpClient.Builder()
        .connectTimeout(60, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
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

        // مراقب النص الذكي (يعمل فوراً)
        etUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val url = s.toString().trim()
                if (url.length > 10 && (url.contains("http") || url.contains("youtu")) && url != lastProcessedUrl) {
                    processWithApi(url)
                }
            }
        })

        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { etUrl.setText(it) }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) processWithApi(url)
            else checkClipboard()
        }
        
        tvStatus.text = "Ready"
    }

    private fun processWithApi(url: String) {
        if (isProcessing) return
        isProcessing = true
        lastProcessedUrl = url
        tvStatus.setTextColor(Color.LTGRAY)
        tvStatus.text = "Processing..."

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // 🟢 استخدام البروتوكول الجديد v10
                // Endpoint: / (بدلاً من /api/json)
                val apiUrl = "https://api.cobalt.tools"
                
                val jsonBody = JSONObject()
                jsonBody.put("url", url)
                // v10 Parameters
                jsonBody.put("videoQuality", "max") 
                jsonBody.put("filenameStyle", "basic")
                jsonBody.put("downloadMode", "auto")

                val request = Request.Builder()
                    .url(apiUrl)
                    .post(jsonBody.toString().toRequestBody("application/json".toMediaType()))
                    .header("Accept", "application/json")
                    .header("Content-Type", "application/json")
                    // Header ضروري لتجنب الحظر
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
                    } else if (status == "picker") {
                        val picker = json.optJSONArray("picker")
                        if (picker != null && picker.length() > 0) {
                            val firstUrl = picker.getJSONObject(0).optString("url")
                            withContext(Dispatchers.Main) { startSystemDownload(firstUrl) }
                        }
                    } else {
                        // محاولة قراءة الخطأ الجديد
                        val errText = json.optString("text")
                        throw Exception(if (errText.isNotEmpty()) errText else "API Status: $status")
                    }
                } else {
                    val errorMsg = try {
                        val errJson = JSONObject(responseStr ?: "{}")
                        val text = errJson.optString("text")
                        val code = errJson.optJSONObject("error")?.optString("code")
                        text.ifEmpty { code ?: "HTTP ${response.code}" }
                    } catch (e: Exception) {
                        "HTTP ${response.code}"
                    }
                    throw Exception(errorMsg)
                }

            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    isProcessing = false
                    lastProcessedUrl = ""
                    tvStatus.setTextColor(Color.RED)
                    tvStatus.text = "Error"
                    showError("API Error: ${e.message}")
                }
            }
        }
    }

    private fun startSystemDownload(url: String) {
        try {
            tvStatus.text = "Downloading..."
            val request = DownloadManager.Request(Uri.parse(url))
            request.setTitle("MyTube Download")
            request.setDescription("Saving media...")
            request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, "MyTube/video_${System.currentTimeMillis()}.mp4")
            
            val dm = getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
            dm.enqueue(request)

            tvStatus.setTextColor(Color.GREEN)
            tvStatus.text = "✅ Started"
            Toast.makeText(this, "Check Notifications", Toast.LENGTH_LONG).show()
            
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
        // أنيميشن ذهبي/رمادي سيرياني
        val colorAnim = ObjectAnimator.ofInt(tvCredits, "textColor",
            Color.parseColor("#FFD700"), 
            Color.parseColor("#424242"), 
            Color.parseColor("#FFD700"))
        colorAnim.setDuration(5000)
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
    # 1. تحديث أيقونات النجمة السيريانية
    create_file("app/src/main/res/drawable/ic_launcher_background.xml", icon_background)
    create_file("app/src/main/res/drawable/ic_launcher_foreground.xml", icon_foreground)
    
    # 2. إضافة مكتبة OkHttp إلى Gradle
    create_file("app/build.gradle.kts", build_gradle_content)
    
    # 3. تحديث الكود للبروتوكول الجديد
    create_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", main_activity_code)
    
    print("\n🚀 Pushing Final Build Fix & New Icon...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Final: Add OkHttp, New Icon, Fix API Protocol"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! Build should succeed now.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
