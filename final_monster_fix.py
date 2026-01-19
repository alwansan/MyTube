import os
import subprocess

def create_file(path, content):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Executed: {path}")

# ==========================================
# 1. تثبيت الإصدارات في Gradle
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
        versionCode = 2
        versionName = "2.0"
        
        // إجبار النظام على دمج كل المكتبات
        ndk {
            abiFilters.add("armeabi-v7a")
            abiFilters.add("arm64-v8a")
            abiFilters.add("x86")
            abiFilters.add("x86_64")
        }
    }

    packaging {
        jniLibs {
            useLegacyPackaging = true
        }
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
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
    
    // استخدام النسخة الموثوقة
    implementation("io.github.junkfood02.youtubedl-android:library:0.17.2")
    implementation("io.github.junkfood02.youtubedl-android:ffmpeg:0.17.2") 
    
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
}
"""

# ==========================================
# 2. المنطق الكامل (Auto Fetch + Anti-Bot + JS Fix)
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
    private val PERMISSION_REQUEST_CODE = 100
    private var isLibraryReady = false
    // متغير لمنع التكرار عند الكتابة السريعة
    private var lastUrlProcessed = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        val btnFetch = findViewById<Button>(R.id.btnFetch)
        tvStatus = findViewById(R.id.tvStatus)
        val tvCredits = findViewById<TextView>(R.id.tvCredits)

        animateCredits(tvCredits)
        requestPermissionsSafely()
        initAndUpdateEngine()

        // 1. التنزيل التلقائي عند اللصق أو الكتابة
        etUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val url = s.toString().trim()
                // شرط: أن يكون رابط يوتيوب ولم يتم معالجته للتو
                if ((url.contains("youtu.be") || url.contains("youtube.com")) && url != lastUrlProcessed) {
                    if (isLibraryReady) {
                        lastUrlProcessed = url
                        startDownload(url)
                    }
                }
            }
        })

        // 2. استقبال المشاركة من تطبيق يوتيوب
        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { 
                etUrl.setText(it) // سيتم تشغيل التنزيل تلقائياً بسبب المراقب أعلاه
            }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) {
                startDownload(url)
            } else {
                checkClipboard()
            }
        }
    }

    private fun initAndUpdateEngine() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // فك الضغط الأولي
                YoutubeDL.getInstance().init(application)
                
                withContext(Dispatchers.Main) { tvStatus.text = "Checking updates..." }
                
                // تحديث المحرك الداخلي
                YoutubeDL.getInstance().updateYoutubeDL(application, YoutubeDL.UpdateChannel.STABLE)
                
                isLibraryReady = true
                withContext(Dispatchers.Main) { 
                    tvStatus.text = "Ready (Latest Engine)"
                    // التحقق إذا كان هناك نص جاهز للمعالجة
                    val currentText = etUrl.text.toString()
                    if (currentText.isNotEmpty() && (currentText.contains("youtu"))) {
                         startDownload(currentText)
                    }
                }
            } catch (e: Exception) {
                // في حالة الفشل، نستمر لأن المكتبة الأصلية موجودة
                isLibraryReady = true
                withContext(Dispatchers.Main) { 
                    tvStatus.text = "Ready (Offline Mode)" 
                }
            }
        }
    }

    private fun startDownload(url: String) {
        // إعادة تعيين الحالة لتجنب "Failed" القديمة
        tvStatus.setTextColor(Color.LTGRAY) 
        tvStatus.text = "Processing..."
        
        val downloadDir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        if (!downloadDir.exists()) downloadDir.mkdirs()

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val request = YoutubeDLRequest(url)
                
                // ============================================================
                // 🔴 الحل السحري لمشكلة JS و Bot
                // ============================================================
                
                // 1. استخدام عميل Android (يتجاوز الحاجة لـ JS Runtime)
                request.addOption("--extractor-args", "youtube:player_client=android")
                
                // 2. تمويه المتصفح
                request.addOption("--user-agent", "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")
                
                // 3. تجاوز فحص الشهادات والموقع
                request.addOption("--no-check-certificates")
                request.addOption("--geo-bypass")
                
                // 4. إعدادات الصيغة والمكان
                request.addOption("-o", downloadDir.absolutePath + "/%(title)s.%(ext)s")
                request.addOption("-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")

                withContext(Dispatchers.Main) { tvStatus.text = "Downloading..." }

                YoutubeDL.getInstance().execute(request, null) { progress, eta, line ->
                    runOnUiThread { tvStatus.text = "$progress% | ETA: $eta s" }
                }

                withContext(Dispatchers.Main) {
                    tvStatus.setTextColor(Color.GREEN)
                    tvStatus.text = "✅ Done! Saved in Downloads/MyTube"
                    Toast.makeText(this@MainActivity, "Saved successfully!", Toast.LENGTH_LONG).show()
                    etUrl.text?.clear() 
                    lastUrlProcessed = "" // السماح بتنزيل جديد
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvStatus.setTextColor(Color.RED)
                    tvStatus.text = "Error (Retrying...)"
                    // محاولة أخيرة باستخدام عميل Web إذا فشل Android
                    retryDownloadWeb(url, downloadDir, e.message ?: "")
                }
            }
        }
    }

    // محاولة ثانية في حال فشل الطريقة الأولى
    private fun retryDownloadWeb(url: String, dir: File, originalError: String) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val request = YoutubeDLRequest(url)
                request.addOption("-o", dir.absolutePath + "/%(title)s.%(ext)s")
                // استخدام عميل iOS كبديل
                request.addOption("--extractor-args", "youtube:player_client=ios")
                request.addOption("-f", "best")
                
                YoutubeDL.getInstance().execute(request, null) { progress, eta, line ->
                    runOnUiThread { tvStatus.text = "Retry: $progress%" }
                }
                
                withContext(Dispatchers.Main) {
                     tvStatus.setTextColor(Color.GREEN)
                     tvStatus.text = "✅ Done (via Backup Mode)"
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvStatus.text = "Failed"
                    showErrorDialog("Failed with both methods.\\n1. $originalError\\n2. ${e.message}")
                }
            }
        }
    }

    private fun checkClipboard() {
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clipData = clipboard.primaryClip
        if (clipData != null && clipData.itemCount > 0) {
            val pasteText = clipData.getItemAt(0).text.toString()
            etUrl.setText(pasteText)
        }
    }

    private fun requestPermissionsSafely() {
        if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.Q) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.WRITE_EXTERNAL_STORAGE), PERMISSION_REQUEST_CODE)
            }
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
             if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), PERMISSION_REQUEST_CODE)
            }
        }
    }

    private fun showErrorDialog(msg: String) {
        AlertDialog.Builder(this)
            .setTitle("Error")
            .setMessage(msg)
            .setPositiveButton("OK", null)
            .show()
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
    
    print("\n🚀 Injecting Final Monster Fix...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Monster Fix: Auto-Fetch + Android Client Spoofing"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! Cache errors are normal, check the 'Artifacts' section in GitHub Actions.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
