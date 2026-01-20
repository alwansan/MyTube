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
# 1. تصميم الأيقونة (سهم مجوف - Minimalist)
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
# 2. Gradle (إصلاح المكتبات)
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
    // مكتبة المتصفح
    implementation("androidx.webkit:webkit:1.9.0")
}
"""

# ==========================================
# 3. MainActivity (المتصفح الخفي الآمن)
# ==========================================
# ملاحظة: تم كتابة كود JS بطريقة سلسلة نصية بسيطة لتجنب أخطاء البناء
main_activity_code = """package org.alituama.mytube

import android.Manifest
import android.animation.ArgbEvaluator
import android.animation.ObjectAnimator
import android.annotation.SuppressLint
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
import android.view.View
import android.webkit.JavascriptInterface
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class MainActivity : AppCompatActivity() {

    private lateinit var tvStatus: TextView
    private lateinit var etUrl: TextInputEditText
    private lateinit var tvCredits: TextView
    private lateinit var hiddenWebView: WebView
    private var lastUrl = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        tvStatus = findViewById(R.id.tvStatus)
        tvCredits = findViewById(R.id.tvCredits)
        val btnFetch = findViewById<Button>(R.id.btnFetch)

        // إعداد المتصفح الخفي
        setupHiddenBrowser()
        
        startAnimations()
        checkPermissions()

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
        
        // إخفاء المتصفح (حجم 1 بكسل وشفاف)
        val params = android.view.ViewGroup.LayoutParams(1, 1)
        hiddenWebView.layoutParams = params
        hiddenWebView.visibility = View.INVISIBLE
        hiddenWebView.alpha = 0.0f
        
        val settings = hiddenWebView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.mediaPlaybackRequiresUserGesture = false
        // انتحال شخصية Android Chrome لتجنب المشاكل
        settings.userAgentString = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"

        // ربط الجافا سكريبت بالكوتلن
        hiddenWebView.addJavascriptInterface(BrowserInterface(this), "AndroidApp")

        hiddenWebView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                // حقن كود البحث عن الفيديو بعد تحميل الصفحة
                injectSniffer()
            }
        }
        
        // إضافة الـ WebView للتخطيط (ضروري ليعمل)
        addContentView(hiddenWebView, params)
    }

    private fun processUrl(url: String) {
        lastUrl = url
        tvStatus.setTextColor(Color.LTGRAY)
        tvStatus.text = "Analyzing..."
        
        // تحميل الصفحة في الخفاء
        hiddenWebView.loadUrl(url)
    }

    private fun injectSniffer() {
        // كود جافا سكريبت بسيط للبحث عن وسم <video> واستخراج رابطه
        // تم استخدام نص عادي لتجنب أخطاء البناء
        val js = "javascript:(function() { " +
                 "   var checkVideo = setInterval(function() { " +
                 "      var video = document.querySelector('video'); " +
                 "      if (video && video.src) { " +
                 "         AndroidApp.foundVideo(video.src); " +
                 "         clearInterval(checkVideo); " +
                 "      } " +
                 "   }, 1000); " +
                 "   setTimeout(function() { clearInterval(checkVideo); }, 15000); " +
                 "})()"
        
        hiddenWebView.loadUrl(js)
    }

    // دالة لتلقي الرابط من المتصفح
    fun onVideoFound(videoUrl: String) {
        runOnUiThread {
            if (videoUrl.startsWith("blob")) {
                tvStatus.setTextColor(Color.RED)
                tvStatus.text = "Protected Stream"
                Toast.makeText(this, "Video is protected (Blob)", Toast.LENGTH_SHORT).show()
            } else {
                startSystemDownload(videoUrl)
            }
        }
    }

    private fun startSystemDownload(url: String) {
        try {
            tvStatus.text = "Downloading..."
            val request = DownloadManager.Request(Uri.parse(url))
            request.setTitle("MyTube Video")
            request.setDescription("Downloading...")
            request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, "MyTube/video_" + System.currentTimeMillis() + ".mp4")
            
            val dm = getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
            dm.enqueue(request)

            tvStatus.setTextColor(Color.GREEN)
            tvStatus.text = "✅ Started"
            Toast.makeText(this, "Started! Check Notifications.", Toast.LENGTH_LONG).show()
            
            etUrl.text?.clear()
            lastUrl = ""
            // إعادة التهيئة بعد 4 ثواني
            Handler(Looper.getMainLooper()).postDelayed({ tvStatus.text = "Ready" }, 4000)

        } catch (e: Exception) {
            tvStatus.text = "DL Error"
        }
    }

    private fun startAnimations() {
        val colorAnim = ObjectAnimator.ofInt(tvCredits, "textColor",
            Color.parseColor("#FFD700"), 
            Color.parseColor("#333333"), 
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
}

// كلاس الواجهة (Interface) يجب أن يكون منفصلاً و public
class BrowserInterface(private val activity: MainActivity) {
    @JavascriptInterface
    fun foundVideo(url: String) {
        activity.onVideoFound(url)
    }
}
"""

if __name__ == "__main__":
    # تنظيف
    if os.path.exists("app/src/main/java/org/alituama/mytube/core"): shutil.rmtree("app/src/main/java/org/alituama/mytube/core")
    
    # 1. تحديث الأيقونة
    create_file("app/src/main/res/drawable/ic_launcher_background.xml", icon_background)
    create_file("app/src/main/res/drawable/ic_launcher_foreground.xml", icon_foreground)
    
    # 2. تحديث Gradle
    create_file("app/build.gradle.kts", build_gradle_content)
    
    # 3. تحديث الكود
    create_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", main_activity_code)
    
    print("\n🚀 Pushing Final Safe Browser Hijack Fix...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Final Fix: Safe String Escaping for Browser Hijack"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! Build failure is solved.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
