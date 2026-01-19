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
# 1. تصميم الأيقونة الفاخرة (Vector XML)
# ==========================================
# أيقونة خلفية (رمادي غامق)
icon_background = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#263238"
        android:pathData="M0,0h108v108h-108z" />
</vector>
"""

# أيقونة أمامية (شعار التنزيل باللون الرمادي الفضي)
icon_foreground = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#CFD8DC"
        android:pathData="M54,19c-19.33,0 -35,15.67 -35,35 0,19.33 15.67,35 35,35s35,-15.67 35,-35c0,-19.33 -15.67,-35 -35,-35zM54,82c-15.46,0 -28,-12.54 -28,-28 0,-15.46 12.54,-28 28,-28s28,12.54 28,28c0,15.46 -12.54,28 -28,28z" />
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M54,39l-13,13h8v14h10v-14h8z" />
    <path
        android:fillColor="#B0BEC5"
        android:pathData="M41,68h26v4h-26z" />
</vector>
"""

# ملف تعريف الأيقونة المتكيفة
ic_launcher_xml = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background" />
    <foreground android:drawable="@drawable/ic_launcher_foreground" />
</adaptive-icon>
"""

# ==========================================
# 2. تحديث AndroidManifest لاستخدام الأيقونة
# ==========================================
manifest_content = """<?xml version="1.0" encoding="utf-8"?>
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
        android:requestLegacyExternalStorage="true"
        android:supportsRtl="true"
        android:theme="@style/Theme.MyTube.Dialog"
        android:usesCleartextTraffic="true" 
        tools:targetApi="31">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.MyTube.Dialog">
            
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
"""

# ==========================================
# 3. تحديث MainActivity (معالجة الأخطاء بدقة)
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
                if (url.startsWith("http") && url.length > 15 && tvStatus.text == "Ready") {
                    processWithApi(url)
                }
            }
        })

        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { etUrl.setText(it) }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) processWithApi(url)
            else checkClipboard()
        }
        
        tvStatus.text = "Ready"
    }

    private fun processWithApi(url: String) {
        tvStatus.setTextColor(Color.LTGRAY)
        tvStatus.text = "Connecting..."

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // 🟢 استخدام سيرفر API مستقر
                val apiUrl = "https://api.cobalt.tools"
                
                val jsonBody = JSONObject()
                jsonBody.put("url", url)
                // الإعدادات القياسية لـ Cobalt
                jsonBody.put("videoQuality", "720") // جودة آمنة ومضمونة
                jsonBody.put("audioFormat", "mp3")
                jsonBody.put("filenameStyle", "classic")

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
                    
                    // حالات النجاح المختلفة
                    if (status == "stream" || status == "redirect" || status == "tunnel") {
                        val downloadUrl = json.optString("url")
                        withContext(Dispatchers.Main) { startSystemDownload(downloadUrl) }
                    } 
                    else if (status == "picker") {
                        // إذا أرجع قائمة، نأخذ الأول
                        val picker = json.optJSONArray("picker")
                        if (picker != null && picker.length() > 0) {
                            val firstUrl = picker.getJSONObject(0).optString("url")
                            withContext(Dispatchers.Main) { startSystemDownload(firstUrl) }
                        }
                    }
                    else if (status == "error") {
                        // قراءة الخطأ القادم من السيرفر
                        val text = json.optString("text", "Unknown Error")
                        throw Exception(text)
                    }
                } else {
                    // قراءة تفاصيل الفشل (400/500)
                    val errorMsg = try {
                        val errJson = JSONObject(responseStr ?: "{}")
                        errJson.optString("text") ?: "Code: ${response.code}"
                    } catch (e: Exception) {
                        "HTTP Error ${response.code}"
                    }
                    throw Exception(errorMsg)
                }

            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
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
            request.setTitle("MyTube Video")
            request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, "MyTube/video_${System.currentTimeMillis()}.mp4")
            
            val dm = getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
            dm.enqueue(request)

            tvStatus.setTextColor(Color.GREEN)
            tvStatus.text = "✅ Started"
            Toast.makeText(this, "Check Notifications!", Toast.LENGTH_LONG).show()
            etUrl.text?.clear()
            etUrl.postDelayed({ tvStatus.text = "Ready" }, 3000)

        } catch (e: Exception) {
            showError("System Error: ${e.message}")
        }
    }

    private fun startAnimations() {
        val colorAnim = ObjectAnimator.ofInt(tvCredits, "textColor",
            Color.GRAY, Color.WHITE, Color.LTGRAY, Color.GRAY)
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
    # 1. إنشاء ملفات الأيقونة
    create_file("app/src/main/res/drawable/ic_launcher_background.xml", icon_background)
    create_file("app/src/main/res/drawable/ic_launcher_foreground.xml", icon_foreground)
    
    # 2. إنشاء مجلد mipmap (للأيقونة الرسمية)
    mipmap_dir = "app/src/main/res/mipmap-anydpi-v26"
    if not os.path.exists(mipmap_dir): os.makedirs(mipmap_dir)
    create_file(f"{mipmap_dir}/ic_launcher.xml", ic_launcher_xml)

    # 3. تحديث الكود والمانيفيست
    create_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", main_activity_code)
    create_file("app/src/main/AndroidManifest.xml", manifest_content)
    
    print("\n🚀 Pushing Luxury Gray Update & API Fixes...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "UI: New Gray Icon + Logic: Improved Error Handling"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! Enjoy the new look.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
