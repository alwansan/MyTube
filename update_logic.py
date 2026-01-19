import os

# ==========================================
# دالة مساعدة
# ==========================================
def create_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Updated: {path}")

# ==========================================
# تحديث MainActivity.kt فقط
# ==========================================
# التغييرات:
# 1. إضافة دالة checkAndRequestPermissions لطلب الإذن من المستخدم.
# 2. تحسين دالة initYoutubeDL لتكون غير متزامنة وتعرض الخطأ على الشاشة.
# 3. منع التحميل إذا لم تكن المكتبة مهيأة.

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
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
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

    private var isLibraryInitialized = false
    private lateinit var tvStatus: TextView
    private val PERMISSION_REQUEST_CODE = 100

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val etUrl = findViewById<TextInputEditText>(R.id.etUrl)
        val btnFetch = findViewById<Button>(R.id.btnFetch)
        tvStatus = findViewById(R.id.tvStatus)
        val tvCredits = findViewById<TextView>(R.id.tvCredits)

        animateCredits(tvCredits)

        // 1. طلب الصلاحيات عند التشغيل
        checkAndRequestPermissions()

        // 2. تهيئة المكتبة في الخلفية
        initYoutubeDL()

        // استقبال المشاركة من يوتيوب
        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            val sharedText = intent.getStringExtra(Intent.EXTRA_TEXT)
            if (sharedText != null) {
                etUrl.setText(sharedText)
            }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) {
                if (isLibraryInitialized) {
                    startDownload(url)
                } else {
                    Toast.makeText(this, "Library not ready yet, wait...", Toast.LENGTH_SHORT).show()
                    initYoutubeDL() // محاولة تهيئة مرة أخرى
                }
            } else {
                // لصق تلقائي
                val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                val clipData = clipboard.primaryClip
                if (clipData != null && clipData.itemCount > 0) {
                    val pasteText = clipData.getItemAt(0).text.toString()
                    etUrl.setText(pasteText)
                    if (isLibraryInitialized) {
                        startDownload(pasteText)
                    }
                }
            }
        }
    }

    private fun checkAndRequestPermissions() {
        val permissions = mutableListOf<String>()
        
        // إذن الكتابة (للأندرويد القديم)
        if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.Q) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                permissions.add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
            }
        }

        // إذن الإشعارات (للأندرويد 13+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                permissions.add(Manifest.permission.POST_NOTIFICATIONS)
            }
        }

        if (permissions.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, permissions.toTypedArray(), PERMISSION_REQUEST_CODE)
        }
    }

    private fun initYoutubeDL() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // التأكد من عدم التهيئة مرتين
                if (isLibraryInitialized) return@launch

                withContext(Dispatchers.Main) {
                    tvStatus.text = "Initializing engines..."
                }

                YoutubeDL.getInstance().init(application)
                isLibraryInitialized = true
                
                withContext(Dispatchers.Main) {
                    tvStatus.text = "Ready to download"
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvStatus.text = "Init Failed: ${e.message}"
                    e.printStackTrace()
                }
            }
        }
    }

    private fun startDownload(url: String) {
        tvStatus.text = "Starting download..."
        
        // المجلد العام للتنزيلات
        val downloadDir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        
        // محاولة إنشاء المجلد
        if (!downloadDir.exists()) {
            try {
                downloadDir.mkdirs()
            } catch (e: Exception) {
                Toast.makeText(this, "Cannot create folder: ${e.message}", Toast.LENGTH_LONG).show()
            }
        }

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val request = YoutubeDLRequest(url)
                request.addOption("-o", downloadDir.absolutePath + "/%(title)s.%(ext)s")
                request.addOption("-f", "bestvideo+bestaudio/best")
                request.addOption("--no-mtime") // لمنع مشاكل الصلاحيات في بعض الأحيان
                
                withContext(Dispatchers.Main) {
                    tvStatus.text = "Downloading..."
                }

                // المتغير الثالث line هو سبب الخطأ السابق وتم إصلاحه هنا
                YoutubeDL.getInstance().execute(request, null) { progress, eta, line ->
                    runOnUiThread {
                        tvStatus.text = "$progress% | ETA: $eta s"
                    }
                }

                withContext(Dispatchers.Main) {
                    tvStatus.text = "✅ Done! Saved in Downloads/MyTube"
                    Toast.makeText(this@MainActivity, "Saved successfully!", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvStatus.text = "❌ Error: ${e.message}"
                }
            }
        }
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
    create_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", kotlin_content)
    
    print("\n🚀 Pushing logic updates to GitHub...")
    import subprocess
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Fix: Add Permissions & Async Init"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! New build triggered.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
