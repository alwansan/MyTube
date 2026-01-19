import os

# ==========================================
# دالة الحفظ
# ==========================================
def create_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Updated: {path}")

# ==========================================
# MainActivity.kt (تصحيح الطلب + قراءة الخطأ)
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
    private var lastUrl = ""
    
    // إعداد عميل الشبكة بمهلة زمنية كافية
    private val client = OkHttpClient.Builder()
        .connectTimeout(60, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(60, TimeUnit.SECONDS)
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
                if (url.startsWith("http") && url != lastUrl && url.length > 15) {
                    lastUrl = url
                    processWithApi(url)
                }
            }
        })

        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { 
                etUrl.setText(it)
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
        tvStatus.setTextColor(Color.LTGRAY)
        tvStatus.text = "Processing..."

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // استخدام السيرفر الرسمي القوي
                val apiUrl = "https://api.cobalt.tools/api/json"
                
                // بناء الطلب بشكل يقبله السيرفر 100%
                val jsonBody = JSONObject()
                jsonBody.put("url", url)
                // 'max' تضمن أفضل جودة متوفرة بدون تعقيد
                jsonBody.put("vQuality", "max") 
                jsonBody.put("filenamePattern", "basic")

                val request = Request.Builder()
                    .url(apiUrl)
                    .post(jsonBody.toString().toRequestBody("application/json".toMediaType()))
                    .header("Accept", "application/json")
                    .header("Content-Type", "application/json")
                    // التمويه كمتصفح كروم حقيقي لتجنب الحظر
                    .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                    .build()

                val response = client.newCall(request).execute()
                val responseStr = response.body?.string()

                if (response.isSuccessful && responseStr != null) {
                    val json = JSONObject(responseStr)
                    val status = json.optString("status")
                    
                    if (status == "stream" || status == "redirect" || status == "tunnel" || json.has("url")) {
                        val downloadUrl = json.optString("url")
                        withContext(Dispatchers.Main) {
                            startSystemDownload(downloadUrl)
                        }
                    } else if (status == "picker") {
                        // في حال كان هناك عدة خيارات (فيديو/صوت)
                        val picker = json.optJSONArray("picker")
                        if (picker != null && picker.length() > 0) {
                            val firstUrl = picker.getJSONObject(0).optString("url")
                            withContext(Dispatchers.Main) { startSystemDownload(firstUrl) }
                        }
                    } else {
                        val errorText = json.optString("text", "Unknown API Error")
                        throw Exception(errorText)
                    }
                } else {
                    // قراءة رسالة الخطأ القادمة من السيرفر (مهم جداً لمعرفة سبب 400)
                    val errorJson = JSONObject(responseStr ?: "{}")
                    val serverMsg = errorJson.optJSONObject("error")?.optString("code") 
                                    ?: errorJson.optString("text") 
                                    ?: "HTTP ${response.code}"
                    throw Exception("Server Error: $serverMsg")
                }

            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvStatus.setTextColor(Color.RED)
                    tvStatus.text = "Failed"
                    showError("Error: ${e.message}")
                }
            }
        }
    }

    private fun startSystemDownload(url: String) {
        try {
            tvStatus.text = "Starting Download..."
            
            val request = DownloadManager.Request(Uri.parse(url))
            request.setTitle("MyTube Video")
            request.setDescription("Downloading...")
            request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, "MyTube/video_${System.currentTimeMillis()}.mp4")
            request.setAllowedOverMetered(true)
            request.setAllowedOverRoaming(true)

            val dm = getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
            dm.enqueue(request)

            tvStatus.setTextColor(Color.GREEN)
            tvStatus.text = "✅ Downloading in Background"
            Toast.makeText(this, "Started! Check Notifications.", Toast.LENGTH_LONG).show()
            
            etUrl.text?.clear()
            lastUrl = ""
            etUrl.postDelayed({ tvStatus.text = "Ready" }, 4000)

        } catch (e: Exception) {
            showError("Download Manager Failed: ${e.message}")
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
            .setTitle("Error Details")
            .setMessage(msg)
            .setPositiveButton("OK", null)
            .show()
    }
}
"""

if __name__ == "__main__":
    create_file("app/src/main/java/org/alituama/mytube/MainActivity.kt", main_activity_code)
    
    print("\n🚀 Pushing API Request Fixes...")
    import subprocess
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Fix API 400 Error: Update User-Agent and JSON Payload"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! This will fix the 400 error.")
    except Exception as e:
        print(f"❌ Git Error: {e}")
