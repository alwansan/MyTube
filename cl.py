
import os
import shutil

# --- MYTUBE CLEAN INSTALL SCRIPT ---
# This script wipes old conflicting files and installs the Hybrid Quality Selector Engine.

def clean_project():
    print("🧹 Cleaning old engine files...")
    paths_to_remove = [
        "app/src/main/java/org/alituama/mytube/core",
        "app/src/main/java/org/alituama/mytube/utils",
        "app/src/main/java/org/alituama/mytube/strategy",
        "app/src/main/java/org/alituama/mytube/ui",
        "browser_hijack_fix.py",
        "browser_hijack_mode.py",
        "embedded_server_fix.py",
        "firefox_stealth_engine.py",
        "snaptube_replica.py"
    ]
    for path in paths_to_remove:
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.exists(path):
            os.remove(path)

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"✅ Created: {path}")

# 1. build.gradle.kts (Dependencies)
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
        versionCode = 100
        versionName = "1.0.0"
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
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
}
""")

# 2. AndroidManifest.xml
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

# 3. Themes & Colors (Syriac Art)
write_file("app/src/main/res/values/themes.xml", """
<resources xmlns:tools="http://schemas.android.com/tools">
    <style name="Theme.MyTube" parent="Theme.MaterialComponents.DayNight.NoActionBar">
        <item name="colorPrimary">#FFD700</item>
        <item name="colorPrimaryVariant">#C5A028</item>
        <item name="colorOnPrimary">#000000</item>
        <item name="android:windowBackground">#121212</item>
        <item name="android:statusBarColor">#0F0F0F</item>
    </style>
    
    <style name="SyriacDialog" parent="Theme.MaterialComponents.DayNight.Dialog.Alert">
        <item name="android:background">#1A1A1A</item>
        <item name="android:textColor">#FFD700</item>
        <item name="colorAccent">#FFD700</item>
    </style>
</resources>
""")

write_file("app/src/main/res/values/colors.xml", """
<resources>
    <color name="black">#FF000000</color>
    <color name="gold">#FFD700</color>
    <color name="dark_matter">#121212</color>
</resources>
""")

# 4. Layout
write_file("app/src/main/res/layout/activity_main.xml", """
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout 
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#121212"
    android:padding="24dp">

    <!-- Icon Area -->
    <View
        android:id="@+id/iconBg"
        android:layout_width="80dp"
        android:layout_height="80dp"
        android:background="@drawable/ic_launcher_background"
        android:backgroundTint="#1A1A1A"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        android:layout_marginTop="40dp" />

    <TextView
        android:id="@+id/tvTitle"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="MYTUBE"
        android:textColor="#FFD700"
        android:textSize="24sp"
        android:letterSpacing="0.2"
        android:textStyle="bold"
        app:layout_constraintTop_toBottomOf="@id/iconBg"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        android:layout_marginTop="16dp" />

    <!-- Status -->
    <TextView
        android:id="@+id/tvStatus"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="AWAITING LINK"
        android:textColor="#666666"
        android:textSize="12sp"
        android:letterSpacing="0.1"
        app:layout_constraintTop_toBottomOf="@id/tvTitle"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        android:layout_marginTop="8dp" />

    <!-- Input Area -->
    <com.google.android.material.textfield.TextInputLayout
        android:id="@+id/inputLayout"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="PASTE YOUTUBE LINK"
        app:boxStrokeColor="#FFD700"
        app:hintTextColor="#C5A028"
        android:textColorHint="#444444"
        style="@style/Widget.MaterialComponents.TextInputLayout.OutlinedBox"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintTop_toTopOf="parent">

        <com.google.android.material.textfield.TextInputEditText
            android:id="@+id/etUrl"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:textColor="#FFFFFF"
            android:inputType="textUri" />
    </com.google.android.material.textfield.TextInputLayout>

    <Button
        android:id="@+id/btnFetch"
        android:layout_width="match_parent"
        android:layout_height="60dp"
        android:text="ANALYZE"
        android:textSize="14sp"
        android:letterSpacing="0.1"
        android:textStyle="bold"
        android:backgroundTint="#1A1A1A"
        android:textColor="#FFD700"
        app:strokeColor="#FFD700"
        app:strokeWidth="1dp"
        app:layout_constraintTop_toBottomOf="@id/inputLayout"
        android:layout_marginTop="16dp" />

    <ProgressBar
        android:id="@+id/progressBar"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:visibility="invisible"
        android:indeterminateTint="#FFD700"
        app:layout_constraintTop_toBottomOf="@id/btnFetch"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        android:layout_marginTop="24dp" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="SYRIAC ENGINE v3.0"
        android:textColor="#333333"
        android:textSize="10sp"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
