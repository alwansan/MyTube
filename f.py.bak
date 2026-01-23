
import os
import shutil
import subprocess

# --- MYTUBE REPAIR SCRIPT v3 (ARM64 + COOKIE BRIDGE) ---

def write_file(path, content):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"✅ Created: {path}")

print("🛠️ Applying Bot Bypass & Cookie Bridge...")

# 1. Update build.gradle.kts (ARM64 Exclusive)
write_file("app/build.gradle.kts", """
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
        versionCode = 308
        versionName = "3.3.0"
        
        ndk {
            abiFilters.add("arm64-v8a")
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    
    packaging {
        jniLibs {
            useLegacyPackaging = true
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    kotlinOptions { jvmTarget = "1.8" }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    
    implementation("io.github.junkfood02.youtubedl-android:library:0.17.2")
    implementation("io.github.junkfood02.youtubedl-android:ffmpeg:0.17.2") 
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
}
""")

# 2. Update gradle.properties
write_file("gradle.properties", """
org.gradle.jvmargs=-Xmx3072m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
""")

# 3. Fix GitHub Workflow
write_file(".github/workflows/android.yml", """
name: Android CI

on:
  push:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'
        cache: gradle

    - name: Grant execute permission for gradlew
      run: chmod +x gradlew

    - name: Build with Gradle
      run: ./gradlew assembleDebug --stacktrace

    - name: Upload APK
      uses: actions/upload-artifact@v4
      with:
        name: MyTube-ARM64
        path: app/build/outputs/apk/debug/app-debug.apk
        if-no-files-found: error
""")

# 4. Update MainActivity.kt (With Cookie Bridge)
write_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", r"""

package org.alituama.mytube

import android.Manifest
import android.app.AlertDialog
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.text.Editable
import android.text.TextWatcher
import android.view.View
import android.webkit.CookieManager
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.yausername.youtubedl_android.YoutubeDL
import com.yausername.youtubedl_android.YoutubeDLRequest
import com.yausername.youtubedl_android.mapper.VideoInfo
import kotlinx.coroutines.*
import java.io.File

class MainActivity : AppCompatActivity() {

    private lateinit var tvStatus: TextView
    private lateinit var etUrl: EditText
    private lateinit var progressBar: ProgressBar
    private lateinit var webView: WebView // THE HIDDEN BROWSER
    private var lastUrl = ""
    private var isEngineReady = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        tvStatus = findViewById(R.id.tvStatus)
        progressBar = findViewById(R.id.progressBar)
        webView = findViewById(R.id.webView)
        val btnFetch = findViewById<Button>(R.id.btnFetch)

