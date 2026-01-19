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

        try {
            YoutubeDL.getInstance().init(application)
        } catch (e: Exception) {
            e.printStackTrace()
        }

        val etUrl = findViewById<TextInputEditText>(R.id.etUrl)
        val btnFetch = findViewById<Button>(R.id.btnFetch)
        val tvStatus = findViewById<TextView>(R.id.tvStatus)
        val tvCredits = findViewById<TextView>(R.id.tvCredits)

        animateCredits(tvCredits)

        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            val sharedText = intent.getStringExtra(Intent.EXTRA_TEXT)
            if (sharedText != null) {
                etUrl.setText(sharedText)
                startDownload(sharedText, tvStatus)
            }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) {
                startDownload(url, tvStatus)
            } else {
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
        statusView.text = "Initializing..."
        
        val downloadDir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        if (!downloadDir.exists()) downloadDir.mkdirs()

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val request = YoutubeDLRequest(url)
                request.addOption("-o", downloadDir.absolutePath + "/%(title)s.%(ext)s")
                request.addOption("-f", "bestvideo+bestaudio/best") 
                
                withContext(Dispatchers.Main) {
                    statusView.text = "Downloading..."
                }

                // FIX: Added 'line' parameter here because library expects 3 args
                YoutubeDL.getInstance().execute(request, null) { progress, eta, line ->
                    runOnUiThread {
                        statusView.text = "Progress: $progress% (ETA: $eta s)"
                    }
                }

                withContext(Dispatchers.Main) {
                    statusView.text = "Done! Check Downloads/MyTube"
                    Toast.makeText(this@MainActivity, "Saved!", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    statusView.text = "Error: " + e.message
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