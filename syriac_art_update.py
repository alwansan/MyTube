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
# 1. تصميم الأيقونة (الفن السرياني الهندسي)
# ==========================================
# الخلفية: لون كحلي/أسود ليلي عميق
icon_background = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#101820"
        android:pathData="M0,0h108v108h-108z" />
    <!-- زخرفة خلفية خفيفة -->
    <path
        android:fillColor="#1A2530"
        android:pathData="M54,0 L108,54 L54,108 L0,54 Z" />
</vector>
"""

# الأمامية: تشكيل هندسي ذهبي يشبه الزخارف السريانية القديمة مدمج مع رمز التشغيل
icon_foreground = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    
    <!-- الإطار الزخرفي الذهبي -->
    <path
        android:fillColor="#D4AF37"
        android:pathData="M54,24 L60,34 L70,34 L62,42 L65,52 L54,46 L43,52 L46,42 L38,34 L48,34 Z" />
        
    <!-- رمز التشغيل في الوسط (أبيض نقي) -->
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M48,38 L64,48 L48,58 Z" />
        
    <!-- خطوط هندسية سفلية -->
    <path
        android:fillColor="#C5A028"
        android:pathData="M34,65 L74,65 L70,70 L38,70 Z M40,74 L68,74 L66,78 L42,78 Z" />
</vector>
"""

# ==========================================
# 2. تحديث MainActivity (إصلاح المنطق والخطأ)
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
import androidx.lifecycle.lifecycleScope
import com.google.android.material.textfield.TextInputEditText
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
    
    private val client = OkHttpClient.Builder()
        .connectTimeout(60, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
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

        // 🟢 الإصلاح 1: مراقب النص الذكي (يعمل فوراً عند اللصق)
        etUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val url = s.toString().trim()
                // الشرط المخفف: رابط يحتوي على http ولم يتم معالجته للتو
                if (url.length > 10 && (url.contains("http") || url.contains("youtu")) && url != lastProcessedUrl) {
                    processWithApi(url)
                }
            }
        })

        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { 
                etUrl.setText(it) // سيقوم المراقب أعلاه بتشغيل التنزيل تلقائياً
            }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) processWithApi(url)
            else checkClipboard()
        }
        
        tvStatus.text = "Ready"
    }

    private fun processWithApi(url: String) {
        if (isProcessing) return
        
        isProcessing = true
        lastProcessedUrl = url // منع التكرار
        tvStatus.setTextColor(Color.LTGRAY)
        tvStatus.text = "Processing..."

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val apiUrl = "https://api.cobalt.tools/api/json" // الرجوع لنقطة النهاية المستقرة
                
                val jsonBody = JSONObject()
                jsonBody.put("url", url)
                jsonBody.put("vQuality", "720") // 720 هو الأكثر استقراراً حالياً
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
                    
                    if (status == "stream" || status == "redirect" || status == "tunnel" || json.has("url")) {
                        val downloadUrl = json.optString("url")
                        withContext(Dispatchers.Main) { startSystemDownload(downloadUrl) }
                    } else if (status == "picker") {
                        val picker = json.optJSONArray("picker")
                        if (picker != null && picker.length() > 0) {
                            val firstUrl = picker.getJSONObject(0).optString("url")
                            withContext(Dispatchers.Main) { startSystemDownload(firstUrl) }
                        }
                    } else {
                        // محاولة قراءة النص
                        val errText = json.optString("text")
                        throw Exception(if (errText.isNotEmpty()) errText else "API Status: $status")
                    }
                } else {
                    // 🟢 الإصلاح 2: استخراج نص الخطأ الحقيقي بدقة
                    val errorMsg = try {
                        val errJson = JSONObject(responseStr ?: "{}")
                        // Cobalt يرسل الخطأ أحياناً في "text" وأحياناً في "error.code"
                        val textErr = errJson.optString("text")
                        val codeErr = errJson.optJSONObject("error")?.optString("code")
                        
                        when {
                            textErr.isNotEmpty() -> textErr
                            !codeErr.isNullOrEmpty() -> "Code: $codeErr"
                            else -> "Server returned ${response.code}"
                        }
                    } catch (e: Exception) {
                        "HTTP Error ${response.code}"
                    }
                    throw Exception(errorMsg)
                }

            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    isProcessing = false
                    lastProcessedUrl = "" // السماح بالمحاولة مرة أخرى
                    tvStatus.setTextColor(Color.RED)
                    tvStatus.text = "Error"
                    showError("API Says: ${e.message}")
                }
            }
        }
    }

    private fun startSystemDownload(url: String) {
        try {
            tvStatus.text = "Downloading..."
            val request = DownloadManager.Request(Uri.parse(url))
            request.setTitle("MyTube Download")
            request.setDescription("Downloading content...")
            request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, "MyTube/video_${System.currentTimeMillis()}.mp4")
            
            val dm = getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
            dm.enqueue(request)

            tvStatus.setTextColor(Color.GREEN)
            tvStatus.text = "✅ Started"
            Toast.makeText(this, "Started! Check Notifications.", Toast.LENGTH_LONG).show()
            
            // إعادة تعيين الحالة بعد فترة قصيرة
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
            Color.parseColor("#FFD700"), // ذهبي
            Color.WHITE, 
            Color.parseColor("#C0C0C0"), // فضي
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
            .setTitle("Report")
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
    
    print("\n🚀 Pushing Syriac Art UI & Logic Fixes...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "UI: Syriac Art Icon + Logic: Fix AutoFetch & Error Parsing"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! Check the new artistic look.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