        setupHiddenBrowser()
        checkPermissions()
        initEngine()

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
    }

    private fun setupHiddenBrowser() {
        // This WebView acts as our "Mozilla" to bypass bot checks
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            userAgentString = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
            mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
        }
        
        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                // Page loaded -> Cookies are ready
            }
        }
        
        // Clear old sessions
        CookieManager.getInstance().removeAllCookies(null)
        CookieManager.getInstance().flush()
    }

    private fun initEngine() {
        tvStatus.text = "IGNITING ENGINE..."
        tvStatus.setTextColor(Color.GRAY)
        progressBar.visibility = View.VISIBLE

        CoroutineScope(Dispatchers.IO).launch {
            try {
                YoutubeDL.getInstance().init(applicationContext)
                
                // Attempt update, but don't fail if offline
                try {
                    YoutubeDL.getInstance().updateYoutubeDL(applicationContext, YoutubeDL.UpdateChannel.STABLE)
                } catch (e: Exception) { e.printStackTrace() }

                isEngineReady = true
                withContext(Dispatchers.Main) {
                    tvStatus.text = "READY (ARM64)"
                    tvStatus.setTextColor(Color.GREEN)
                    progressBar.visibility = View.INVISIBLE
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvStatus.text = "ENGINE ERROR"
                    tvStatus.setTextColor(Color.RED)
                    showErrorDialog("Init Failed: ${e.message}")
                }
            }
        }
    }

    private fun processUrl(url: String) {
        if (!isEngineReady) {
            Toast.makeText(this, "Engine booting...", Toast.LENGTH_SHORT).show()
            initEngine()
            return
        }

        lastUrl = url
        tvStatus.text = "BYPASSING BOT CHECK..."
        tvStatus.setTextColor(Color.parseColor("#FFD700")) // Gold
        progressBar.visibility = View.VISIBLE
        
        // STEP 1: LOAD IN HIDDEN BROWSER TO GENERATE COOKIES
        webView.visibility = View.INVISIBLE // Keep it loaded but hidden, or 1px
        webView.loadUrl(url)
        
        // Wait for cookies to populate (simple delay usually works better than complex listeners for this)
        Handler(Looper.getMainLooper()).postDelayed({
            extractCookiesAndAnalyze(url)
        }, 3500) // 3.5s delay to allow JS to execute on the page
    }

    private fun extractCookiesAndAnalyze(url: String) {
        val cookies = CookieManager.getInstance().getCookie(url)
        val userAgent = webView.settings.userAgentString
        
        if (cookies == null) {
            tvStatus.text = "RETRYING BYPASS..."
            Handler(Looper.getMainLooper()).postDelayed({ extractCookiesAndAnalyze(url) }, 2000)
            return
        }

        tvStatus.text = "ANALYZING STREAM..."
        
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val request = YoutubeDLRequest(url)
                
                // CRITICAL: PASS BROWSER CREDENTIALS TO YT-DLP
                request.addHeader("Cookie", cookies)
                request.addHeader("User-Agent", userAgent)
                
                // Options to reduce errors
                request.addOption("--no-playlist")
                request.addOption("--no-check-certificate")
                request.addOption("--geo-bypass")
                // Fallback for no JS runtime in yt-dlp (we did the JS part in WebView)
                request.addOption("--extractor-args", "youtube:player_client=android") 

                val info: VideoInfo = YoutubeDL.getInstance().getInfo(request)
                
                withContext(Dispatchers.Main) {
                    progressBar.visibility = View.INVISIBLE
                    showFormatSelector(info, url, cookies, userAgent)
                }

            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    progressBar.visibility = View.INVISIBLE
                    tvStatus.text = "FAILED"
                    tvStatus.setTextColor(Color.RED)
                    showErrorDialog("Bot Check Failed: ${e.message}")
                }
            }
        }
    }

    private fun showFormatSelector(info: VideoInfo, url: String, cookies: String, userAgent: String) {
        val formats = info.formats ?: emptyList()
        val options = ArrayList<VideoOption>()
        val title = info.title ?: "Video"

        val seenQualities = HashSet<String>()
        for (f in formats) {
            if (f.vcodec != "none" && f.height > 0) {
                val q = "${f.height}p"
                if (!seenQualities.contains(q)) {
                    val desc = if (f.acodec != "none") "Standard" else "Video Only"
                    options.add(VideoOption(q, desc, f.formatId ?: ""))
                    seenQualities.add(q)
                }
            }
        }
        
        options.sortByDescending { it.quality.replace("p", "").toIntOrNull() ?: 0 }
        options.add(VideoOption("Audio Only", "MP3", "bestaudio/best"))

        if (options.isEmpty()) {
            tvStatus.text = "NO FORMATS"
            return
        }

        val builder = AlertDialog.Builder(this, R.style.SyriacDialog)
        builder.setTitle(title)
        val adapter = ArrayAdapter(this, android.R.layout.select_dialog_singlechoice, options.map { "${it.quality} | ${it.desc}" })
        
        builder.setAdapter(adapter) { _, which ->
            val selected = options[which]
            startDownload(title, url, selected.formatId, selected.quality, cookies, userAgent)
        }
        
        builder.setOnCancelListener { 
            tvStatus.text = "READY" 
            tvStatus.setTextColor(Color.GRAY)
        }
        builder.show()
    }

    private fun startDownload(title: String, url: String, formatId: String, qualityLabel: String, cookies: String, userAgent: String) {
        tvStatus.text = "DOWNLOADING..."
        tvStatus.setTextColor(Color.GREEN)
        progressBar.visibility = View.VISIBLE
        
        val downloadDir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        if (!downloadDir.exists()) downloadDir.mkdirs()

        CoroutineScope(Dispatchers.IO).launch {
            try {
                val cleanTitle = title.replace(Regex("[^a-zA-Z0-9.-]"), "_")
                val request = YoutubeDLRequest(url)
                
                // Pass credentials again for the download phase
                request.addHeader("Cookie", cookies)
                request.addHeader("User-Agent", userAgent)
                
                if (qualityLabel == "Audio Only") {
                     request.addOption("-f", "bestaudio/best")
                     request.addOption("-x")
                     request.addOption("--audio-format", "mp3")
                } else {
                     request.addOption("-f", "$formatId+bestaudio/best")
                }
                
                request.addOption("-o", downloadDir.absolutePath + "/%(title)s.%(ext)s")
                request.addOption("--no-mtime")
                
                YoutubeDL.getInstance().execute(request, null) { progress, eta, line -> }

                withContext(Dispatchers.Main) {
                    progressBar.visibility = View.INVISIBLE
                    tvStatus.text = "COMPLETE"
                    Toast.makeText(applicationContext, "Saved to Downloads/MyTube", Toast.LENGTH_LONG).show()
                    etUrl.text.clear()
                }

            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    progressBar.visibility = View.INVISIBLE
                    tvStatus.text = "ERROR"
                    tvStatus.setTextColor(Color.RED)
                    showErrorDialog(e.message ?: "Download failed")
                }
            }
        }
    }

    private fun showErrorDialog(msg: String) {
        AlertDialog.Builder(this, R.style.SyriacDialog)
            .setTitle("Error")
            .setMessage(msg)
            .setPositiveButton("OK", null)
            .show()
    }

    private fun checkClipboard() {
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clip = clipboard.primaryClip
        if (clip != null && clip.itemCount > 0) {
            etUrl.setText(clip.getItemAt(0).text.toString())
        }
    }

    private fun checkPermissions() {
        if (Build.VERSION.SDK_INT >= 33 && ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != 0) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), 100)
        }
        if (Build.VERSION.SDK_INT <= 29 && ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != 0) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.WRITE_EXTERNAL_STORAGE), 101)
        }
    }

    data class VideoOption(val quality: String, val desc: String, val formatId: String)
}
  
