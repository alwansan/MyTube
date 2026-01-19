import os
import shutil
import subprocess

# ==========================================
# 🛠️ أدوات النظام
# ==========================================
def create_file(path, content):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Created: {path}")

def clean_structure():
    # تنظيف لضمان عدم تضارب الملفات
    if os.path.exists("app/src/main/java/org/alituama/mytube/strategy"):
        shutil.rmtree("app/src/main/java/org/alituama/mytube/strategy")
    print("🧹 Cleanup complete.")

# ==========================================
# 1. Gradle (إعدادات البناء)
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
        versionCode = 6
        versionName = "6.0"
        
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
    implementation("io.github.junkfood02.youtubedl-android:library:0.17.2")
    implementation("io.github.junkfood02.youtubedl-android:ffmpeg:0.17.2") 
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
}
"""

# ==========================================
# 2. Helper: الصلاحيات
# ==========================================
permission_helper_code = """package org.alituama.mytube.utils

import android.Manifest
import android.app.Activity
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

object PermissionHelper {
    fun checkAndRequest(activity: Activity) {
        val perms = mutableListOf<String>()
        if (Build.VERSION.SDK_INT >= 33 && ContextCompat.checkSelfPermission(activity, Manifest.permission.POST_NOTIFICATIONS) != 0) {
            perms.add(Manifest.permission.POST_NOTIFICATIONS)
        }
        if (Build.VERSION.SDK_INT <= 29 && ContextCompat.checkSelfPermission(activity, Manifest.permission.WRITE_EXTERNAL_STORAGE) != 0) {
            perms.add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
        }
        if (perms.isNotEmpty()) ActivityCompat.requestPermissions(activity, perms.toTypedArray(), 100)
    }
}
"""

# ==========================================
# 3. Core: مدير المكتبة (التهيئة)
# ==========================================
library_manager_code = """package org.alituama.mytube.core

import android.app.Application
import android.util.Log
import com.yausername.youtubedl_android.YoutubeDL

object LibraryManager {
    fun init(app: Application): Boolean {
        return try {
            YoutubeDL.getInstance().init(app)
            try {
                // محاولة تحديث صامتة، إذا فشلت نستخدم المدمج
                YoutubeDL.getInstance().updateYoutubeDL(app, YoutubeDL.UpdateChannel.STABLE)
            } catch (e: Exception) {
                Log.w("MyTube", "Update failed, staying on version: ${YoutubeDL.getInstance().version(app)}")
            }
            true
        } catch (e: Exception) {
            false
        }
    }
}
"""

# ==========================================
# 4. Core: محرك التنزيل (الحل لمشكلة JS و Bot)
# ==========================================
# التغيير الجذري هنا:
# - إلغاء android_tv لأنه غير مدعوم
# - استخدام ios كخيار أول لأنه لا يحتاج JS
# - إضافة خيار لتخطي فحص JS
download_engine_code = """package org.alituama.mytube.core

import com.yausername.youtubedl_android.YoutubeDL
import com.yausername.youtubedl_android.YoutubeDLRequest
import java.io.File

class DownloadEngine(private val saveDir: File) {

    fun download(url: String, callback: (String, Float, Long) -> Unit) {
        // المحاولة 1: iOS (الأفضل لتجاوز البوت و JS)
        try {
            executeDownload(url, "ios", callback)
        } catch (e: Exception) {
            // المحاولة 2: Android Clients
            try {
                executeDownload(url, "android", callback)
            } catch (e2: Exception) {
                // المحاولة 3: Web (القديم)
                throw Exception("Failed: ${e2.message}")
            }
        }
    }

    private fun executeDownload(url: String, client: String, callback: (String, Float, Long) -> Unit) {
        val request = YoutubeDLRequest(url)
        request.addOption("-o", saveDir.absolutePath + "/%(title)s.%(ext)s")
        request.addOption("-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")
        
        // 🔴 إعدادات تجاوز الحظر وحل مشكلة JS
        request.addOption("--no-check-certificates")
        request.addOption("--geo-bypass")
        
        if (client == "ios") {
            // iOS يستخدم API لا تعتمد على JS المعقد
            request.addOption("--extractor-args", "youtube:player_client=ios,ios_creator")
        } else {
            request.addOption("--extractor-args", "youtube:player_client=android,android_creator")
        }

        // 🔴 تخطي فحص JS الذي يسبب الخطأ في أندرويد
        request.addOption("--extractor-args", "youtube:player_skip=js")

        YoutubeDL.getInstance().execute(request, null) { progress, eta, line ->
            callback(line ?: "Processing", progress, eta)
        }
    }
}
"""

# ==========================================
# 5. UI: الواجهة الجميلة (استعادة الانيميشن)
# ==========================================
main_activity_code = """package org.alituama.mytube.ui

