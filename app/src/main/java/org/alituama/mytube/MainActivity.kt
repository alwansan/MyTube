package org.alituama.mytube

import android.Manifest
import android.app.AlertDialog
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
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.yausername.youtubedl_android.YoutubeDL
import com.yausername.youtubedl_android.YoutubeDLRequest
import com.yausername.youtubedl_android.mapper.VideoInfo
import kotlinx.coroutines.*
import java.io.File

class MainActivity : AppCompatActivity() {

    private lateinit var tvStatus: TextView
    private lateinit var etUrl: EditText
    private lateinit var progressBar: ProgressBar
    private var lastUrl = ""
    private var isEngineReady = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        tvStatus = findViewById(R.id.tvStatus)
        progressBar = findViewById(R.id.progressBar)
        val btnFetch = findViewById<Button>(R.id.btnFetch)

        checkPermissions()
        
        // 1. Initialize the heavy engine (Background Thread)
        initEngine()

        etUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val url = s.toString().trim()
                if (url.length > 10 && (url.contains("http") || url.contains("youtu")) && url != lastUrl) {
                    processUrl(url)
                }
            }
        })

        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { etUrl.setText(it) }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) processUrl(url)
            else checkClipboard()
        }
    }

    private fun initEngine() {
        tvStatus.text = "BOOTING ENGINE..."
        tvStatus.setTextColor(Color.GRAY)
        progressBar.visibility = View.VISIBLE

        CoroutineScope(Dispatchers.IO).launch {
            try {
                // Initialize the library (Extracts Python/FFmpeg from APK)
                YoutubeDL.getInstance().init(applicationContext)

                withContext(Dispatchers.Main) {
                    tvStatus.text = "CHECKING UPDATES..."
                }

                // Update yt-dlp binary from internet (Crucial for fixing bugs)
                try {
                     YoutubeDL.getInstance().updateYoutubeDL(applicationContext, YoutubeDL.UpdateChannel.STABLE)
                } catch (e: Exception) {
                    // Ignore update errors if offline
                }

                isEngineReady = true
                withContext(Dispatchers.Main) {
                    tvStatus.text = "ENGINE READY"
                    tvStatus.setTextColor(Color.GREEN)
                    progressBar.visibility = View.INVISIBLE
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvStatus.text = "ENGINE FAILURE"
                    tvStatus.setTextColor(Color.RED)
                    showErrorDialog("Failed to initialize yt-dlp engine: ${e.message}")
                }
            }
        }
    }

    private fun processUrl(url: String) {
        if (!isEngineReady) {
            Toast.makeText(this, "Engine is still booting...", Toast.LENGTH_SHORT).show()
            return
        }

        lastUrl = url
        tvStatus.text = "ANALYZING (DEEP)..."
        tvStatus.setTextColor(Color.parseColor("#FFD700"))
        progressBar.visibility = View.VISIBLE

        CoroutineScope(Dispatchers.IO).launch {
            try {
                val request = YoutubeDLRequest(url)
                request.addOption("--no-playlist")
                val info: VideoInfo = YoutubeDL.getInstance().getInfo(request)
                
                withContext(Dispatchers.Main) {
                    progressBar.visibility = View.INVISIBLE
                    showFormatSelector(info, url)
                }

            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    progressBar.visibility = View.INVISIBLE
                    tvStatus.text = "ANALYSIS FAILED"
                    tvStatus.setTextColor(Color.RED)
                    showErrorDialog(e.message ?: "Unknown Error")
                }
            }
        }
    }

    private fun showFormatSelector(info: VideoInfo, url: String) {
        val formats = info.formats ?: emptyList()
        val options = ArrayList<VideoOption>()
        val title = info.title ?: "Video"

        val seenQualities = HashSet<String>()
        for (f in formats) {
            if (f.vcodec != "none" && f.height > 0) {
                val q = "${f.height}p"
                if (!seenQualities.contains(q)) {
                    val desc = if (f.acodec != "none") "Standard" else "High Quality"
                    options.add(VideoOption(q, desc, f.formatId ?: ""))
                    seenQualities.add(q)
                }
            }
        }
        
        options.sortByDescending { it.quality.replace("p", "").toIntOrNull() ?: 0 }
        options.add(VideoOption("Audio Only", "MP3/M4A", "bestaudio/best"))

        if (options.isEmpty()) {
            tvStatus.text = "NO FORMATS"
            return
        }

        val builder = AlertDialog.Builder(this, R.style.SyriacDialog)
        builder.setTitle(title)
        val adapter = ArrayAdapter(this, android.R.layout.select_dialog_singlechoice, options.map { "${it.quality} | ${it.desc}" })
        
        builder.setAdapter(adapter) { _, which ->
            val selected = options[which]
            startDownload(title, url, selected.formatId, selected.quality)
        }
        
        builder.setOnCancelListener { 
            tvStatus.text = "READY" 
            tvStatus.setTextColor(Color.GRAY)
        }
        builder.show()
    }

    private fun startDownload(title: String, url: String, formatId: String, qualityLabel: String) {
        tvStatus.text = "DOWNLOADING..."
        tvStatus.setTextColor(Color.GREEN)
        progressBar.visibility = View.VISIBLE
        
        val downloadDir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        if (!downloadDir.exists()) downloadDir.mkdirs()

        CoroutineScope(Dispatchers.IO).launch {
            try {
                val cleanTitle = title.replace(Regex("[^a-zA-Z0-9.-]"), "_")
                val fileName = "${cleanTitle}_${qualityLabel}.%(ext)s"
                
                val request = YoutubeDLRequest(url)
                if (qualityLabel == "Audio Only") {
                     request.addOption("-f", "bestaudio/best")
                     request.addOption("-x")
                     request.addOption("--audio-format", "mp3")
                } else {
                     request.addOption("-f", "$formatId+bestaudio/best")
                }
                
                request.addOption("-o", downloadDir.absolutePath + "/%(title)s.%(ext)s")
                request.addOption("--no-mtime")
                
                YoutubeDL.getInstance().execute(request, null) { progress, eta, line -> }

                withContext(Dispatchers.Main) {
                    progressBar.visibility = View.INVISIBLE
                    tvStatus.text = "DOWNLOAD COMPLETE"
                    Toast.makeText(applicationContext, "Saved to Downloads/MyTube", Toast.LENGTH_LONG).show()
                    etUrl.text.clear()
                }

            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    progressBar.visibility = View.INVISIBLE
                    tvStatus.text = "DOWNLOAD ERROR"
                    tvStatus.setTextColor(Color.RED)
                    showErrorDialog(e.message ?: "Download failed")
                }
            }
        }
    }

    private fun showErrorDialog(msg: String) {
        AlertDialog.Builder(this, R.style.SyriacDialog)
            .setTitle("Error")
            .setMessage(msg)
            .setPositiveButton("OK", null)
            .show()
    }

    private fun checkClipboard() {
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clip = clipboard.primaryClip
        if (clip != null && clip.itemCount > 0) {
            etUrl.setText(clip.getItemAt(0).text.toString())
        }
    }

    private fun checkPermissions() {
        if (Build.VERSION.SDK_INT >= 33 && ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != 0) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), 100)
        }
        if (Build.VERSION.SDK_INT <= 29 && ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != 0) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.WRITE_EXTERNAL_STORAGE), 101)
        }
    }

    data class VideoOption(val quality: String, val desc: String, val formatId: String)
}