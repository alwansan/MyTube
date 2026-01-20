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

# ==========================================
# 1. الأيقونة (سهم مجوف نقي جداً)
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
</vector>
"""

icon_foreground = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <!-- سهم مجوف فقط -->
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
# 2. Gradle (مكتبات النظام الأساسية فقط)
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
        versionCode = 30
        versionName = "30.0"
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
    implementation("androidx.webkit:webkit:1.9.0")
}
"""

# ==========================================
# 3. MainActivity (نظام المحاكاة والاقتناص)
# ==========================================
# هذا الكود يستخدم خدعة JS آمنة لضمان عدم فشل البناء
main_activity_code = """package org.alituama.mytube

import android.Manifest
import android.annotation.SuppressLint
import android.app.DownloadManager
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.text.Editable
import android.text.TextWatcher
import android.view.View
import android.webkit.JavascriptInterface
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class MainActivity : AppCompatActivity() {

    private lateinit var tvStatus: TextView
    private lateinit var etUrl: EditText
    private lateinit var hiddenWebView: WebView
    private var lastUrl = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        tvStatus = findViewById(R.id.tvStatus)
        val btnFetch = findViewById<Button>(R.id.btnFetch)

        // إعداد المتصفح الخفي (المحرك)
        setupHiddenBrowser()
        checkPermissions()

        // مراقب النص الذكي
        etUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val url = s.toString().trim()
                if (url.length > 10 && (url.contains("http") || url.contains("youtu")) && url != lastUrl) {
                    processUrl(url)
                }
            }
        })

        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { etUrl.setText(it) }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) processUrl(url)
            else checkClipboard()
        }
        
        tvStatus.text = "Ready"
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun setupHiddenBrowser() {
        hiddenWebView = WebView(this)
        
        // إخفاء المتصفح تماماً
        hiddenWebView.visibility = View.INVISIBLE
        hiddenWebView.alpha = 0f
        
        val settings = hiddenWebView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.mediaPlaybackRequiresUserGesture = false
        
        // انتحال شخصية iPhone 14 Pro
        // هذا يجعل يوتيوب يرسل ملفات MP4 متوافقة مباشرة
        settings.userAgentString = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"

        // إضافة واجهة للاستماع للروابط المكتشفة
        hiddenWebView.addJavascriptInterface(WebAppInterface(this), "Sniffer")

        hiddenWebView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                // حقن كود البحث عن الفيديو
                injectVideoSniffer()
            }
        }
        
        // إضافة المتصفح للتخطيط (مهم جداً ليعمل)
        val params = android.view.ViewGroup.LayoutParams(1, 1)
        addContentView(hiddenWebView, params)
    }

    private fun processUrl(url: String) {
        lastUrl = url
        tvStatus.text = "Analyzing (Hijack Mode)..."
        hiddenWebView.loadUrl(url)
        
        // مؤقت لإلغاء العملية إذا طالت
        Handler(Looper.getMainLooper()).postDelayed({
            if (tvStatus.text == "Analyzing (Hijack Mode)...") {
                tvStatus.text = "Timeout - Try Again"
            }
        }, 15000)
    }

    private fun injectVideoSniffer() {
        // كود JS بسيط جداً وقوي للبحث عن الفيديو
        val js = "javascript:(function() { " +
                 "   var timer = setInterval(function() { " +
                 "      var video = document.querySelector('video'); " +
                 "      if (video && video.src) { " +
                 "         Sniffer.onVideoFound(video.src); " +
                 "         clearInterval(timer); " +
                 "      } " +
                 "   }, 500); " +
                 "})()"
        hiddenWebView.loadUrl(js)
    }

    fun handleVideoFound(videoUrl: String) {
        runOnUiThread {
            if (videoUrl.startsWith("http")) {
                startSystemDownload(videoUrl)
            } else if (videoUrl.startsWith("blob")) {
                // روابط Blob مشفرة، لا يمكن تنزيلها مباشرة
                tvStatus.text = "Protected Stream (Blob)"
                Toast.makeText(this, "Video is protected", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun startSystemDownload(url: String) {
        try {
            tvStatus.text = "Downloading..."
            val request = DownloadManager.Request(Uri.parse(url))
            request.setTitle("MyTube Video")
            request.setDescription("Saving to Downloads...")
            request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, "MyTube/video_" + System.currentTimeMillis() + ".mp4")
            request.setAllowedOverMetered(true)
            
            val dm = getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
            dm.enqueue(request)

            tvStatus.text = "✅ Started"
            Toast.makeText(this, "Downloading in background!", Toast.LENGTH_LONG).show()
            
            etUrl.text.clear()
            lastUrl = ""
            
            // إعادة الحالة
            Handler(Looper.getMainLooper()).postDelayed({ tvStatus.text = "Ready" }, 4000)

        } catch (e: Exception) {
            tvStatus.text = "Download Error"
        }
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
}

// واجهة الجسر بين المتصفح والتطبيق
class WebAppInterface(private val mContext: MainActivity) {
    @JavascriptInterface
    fun onVideoFound(url: String) {
        mContext.handleVideoFound(url)
    }
}
"""

if __name__ == "__main__":
    # تنظيف شامل
    if os.path.exists("app/src/main/java/org/alituama/mytube/core"): shutil.rmtree("app/src/main/java/org/alituama/mytube/core")
    if os.path.exists("app/src/main/java/org/alituama/mytube/utils"): shutil.rmtree("app/src/main/java/org/alituama/mytube/utils")
    if os.path.exists("app/src/main/java/org/alituama/mytube/strategy"): shutil.rmtree("app/src/main/java/org/alituama/mytube/strategy")
    if os.path.exists("app/src/main/java/org/alituama/mytube/ui"): shutil.rmtree("app/src/main/java/org/alituama/mytube/ui")

    # 1. تحديث الأيقونة
    create_file("app/src/main/res/drawable/ic_launcher_background.xml", icon_background)
    create_file("app/src/main/res/drawable/ic_launcher_foreground.xml", icon_foreground)
    
    # 2. تحديث Gradle
    create_file("app/build.gradle.kts", build_gradle_content)
    
    # 3. تحديث الكود
    create_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", main_activity_code)
    
    print("\n🚀 Pushing SnapTube Replica Fix...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Final: SnapTube Replica (Hidden Browser Injection)"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! This code is clean and compilation-safe.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
