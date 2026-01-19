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
# 1. الأيقونة الغامضة (نجمة سيريانية مريبة)
# ==========================================
# الخلفية: رمادي داكن معدني (مريب)
icon_background = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#212121"
        android:pathData="M0,0h108v108h-108z" />
    <!-- تأثير ظلال غامضة -->
    <path
        android:fillColor="#000000"
        android:fillAlpha="0.3"
        android:pathData="M54,54 m-45,0 a45,45 0 1,0 90,0 a45,45 0 1,0 -90,0" />
</vector>
"""

# الأمامية: نجمة ثمانية سيريانية بخطوط ذهبية حادة
icon_foreground = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    
    <!-- النجمة الثمانية (رمز سيرياني قديم) -->
    <path
        android:fillColor="#FFC107"
        android:pathData="M54,14 L61,40 L88,40 L66,56 L74,82 L54,68 L34,82 L42,56 L20,40 L47,40 Z" />
        
    <!-- عين في الوسط (لإضافة الغموض) -->
    <path
        android:fillColor="#212121"
        android:pathData="M54,48 C58,48 61,51 61,55 C61,59 58,62 54,62 C50,62 47,59 47,55 C47,51 50,48 54,48 Z" />
        
    <!-- خطوط إشعاعية -->
    <path
        android:strokeColor="#FFC107"
        android:strokeWidth="1"
        android:pathData="M54,14 L54,8 M54,94 L54,100 M14,54 L8,54 M94,54 L100,54" />
</vector>
"""

# ==========================================
# 2. تحديث MainActivity (نظام السيرفرات البديلة)
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
    
    // قائمة سيرفرات بديلة قوية (تتجاوز الحظر)
    private val apiInstances = listOf(
        "https://cobalt.kwiatekmiki.pl", // سيرفر بولندي قوي
        "https://api.cobalt.tools",      // الرسمي (قد يكون محظوراً لكن نجربه)
        "https://cobalt.synced.vip"      // سيرفر بديل
    )
    
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
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
                    processWithMultiServer(url)
                }
            }
        })

        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { etUrl.setText(it) }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) processWithMultiServer(url)
            else checkClipboard()
        }
        
        tvStatus.text = "Ready"
    }

    private fun processWithMultiServer(url: String) {
        if (isProcessing) return
        isProcessing = true
        lastProcessedUrl = url
        tvStatus.setTextColor(Color.LTGRAY)
        tvStatus.text = "Searching..."

        lifecycleScope.launch(Dispatchers.IO) {
            var success = false
            var lastError = ""

            // تجربة السيرفرات واحداً تلو الآخر
            for (apiUrl in apiInstances) {
                try {
                    withContext(Dispatchers.Main) { tvStatus.text = "Trying Server..." }
                    
                    val jsonBody = JSONObject()
                    jsonBody.put("url", url)
                    jsonBody.put("videoQuality", "720")
                    jsonBody.put("filenameStyle", "basic")

                    val request = Request.Builder()
                        .url("$apiUrl/api/json") // الصيغة القياسية للسيرفرات البديلة
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
                            break // نجاح! نخرج من الحلقة
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
                    lastError = e.message ?: "Unknown"
                    continue // نجرب السيرفر التالي
                }
            }

            if (!success) {
                withContext(Dispatchers.Main) {
                    isProcessing = false
                    lastProcessedUrl = ""
                    tvStatus.setTextColor(Color.RED)
                    tvStatus.text = "All Servers Failed"
                    showError("Connection Error: $lastError")
                }
            }
        }
    }

    private fun startSystemDownload(url: String) {
        try {
            tvStatus.text = "Downloading..."
            val request = DownloadManager.Request(Uri.parse(url))
            request.setTitle("MyTube Download")
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
        // أنيميشن ذهبي غامض
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
    
    print("\n🚀 Pushing Mysterious Star Update & Server Bypass...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "UI: Mysterious Syriac Star + Logic: Multi-Server Bypass"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! Check the new icon and logic.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
