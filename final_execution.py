import os
import shutil
import subprocess

# ==========================================
# 🛠️ الأدوات المساعدة
# ==========================================
def create_file(path, content):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Created: {path}")

def clean_structure():
    # تنظيف شامل لضمان عدم بقاء كود قديم
    paths = [
        "app/src/main/java/org/alituama/mytube/core",
        "app/src/main/java/org/alituama/mytube/utils",
        "app/src/main/java/org/alituama/mytube/strategy",
        "app/src/main/java/org/alituama/mytube/ui"
    ]
    for p in paths:
        if os.path.exists(p): shutil.rmtree(p)
    print("🧹 Workspace cleaned.")

# ==========================================
# 1. Gradle (إجبار النظام على استخدام أحدث الأدوات)
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
        versionCode = 8
        versionName = "8.0"
        
        ndk {
            abiFilters.add("armeabi-v7a")
            abiFilters.add("arm64-v8a")
            abiFilters.add("x86")
            abiFilters.add("x86_64")
        }
    }

    packaging {
        jniLibs { useLegacyPackaging = true }
        resources { excludes += "/META-INF/{AL2.0,LGPL2.1}" }
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
    kotlinOptions { jvmTarget = "1.8" }
    buildFeatures { viewBinding = true }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    
    // المكتبة المحدثة (JunkFood02 Fork)
    implementation("io.github.junkfood02.youtubedl-android:library:0.17.2")
    implementation("io.github.junkfood02.youtubedl-android:ffmpeg:0.17.2") 
    
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
}
"""

# ==========================================
# 2. MainActivity (المنطق الجديد كلياً)
# ==========================================
main_activity_code = """package org.alituama.mytube

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
    private lateinit var tvCredits: TextView
    private var isLibraryReady = false
    private var lastUrl = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        tvStatus = findViewById(R.id.tvStatus)
        tvCredits = findViewById(R.id.tvCredits)
        val btnFetch = findViewById<Button>(R.id.btnFetch)

        // تجميل الواجهة
        startAnimations()
        
        // طلب الصلاحيات
        checkPermissions()

        // تهيئة النظام
        initEngine()

        // مراقب النص (تلقائي)
        etUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val url = s.toString().trim()
                if (url.contains("youtu") && url != lastUrl && isLibraryReady) {
                    lastUrl = url
                    startDownload(url)
                }
            }
        })

        // المشاركة من يوتيوب
        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { etUrl.setText(it) }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) startDownload(url)
            else checkClipboard()
        }
    }

    private fun initEngine() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                withContext(Dispatchers.Main) { tvStatus.text = "Initializing System..." }
                YoutubeDL.getInstance().init(application)
                
                withContext(Dispatchers.Main) { tvStatus.text = "Updating Keys..." }
                try {
                    YoutubeDL.getInstance().updateYoutubeDL(application, YoutubeDL.UpdateChannel.STABLE)
                } catch (e: Exception) {
                    Log.w("MyTube", "Update warning: ${e.message}")
                }

                isLibraryReady = true
                withContext(Dispatchers.Main) { 
                    tvStatus.text = "Ready (Native Mode)"
                    if (etUrl.text.toString().contains("youtu")) startDownload(etUrl.text.toString())
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) { tvStatus.text = "Error: ${e.message}" }
            }
        }
    }

    private fun startDownload(url: String) {
        if (!isLibraryReady) return

        tvStatus.setTextColor(Color.LTGRAY)
        tvStatus.text = "Processing..."
        
        val dir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        if (!dir.exists()) dir.mkdirs()

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val request = YoutubeDLRequest(url)
                request.addOption("-o", dir.absolutePath + "/%(title)s.%(ext)s")
                request.addOption("-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")
                
                // ==================================================================
                // 🔐 الحل النهائي: انتحال شخصية تطبيق يوتيوب الرسمي (API)
                // ==================================================================
                
                // 1. تحديد العميل على أنه ANDROID (التطبيق الرسمي، ليس المتصفح)
                // هذا يمنع طلب JS Runtime لأن التطبيق لا يستخدمه
                request.addOption("--extractor-args", "youtube:player_client=android")
                
                // 2. استخدام User-Agent لهاتف حقيقي (Pixel 8) يستخدم التطبيق
                request.addOption("--user-agent", "com.google.android.youtube/19.29.35 (Linux; U; Android 14; en_US) google/pixel_8_pro")
                
                // 3. تخطي فحص JS بشكل صريح (لإزالة التحذير الأول)
                request.addOption("--extractor-args", "youtube:player_skip=js")
                
                // 4. إعدادات الشبكة
                request.addOption("--no-check-certificates")
                request.addOption("--geo-bypass")

                withContext(Dispatchers.Main) { tvStatus.text = "Downloading..." }

                YoutubeDL.getInstance().execute(request, null) { progress, eta, line ->
                    val p: Float = progress
                    val e: Long = eta
                    runOnUiThread { tvStatus.text = "$p% | ETA: $e s" }
                }

                withContext(Dispatchers.Main) {
                    tvStatus.setTextColor(Color.GREEN)
                    tvStatus.text = "✅ Success!"
                    Toast.makeText(this@MainActivity, "Saved to Downloads/MyTube", Toast.LENGTH_LONG).show()
                    etUrl.text?.clear()
                    lastUrl = ""
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvStatus.setTextColor(Color.RED)
                    tvStatus.text = "Failed"
                    showError(e.message ?: "Unknown Error")
                }
            }
        }
    }

    private fun startAnimations() {
        val colorAnim = ObjectAnimator.ofInt(tvCredits, "textColor",
            Color.RED, Color.YELLOW, Color.WHITE, Color.RED)
        colorAnim.setDuration(3000)
        colorAnim.setEvaluator(ArgbEvaluator())
        colorAnim.repeatCount = ObjectAnimator.INFINITE
        colorAnim.repeatMode = ObjectAnimator.RESTART
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
            .setTitle("Details")
            .setMessage(msg)
            .setPositiveButton("OK", null)
            .show()
    }
}
"""

# ==========================================
# تنفيذ العملية والرفع
# ==========================================
clean_structure()
create_file("app/build.gradle.kts", build_gradle_content)
create_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", main_activity_code)

print("\n🚀 Pushing Final Native-App Spoofing Fix...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Final Fix: Impersonate Official YouTube App (No JS required)"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ Done! Check GitHub Actions.")
except Exception as e:
    print(f"❌ Git Error: {e}")
