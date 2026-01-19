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
# 1. تصميم الأيقونة (سهم مجوف غامض)
# ==========================================
# الخلفية: رمادي فحمي معتم
icon_background = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#121212"
        android:pathData="M0,0h108v108h-108z" />
    <path
        android:fillColor="#1C1C1C"
        android:pathData="M54,0 L108,0 L54,108 L0,108 Z" />
</vector>
"""

# الأمامية: سهم مجوف (حواف ذهبية فقط)
icon_foreground = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    
    <!-- السهم المجوف (Outline) -->
    <path
        android:strokeWidth="3"
        android:strokeColor="#FFD700"
        android:fillColor="#00000000"
        android:strokeLineJoin="round"
        android:strokeLineCap="round"
        android:pathData="M34,48 L34,22 L74,22 L74,48 L92,48 L54,86 L16,48 Z" />
        
    <!-- زخرفة سيريانية داخلية (خط عمودي) -->
    <path
        android:strokeWidth="1.5"
        android:strokeColor="#C5A028"
        android:strokeLineCap="round"
        android:pathData="M54,28 L54,65" />
        
    <!-- نقطة غامضة في الأسفل -->
    <path
        android:fillColor="#FFD700"
        android:pathData="M54,94 a2,2 0 1,0 4,0 a2,2 0 1,0 -4,0" />
</vector>
"""

# ==========================================
# 2. MainActivity (قائمة سيرفرات جديدة ونظيفة)
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
    
    // قائمة سيرفرات جديدة ومحدثة (تعمل في 2025/2026)
    // تم حذف السيرفرات الميتة وإضافة سيرفرات نشطة
    private val instances = listOf(
        "https://cobalt.aur1.st",      // سيرفر قوي جداً
        "https://co.wuk.sh",           // سيرفر المطور الأصلي (غالباً مزدحم لكن يعمل)
        "https://cobalt.kwiatekmiki.pl", // سيرفر احتياطي
        "https://api.cobalt.tools"     // الرسمي (كخيار أخير)
    )
    
    private val client = OkHttpClient.Builder()
        .connectTimeout(20, TimeUnit.SECONDS) // تقليل وقت الانتظار لتسريع التبديل
        .readTimeout(20, TimeUnit.SECONDS)
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
                if (url.length > 10 && (url.contains("http") || url.contains("youtu")) && url != lastProcessedUrl) {
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
        tvStatus.text = "Searching..."

        lifecycleScope.launch(Dispatchers.IO) {
            var success = false
            var lastError = ""

            for (baseUrl in instances) {
                try {
                    withContext(Dispatchers.Main) { 
                        // عرض اسم السيرفر الذي يتم تجربته حالياً (بدون https)
                        val serverName = baseUrl.replace("https://", "").replace("api.", "")
                        tvStatus.text = "Trying $serverName..." 
                    }
                    
                    val apiUrl = "$baseUrl/api/json"
                    
                    val jsonBody = JSONObject()
                    jsonBody.put("url", url)
                    jsonBody.put("videoQuality", "720")
                    jsonBody.put("filenameStyle", "basic")

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
                        } else {
                            // إذا كان الخطأ متعلق بالحظر، ننتقل للسيرفر التالي
                            val errText = json.optString("text").lowercase()
                            if (errText.contains("key") || errText.contains("auth") || errText.contains("limit")) {
                                throw Exception("Auth Blocked")
                            }
                        }
                    }
                } catch (e: Exception) {
                    lastError = e.message ?: "Connect Error"
                    continue
                }
            }

            if (!success) {
                withContext(Dispatchers.Main) {
                    isProcessing = false
                    lastProcessedUrl = ""
                    tvStatus.setTextColor(Color.RED)
                    tvStatus.text = "All Servers Busy"
                    showError("Connection Failed.\\nLast Error: $lastError")
                }
            }
        }
    }

    private fun startSystemDownload(url: String) {
        try {
            tvStatus.text = "Downloading..."
            val request = DownloadManager.Request(Uri.parse(url))
            request.setTitle("MyTube Video")
            request.setDescription("Downloading content...")
            request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, "MyTube/video_${System.currentTimeMillis()}.mp4")
            
            val dm = getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
            dm.enqueue(request)

            tvStatus.setTextColor(Color.GREEN)
            tvStatus.text = "✅ Started"
            Toast.makeText(this, "Started! Check Notifications.", Toast.LENGTH_LONG).show()
            
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
        val colorAnim = ObjectAnimator.ofInt(tvCredits, "textColor",
            Color.parseColor("#FFD700"), 
            Color.parseColor("#424242"), 
            Color.parseColor("#FFD700"))
        colorAnim.setDuration(5000)
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
            .setTitle("Report")
            .setMessage(msg)
            .setPositiveButton("OK", null)
            .show()
    }
}
"""

if __name__ == "__main__":
    # تحديث الأيقونات
    create_file("app/src/main/res/drawable/ic_launcher_background.xml", icon_background)
    create_file("app/src/main/res/drawable/ic_launcher_foreground.xml", icon_foreground)
    
    # تحديث الكود
    create_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", main_activity_code)
    
    print("\n🚀 Pushing Hollow Arrow Icon & New Server List...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "UI: Hollow Arrow Icon + Logic: Updated 2026 Server List"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! Check the new design.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
