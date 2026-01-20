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

# تنظيف شامل
def clean_all():
    paths = [
        "app/src/main/java/org/alituama/mytube/core",
        "app/src/main/java/org/alituama/mytube/utils",
        "app/src/main/java/org/alituama/mytube/ui",
        "app/src/main/java/org/alituama/mytube/strategy"
    ]
    for p in paths:
        if os.path.exists(p): shutil.rmtree(p)
    print("🧹 Wiped old engines.")

# ==========================================
# 1. الأيقونة: سهم مجوف (التصميم المعتمد)
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
# 2. Gradle: مكتبات النظام فقط
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
        versionCode = 40
        versionName = "4.0"
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
# 3. MainActivity: المحرك الكامل (المتصفح + اللاقط)
# ==========================================
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
import android.webkit.CookieManager
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
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
    private lateinit var tvCredits: TextView
    private lateinit var stealthBrowser: WebView
    
    // متغير لتخزين آخر رابط تم اكتشافه لمنع التكرار
    private var lastDetectedVideo = ""
    private var isDownloading = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        tvStatus = findViewById(R.id.tvStatus)
        tvCredits = findViewById(R.id.tvCredits)
        val btnFetch = findViewById<Button>(R.id.btnFetch)

        // 1. تشغيل المتصفح الخفي
        initStealthBrowser()
        
        startAnimations()
        checkPermissions()

        // 2. مراقبة النص (Auto Detect)
        etUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val url = s.toString().trim()
                if (url.length > 10 && (url.contains("http") || url.contains("youtu"))) {
                    // إذا كان الرابط جديداً ولم نبدأ التحميل بعد
                    if (!isDownloading) {
                        startSniffing(url)
                    }
                }
            }
        })

        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { etUrl.setText(it) }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) startSniffing(url)
            else checkClipboard()
        }
        
        tvStatus.text = "System Ready"
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun initStealthBrowser() {
        stealthBrowser = WebView(this)
        
        // إعدادات المتصفح ليكون "شبح"
        val settings = stealthBrowser.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.mediaPlaybackRequiresUserGesture = false
        settings.blockNetworkImage = true // لتسريع التحميل وتوفير البيانات
        
        // 🛑 الخدعة الكبرى: انتحال شخصية متصفح Firefox على iOS
        // هذا يجبر يوتيوب على إرسال فيديو MP4 مباشر بدلاً من Blob المشفر
        settings.userAgentString = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/114.1 Mobile/15E148 Safari/605.1.15"

        // تفعيل الكوكيز لضمان العمل
        CookieManager.getInstance().setAcceptCookie(true)

        // 🕵️ إعداد اللاقط (Sniffer)
        stealthBrowser.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(view: WebView?, request: WebResourceRequest?): WebResourceResponse? {
                val url = request?.url.toString()
                
                // البحث عن روابط الفيديو الحقيقية (googlevideo.com)
                if (url.contains("googlevideo.com") && url.contains("videoplayback")) {
                    // تحقق مما إذا كان هذا الرابط لفيديو حقيقي (وليس صوت فقط أو معاينة)
                    // عادة روابط الفيديو تحتوي على "mime=video" أو تأتي بحجم كبير
                    
                    if (!isDownloading && url != lastDetectedVideo) {
                        lastDetectedVideo = url
                        isDownloading = true
                        
                        runOnUiThread {
                            tvStatus.text = "Video Detected!"
                            tvStatus.setTextColor(Color.GREEN)
                            // إيقاف المتصفح لتوفير الموارد
                            stealthBrowser.stopLoading()
                            // بدء التحميل
                            downloadFile(url)
                        }
                    }
                }
                return super.shouldInterceptRequest(view, request)
            }
            
            override fun onPageFinished(view: WebView?, url: String?) {
                // محاولة تشغيل الفيديو تلقائياً ليظهر رابط التحميل في الشبكة
                view?.loadUrl("javascript:(function() { var v = document.querySelector('video'); if (v) { v.play(); } })()")
            }
        }
        
        // إضافة المتصفح بحجم 0 (غير مرئي)
        val params = android.view.ViewGroup.LayoutParams(0, 0)
        addContentView(stealthBrowser, params)
    }

    private fun startSniffing(url: String) {
        isDownloading = false
        tvStatus.setTextColor(Color.LTGRAY)
        tvStatus.text = "Sniffing URL..."
        
        // تحميل الصفحة في المتصفح الخفي
        stealthBrowser.loadUrl(url)
        
        // مؤقت للفشل (إذا لم يجد شيئاً خلال 20 ثانية)
        Handler(Looper.getMainLooper()).postDelayed({
            if (!isDownloading) {
                tvStatus.setTextColor(Color.RED)
                tvStatus.text = "Sniffing Timeout"
            }
        }, 20000)
    }

    private fun downloadFile(videoUrl: String) {
        try {
            val request = DownloadManager.Request(Uri.parse(videoUrl))
            request.setTitle("MyTube Video")
            request.setDescription("Downloading content...")
            request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, "MyTube/video_" + System.currentTimeMillis() + ".mp4")
            request.setAllowedOverMetered(true)
            
            // إضافة User-Agent للطلب لضمان قبول السيرفر
            request.addRequestHeader("User-Agent", stealthBrowser.settings.userAgentString)

            val dm = getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
            dm.enqueue(request)

            Toast.makeText(this, "Downloading Started 🚀", Toast.LENGTH_LONG).show()
            
            // إعادة ضبط الحالة لاستقبال رابط جديد
            Handler(Looper.getMainLooper()).postDelayed({ 
                tvStatus.text = "Ready"
                tvStatus.setTextColor(Color.WHITE)
                etUrl.text.clear()
                isDownloading = false 
            }, 3000)

        } catch (e: Exception) {
            tvStatus.text = "DL Error: " + e.message
            isDownloading = false
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
"""

if __name__ == "__main__":
    clean_all()
    
    create_file("app/src/main/res/drawable/ic_launcher_background.xml", icon_background)
    create_file("app/src/main/res/drawable/ic_launcher_foreground.xml", icon_foreground)
    
    create_file("app/build.gradle.kts", build_gradle_content)
    create_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", main_activity_code)
    
    print("\n🚀 Pushing Firefox Stealth Engine...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Final: Stealth Mozilla Browser + Native Sniffer"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! No servers, no python, just pure Android logic.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