""")

# 5. MainActivity.kt
write_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", """

package org.alituama.mytube

import android.Manifest
import android.annotation.SuppressLint
import android.app.AlertDialog
import android.app.DownloadManager
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.text.Editable
import android.text.TextWatcher
import android.view.View
import android.webkit.JavascriptInterface
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
import org.json.JSONObject

class MainActivity : AppCompatActivity() {

    private lateinit var tvStatus: TextView
    private lateinit var etUrl: EditText
    private lateinit var progressBar: ProgressBar
    private lateinit var hiddenWebView: WebView
    private var lastUrl = ""
    private var isAnalyzing = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        tvStatus = findViewById(R.id.tvStatus)
        progressBar = findViewById(R.id.progressBar)
        val btnFetch = findViewById<Button>(R.id.btnFetch)

        setupHiddenEngine()
        checkPermissions()

        // Auto-Action Listener
        etUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val url = s.toString().trim()
                if (url.length > 10 && (url.contains("http") || url.contains("youtu")) && url != lastUrl) {
                    startAnalysis(url)
                }
            }
        })

        // Handle "Share to" from YouTube app
        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { 
                etUrl.setText(it) // Triggers TextWatcher
            }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) startAnalysis(url)
            else checkClipboard()
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun setupHiddenEngine() {
        hiddenWebView = WebView(this)
        val settings = hiddenWebView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.mediaPlaybackRequiresUserGesture = false
        // Desktop UA forces YouTube to load the full player with all resolutions (up to 4K)
        settings.userAgentString = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        hiddenWebView.addJavascriptInterface(VideoInterface(), "AndroidBridge")

        hiddenWebView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                if (isAnalyzing) {
                    // Inject JS to extract the player response JSON
                    injectExtractor()
                }
            }
        }
        
        // Add to view hierarchy but keep invisible (required for JS execution)
        val params = android.view.ViewGroup.LayoutParams(1, 1)
        hiddenWebView.visibility = View.INVISIBLE
        addContentView(hiddenWebView, params)
    }

    private fun startAnalysis(url: String) {
        lastUrl = url
        isAnalyzing = true
        tvStatus.text = "ANALYZING METADATA..."
        tvStatus.setTextColor(Color.parseColor("#FFD700")) // Gold
        progressBar.visibility = View.VISIBLE
        
        hiddenWebView.loadUrl(url)
    }

    private fun injectExtractor() {
        val js = "javascript:(function() { " +
                 "   try {" +
                 "     var json = null;" +
                 "     if (window.ytInitialPlayerResponse) {" +
                 "       json = JSON.stringify(window.ytInitialPlayerResponse);" +
                 "     }" +
                 "     if (json) { AndroidBridge.onMetadataFound(json); }" +
                 "   } catch(e) { }" +
                 "})()"
        hiddenWebView.loadUrl(js)
    }

    inner class VideoInterface {
        @JavascriptInterface
        fun onMetadataFound(jsonString: String) {
            runOnUiThread {
                try {
                    processMetadata(jsonString)
                } catch (e: Exception) {
                    tvStatus.text = "PARSING ERROR"
                    tvStatus.setTextColor(Color.RED)
                }
            }
        }
    }

    private fun processMetadata(jsonString: String) {
        val formats = ArrayList<VideoOption>()
        val json = JSONObject(jsonString)
        
        if (!json.has("streamingData")) return 

        val streamingData = json.getJSONObject("streamingData")
        val videoDetails = json.getJSONObject("videoDetails")
        val title = videoDetails.getString("title")

        // 1. Standard Formats (Muxed Audio+Video) - Usually up to 720p
        if (streamingData.has("formats")) {
            val rawFormats = streamingData.getJSONArray("formats")
            for (i in 0 until rawFormats.length()) {
                val f = rawFormats.getJSONObject(i)
                val label = f.optString("qualityLabel", "Unknown")
                val type = f.optString("mimeType", "")
                val url = f.getString("url")
                
                if (type.contains("mp4")) {
                    formats.add(VideoOption(label, "MP4 (Audio+Video)", url))
                }
            }
        }

        // 2. Adaptive Formats (Split Streams) - 1080p, 4K, etc.
        if (streamingData.has("adaptiveFormats")) {
            val adaptive = streamingData.getJSONArray("adaptiveFormats")
            for (i in 0 until adaptive.length()) {
                val f = adaptive.getJSONObject(i)
                val label = f.optString("qualityLabel", "")
                val type = f.optString("mimeType", "")
                val url = f.getString("url")

                // We filter for high quality MP4 video streams
                if (type.contains("video/mp4") && label.isNotEmpty()) {
                    // Check if we already have this quality from "formats"
                    val exists = formats.any { it.quality == label && it.desc.contains("Audio+Video") }
                    if (!exists) {
                         formats.add(VideoOption(label, "MP4 (Video Only)", url))
                    }
                }
                
                // Optional: Capture Audio Only track
                if (type.contains("audio/mp4") && !formats.any { it.quality == "Audio" }) {
                     formats.add(VideoOption("Audio", "M4A (Audio Only)", url))
                }
            }
        }

        // Sort by quality (rough string comparison or logic)
        formats.sortByDescending { it.quality.replace("p", "").toIntOrNull() ?: 0 }

        if (formats.isNotEmpty()) {
            showQualitySelector(title, formats)
        } else {
            tvStatus.text = "NO STREAMS FOUND"
            tvStatus.setTextColor(Color.RED)
        }
        
        isAnalyzing = false
        progressBar.visibility = View.INVISIBLE
    }

    private fun showQualitySelector(title: String, options: List<VideoOption>) {
        tvStatus.text = "SELECT QUALITY"
        
        val builder = AlertDialog.Builder(this, R.style.SyriacDialog)
        builder.setTitle("Target: \${title.take(20)}...")

        val adapter = ArrayAdapter(this, android.R.layout.select_dialog_singlechoice, options.map { 
            "${it.quality}  |  ${it.desc}" 
        })
        
        builder.setAdapter(adapter) { _, which ->
            val selected = options[which]
            startDownload(title, selected)
        }
        
        builder.setOnCancelListener {
             tvStatus.text = "READY"
             tvStatus.setTextColor(Color.GRAY)
        }

        val dialog = builder.create()
        dialog.show()
    }

    private fun startDownload(title: String, option: VideoOption) {
        try {
            val cleanTitle = title.replace(Regex("[^a-zA-Z0-9.-]"), "_")
            val fileName = "MyTube_${cleanTitle}_${option.quality}_${System.currentTimeMillis()}.mp4"

            val request = DownloadManager.Request(Uri.parse(option.url))
            request.setTitle("MyTube: ${option.quality}")
            request.setDescription(title)
            request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, fileName)
            request.setAllowedOverMetered(true)

            val dm = getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
            dm.enqueue(request)

            Toast.makeText(this, "Downloading ${option.quality}...", Toast.LENGTH_LONG).show()
            tvStatus.text = "DOWNLOADING..."
            tvStatus.setTextColor(Color.GREEN)
            
            etUrl.text.clear()

        } catch (e: Exception) {
            Toast.makeText(this, "Download Failed", Toast.LENGTH_SHORT).show()
        }
    }

    private fun checkClipboard() {
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clip = clipboard.primaryClip
        if (clip != null && clip.itemCount > 0) {
            etUrl.setText(clip.getItemAt(0).text.toString())
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

    data class VideoOption(val quality: String, val desc: String, val url: String)
}
  
""")

# 6. Icons
write_file("app/src/main/res/drawable/ic_launcher_background.xml", """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#121212" android:pathData="M0,0h108v108h-108z" />
</vector>""")

write_file("app/src/main/res/drawable/ic_launcher_foreground.xml", """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
    <path android:strokeWidth="4" android:strokeColor="#FFD700" android:fillColor="#00000000" android:strokeLineJoin="round" android:strokeLineCap="round" android:pathData="M35,45 L35,15 L73,15 L73,45 L95,45 L54,90 L13,45 Z" />
</vector>""")


clean_project()
print("🚀 Clean Install Complete! Run: git add . && git commit -m 'Fresh Install: Hybrid Quality Engine' && git push")

