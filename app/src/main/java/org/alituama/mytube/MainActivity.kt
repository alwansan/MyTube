package org.alituama.mytube

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

        // 1. تشغيل الأنيميشن (التصميم الجميل)
        startAnimations()

        // 2. طلب الصلاحيات
        checkPermissions()

        // 3. تهيئة المكتبة وتحديثها
        initEngine()

        // 4. مراقبة النص للتنزيل التلقائي
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

        // 5. استقبال المشاركة
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
                withContext(Dispatchers.Main) { tvStatus.text = "Initializing..." }
                YoutubeDL.getInstance().init(application)
                
                withContext(Dispatchers.Main) { tvStatus.text = "Updating Core..." }
                // محاولة تحديث المكتبة للحصول على أحدث التواقيع
                try {
                    YoutubeDL.getInstance().updateYoutubeDL(application, YoutubeDL.UpdateChannel.STABLE)
                } catch (e: Exception) {
                    Log.w("MyTube", "Update failed: ${e.message}")
                }

                isLibraryReady = true
                withContext(Dispatchers.Main) { 
                    tvStatus.text = "Ready (Engine Active)"
                    // إذا كان هناك رابط تم لصقه، ابدأ العمل
                    if (etUrl.text.toString().contains("youtu")) {
                        startDownload(etUrl.text.toString())
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) { tvStatus.text = "Init Error (Check Logs)" }
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
                
                // =======================================================
                // 🔴 الخلطة السرية المستوحاة من كود البوت الخاص بك
                // =======================================================
                request.addOption("--no-check-certificates")
                request.addOption("--geo-bypass")
                
                // استخدام User-Agent الخاص بالكمبيوتر (مثل البوت الخاص بك)
                request.addOption("--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                
                // استخدام عميل iOS لأنه الأقوى حالياً ضد البوت
                request.addOption("--extractor-args", "youtube:player_client=ios")
                
                // تخطي فحص JS المزعج
                request.addOption("--extractor-args", "youtube:player_skip=js")

                withContext(Dispatchers.Main) { tvStatus.text = "Downloading..." }

                YoutubeDL.getInstance().execute(request, null) { progress, eta, line ->
                    // استخدام النوع الصريح للمتغيرات لمنع خطأ البناء
                    val p: Float = progress
                    val e: Long = eta
                    val l: String? = line
                    runOnUiThread { 
                        tvStatus.text = "$p% | ETA: $e s" 
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

    private fun startAnimations() {
        // انيميشن الألوان للنص السفلي
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
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), 100)
            }
        }
        if (Build.VERSION.SDK_INT <= 29) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
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
            .setTitle("Error Report")
            .setMessage(msg)
            .setPositiveButton("OK", null)
            .show()
    }
}