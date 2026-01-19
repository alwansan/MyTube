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
# 1. الأيقونة: سهم مجوف (Hollow Arrow) - سيرياني
# ==========================================
# الخلفية: رمادي معدني غامق جداً
icon_background = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#1A1A1A"
        android:pathData="M0,0h108v108h-108z" />
    <!-- نقش خفيف -->
    <path
        android:fillColor="#222222"
        android:pathData="M54,0 L108,54 L54,108 L0,54 Z" />
</vector>
"""

# الأمامية: سهم مجوف بحواف ذهبية فقط
icon_foreground = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    
    <!-- جسم السهم المجوف (Stroke Only) -->
    <path
        android:strokeWidth="2.5"
        android:strokeColor="#FFC107"
        android:fillColor="#00000000"
        android:strokeLineJoin="miter"
        android:pathData="M38,45 L38,15 L70,15 L70,45 L88,45 L54,85 L20,45 Z" />
        
    <!-- عين غامضة داخل السهم -->
    <path
        android:fillColor="#FFC107"
        android:pathData="M54,35 a3,3 0 1,0 6,0 a3,3 0 1,0 -6,0" />
        
    <!-- زخارف سيريانية جانبية -->
    <path
        android:strokeWidth="1"
        android:strokeColor="#C5A028"
        android:pathData="M15,54 L25,54 M83,54 L93,54" />
</vector>
"""

# ==========================================
# 2. MainActivity (قائمة السيرفرات النشطة 2026)
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
    
    // 🟢 قائمة السيرفرات العاملة (Updated List)
    // تم اختيار هذه السيرفرات لأنها عامة ولا تطلب مفاتيح
    private val instances = listOf(
        "https://cobalt.aur1.st",       // سيرفر سريع
        "https://api.cobalt.tools",     // الرسمي (قد يطلب auth)
        "https://co.wuk.sh",            // المطور الأصلي
        "https://cobalt.kwiatekmiki.pl" // سيرفر احتياطي
    )
    
    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
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

        etUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val url = s.toString().trim()
                // شرط مخفف جداً للسرعة
                if (url.length > 10 && (url.contains("http")) && url != lastProcessedUrl) {
                    processWithFailover(url)
                }
            }
        })

        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { etUrl.setText(it) }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) processWithFailover(url)
            else checkClipboard()
        }
        
        tvStatus.text = "Ready"
    }

    private fun processWithFailover(url: String) {
        if (isProcessing) return
        isProcessing = true
        lastProcessedUrl = url
        tvStatus.setTextColor(Color.LTGRAY)
        tvStatus.text = "Routing..."

        lifecycleScope.launch(Dispatchers.IO) {
            var success = false
            var lastError = ""

            // تجربة السيرفرات بالتسلسل
            for (baseUrl in instances) {
                try {
                    val serverName = baseUrl.replace("https://", "").split(".")[0]
                    withContext(Dispatchers.Main) { tvStatus.text = "Trying $serverName..." }
                    
                    val apiUrl = "$baseUrl/api/json" // مسار API الموحد
                    
                    val jsonBody = JSONObject()
                    jsonBody.put("url", url)
                    jsonBody.put("vQuality", "720") // 720 الأكثر ضماناً
                    jsonBody.put("filenamePattern", "basic")

                    val request = Request.Builder()
                        .url(apiUrl)
                        .post(jsonBody.toString().toRequestBody("application/json".toMediaType()))
                        .header("Accept", "application/json")
                        .header("Content-Type", "application/json")
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
                            success = true
                            break
                        } else if (status == "picker") {
                            val picker = json.optJSONArray("picker")
                            if (picker != null && picker.length() > 0) {
                                val firstUrl = picker.getJSONObject(0).optString("url")
                                withContext(Dispatchers.Main) { startSystemDownload(firstUrl) }
                                success = true
                                break
                            }
                        }
                    }
                } catch (e: Exception) {
                    lastError = e.message ?: "Error"
                    continue // انتقل للسيرفر التالي
                }
            }

            if (!success) {
                withContext(Dispatchers.Main) {
                    isProcessing = false
                    lastProcessedUrl = ""
                    tvStatus.setTextColor(Color.RED)
                    tvStatus.text = "Connection Failed"
                    showError("Could not connect to any server.\\nLast Error: $lastError")
                }
            }
        }
    }

    private fun startSystemDownload(url: String) {
        try {
            tvStatus.text = "Starting..."
            val request = DownloadManager.Request(Uri.parse(url))
            request.setTitle("MyTube Video")
            request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, "MyTube/video_${System.currentTimeMillis()}.mp4")
            
            val dm = getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
            dm.enqueue(request)

            tvStatus.setTextColor(Color.GREEN)
            tvStatus.text = "✅ Downloading"
            Toast.makeText(this, "Downloading in background", Toast.LENGTH_LONG).show()
            
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
        // أنيميشن ذهبي غامض
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

    private fun showError(msg: String) {
        AlertDialog.Builder(this)
            .setTitle("Server Report")
            .setMessage(msg)
            .setPositiveButton("OK", null)
            .show()
    }
}
"""

if __name__ == "__main__":
    # 1. تحديث الأيقونات
    create_file("app/src/main/res/drawable/ic_launcher_background.xml", icon_background)
    create_file("app/src/main/res/drawable/ic_launcher_foreground.xml", icon_foreground)
    
    # 2. تحديث الكود
    create_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", main_activity_code)
    
    print("\n🚀 Pushing Hollow Arrow & Active Server List...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "UI: Hollow Arrow + Logic: Updated Server List 2026"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! Download should work with new servers.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