import android.animation.ArgbEvaluator
import android.animation.ObjectAnimator
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.os.Environment
import android.text.Editable
import android.text.TextWatcher
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.google.android.material.textfield.TextInputEditText
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.alituama.mytube.R
import org.alituama.mytube.core.DownloadEngine
import org.alituama.mytube.core.LibraryManager
import org.alituama.mytube.utils.PermissionHelper
import java.io.File

class MainActivity : AppCompatActivity() {

    private lateinit var tvStatus: TextView
    private lateinit var etUrl: TextInputEditText
    private lateinit var tvCredits: TextView
    private var isEngineReady = false
    private var lastUrl = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        tvStatus = findViewById(R.id.tvStatus)
        tvCredits = findViewById(R.id.tvCredits)
        val btnFetch = findViewById<Button>(R.id.btnFetch)

        // ✨ استعادة الانيميشن الجميل
        restoreBeautifulUI()

        PermissionHelper.checkAndRequest(this)

        // تهيئة المحرك
        lifecycleScope.launch(Dispatchers.IO) {
            withContext(Dispatchers.Main) { tvStatus.text = "Initializing Engine..." }
            isEngineReady = LibraryManager.init(application)
            withContext(Dispatchers.Main) { 
                tvStatus.text = if (isEngineReady) "Ready to Download" else "Engine Error"
                if (isEngineReady && etUrl.text.toString().contains("youtu")) {
                    startDownload(etUrl.text.toString())
                }
            }
        }

        etUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val url = s.toString().trim()
                if (url.contains("youtu") && url != lastUrl && isEngineReady) {
                    lastUrl = url
                    startDownload(url)
                }
            }
        })

        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { etUrl.setText(it) }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) startDownload(url)
            else checkClipboard()
        }
    }

    private fun startDownload(url: String) {
        if (!isEngineReady) return

        tvStatus.setTextColor(Color.LTGRAY)
        tvStatus.text = "Processing..."
        
        val dir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        if (!dir.exists()) dir.mkdirs()

        val engine = DownloadEngine(dir)

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                withContext(Dispatchers.Main) { tvStatus.text = "Downloading..." }
                
                engine.download(url) { line, progress, eta ->
                    runOnUiThread {
                        tvStatus.text = "$progress% | ETA: $eta s"
                    }
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

    private fun restoreBeautifulUI() {
        // ✨ انيميشن الألوان المتغيرة للنص (Breathing Effect)
        val colorAnim = ObjectAnimator.ofInt(tvCredits, "textColor",
            Color.RED, Color.YELLOW, Color.WHITE, Color.RED)
        colorAnim.setDuration(3000)
        colorAnim.setEvaluator(ArgbEvaluator())
        colorAnim.repeatCount = ObjectAnimator.INFINITE
        colorAnim.repeatMode = ObjectAnimator.RESTART
        colorAnim.start()
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
            .setTitle("Error Report")
            .setMessage(msg)
            .setPositiveButton("OK", null)
            .show()
    }
}
"""

# ==========================================
# التنفيذ والرفع
# ==========================================
clean_structure()
create_file("app/build.gradle.kts", build_gradle_content)
create_file("app/src/main/java/org/alituama/mytube/utils/PermissionHelper.kt", permission_helper_code)
create_file("app/src/main/java/org/alituama/mytube/core/LibraryManager.kt", library_manager_code)
create_file("app/src/main/java/org/alituama/mytube/core/DownloadEngine.kt", download_engine_code)
create_file("app/src/main/java/org/alituama/mytube/ui/MainActivity.kt", main_activity_code)

print("\n🚀 Pushing Restoration Fix (UI + iOS Strategy) to GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Fix: Restore UI Animations + Fix Bot Issue using iOS Client"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ Pushed successfully!")
except Exception as e:
    print(f"❌ Git Error: {e}")
