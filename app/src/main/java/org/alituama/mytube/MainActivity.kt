package org.alituama.mytube

import android.animation.ArgbEvaluator
import android.animation.ObjectAnimator
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.os.Environment
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.google.android.material.textfield.TextInputEditText
import com.yausername.youtubedl_android.YoutubeDL
import com.yausername.youtubedl_android.YoutubeDLRequest
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // 1. تهيئة مكتبة التحميل
        try {
            YoutubeDL.getInstance().init(application)
        } catch (e: Exception) {
            Toast.makeText(this, "Error initializing libs", Toast.LENGTH_LONG).show()
        }

        val etUrl = findViewById<TextInputEditText>(R.id.etUrl)
        val btnFetch = findViewById<Button>(R.id.btnFetch)
        val tvStatus = findViewById<TextView>(R.id.tvStatus)
        val tvCredits = findViewById<TextView>(R.id.tvCredits)

        // 2. تشغيل انيميشن الحقوق
        animateCredits(tvCredits)

        // 3. التعامل مع المشاركة (Share Intent)
        // عند مشاركة رابط من يوتيوب، سيتم وضعه هنا تلقائياً
        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            val sharedText = intent.getStringExtra(Intent.EXTRA_TEXT)
            if (sharedText != null) {
                etUrl.setText(sharedText)
                startDownload(sharedText, tvStatus) // بدء تلقائي
            }
        }

        // 4. زر البحث واللصق
        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) {
                startDownload(url, tvStatus)
            } else {
                // لصق تلقائي إذا كان الحقل فارغاً
                val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                val clipData = clipboard.primaryClip
                if (clipData != null && clipData.itemCount > 0) {
                    val pasteText = clipData.getItemAt(0).text.toString()
                    etUrl.setText(pasteText)
                    startDownload(pasteText, tvStatus)
                }
            }
        }
    }

    private fun startDownload(url: String, statusView: TextView) {
        statusView.text = "Initializing download..."
        
        // المسار: /storage/emulated/0/Download/MyTube
        val downloadDir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        if (!downloadDir.exists()) downloadDir.mkdirs()

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // إعدادات التحميل: أفضل فيديو + أفضل صوت
                val request = YoutubeDLRequest(url)
                request.addOption("-o", downloadDir.absolutePath + "/%(title)s.%(ext)s")
                request.addOption("-f", "bestvideo+bestaudio/best") 
                
                withContext(Dispatchers.Main) {
                    statusView.text = "Downloading... (Check notifications)"
                }

                // بدء التحميل
                YoutubeDL.getInstance().execute(request) { progress, eta ->
                    runOnUiThread {
                        statusView.text = "Progress: $progress% (ETA: $eta s)"
                    }
                }

                withContext(Dispatchers.Main) {
                    statusView.text = "✅ Download Complete!"
                    Toast.makeText(this@MainActivity, "Saved to MyTube folder", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    statusView.text = "❌ Error: ${e.message}"
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