""")

# 5. Update Layout (Added WebView)
write_file("app/src/main/res/layout/activity_main.xml", """

<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#121212"
    android:padding="24dp">

    <!-- HIDDEN BROWSER (1x1 pixel) -->
    <WebView
        android:id="@+id/webView"
        android:layout_width="1dp"
        android:layout_height="1dp"
        android:visibility="invisible"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

    <TextView
        android:id="@+id/tvTitle"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:fontFamily="serif"
        android:text="MYTUBE"
        android:textColor="#FFD700"
        android:textSize="32sp"
        android:letterSpacing="0.2"
        app:layout_constraintBottom_toTopOf="@+id/etUrl"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintVertical_bias="0.3" />

    <EditText
        android:id="@+id/etUrl"
        android:layout_width="0dp"
        android:layout_height="60dp"
        android:background="#1A1A1A"
        android:hint="PASTE LINK HERE"
        android:textColorHint="#505050"
        android:textColor="#FFD700"
        android:gravity="center"
        android:textSize="14sp"
        android:inputType="textUri"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

    <Button
        android:id="@+id/btnFetch"
        android:layout_width="0dp"
        android:layout_height="50dp"
        android:layout_marginTop="20dp"
        android:backgroundTint="#1A1A1A"
        android:text="ENGAGE"
        android:textColor="#FFD700"
        android:letterSpacing="0.1"
        android:stateListAnimator="@null"
        app:strokeColor="#33FFD700"
        app:strokeWidth="1dp"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toBottomOf="@+id/etUrl" />

    <TextView
        android:id="@+id/tvStatus"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="32dp"
        android:text="SYSTEM IDLE"
        android:textColor="#505050"
        android:textSize="10sp"
        android:letterSpacing="0.3"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toBottomOf="@+id/btnFetch" />

    <ProgressBar
        android:id="@+id/progressBar"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        android:visibility="invisible"
        android:indeterminateTint="#FFD700"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toBottomOf="@+id/tvStatus" />

</androidx.constraintlayout.widget.ConstraintLayout>
  
""")

# 6. Ensure Manifest
write_file("app/src/main/AndroidManifest.xml", """
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="MyTube"
        android:supportsRtl="true"
        android:theme="@style/Theme.MyTube"
        android:usesCleartextTraffic="true"
        android:extractNativeLibs="true"
        tools:targetApi="31">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.MyTube"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
            <intent-filter>
                <action android:name="android.intent.action.SEND" />
                <category android:name="android.intent.category.DEFAULT" />
                <data android:mimeType="text/plain" />
            </intent-filter>
        </activity>
    </application>
</manifest>
""")

print("🚀 Codebase Updated: Cookie Bridge + ARM64!")

# --- AUTO PUSH TO GITHUB ---
try:
    print("🔄 Pushing to GitHub...")
    subprocess.run(["git", "remote", "add", "origin", "https://github.com/alwansan/MyTube.git"], check=False, capture_output=True)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Fix: Bot Bypass + No JS Runtime"], check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
    print("✅ Uploaded successfully.")
except Exception as e:
    print(f"❌ Git error: {e}")
