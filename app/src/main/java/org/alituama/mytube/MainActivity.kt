package org.alituama.mytube

import android.Manifest
import android.app.AlertDialog
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.text.Editable
import android.text.TextWatcher
import android.view.View
import android.webkit.CookieManager
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
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
import java.util.concurrent.atomic.AtomicBoolean

class MainActivity : AppCompatActivity() {

    private lateinit var tvStatus: TextView
    private lateinit var etUrl: EditText
    private lateinit var progressBar: ProgressBar
    private lateinit var webView: WebView 
    private var lastUrl = ""
    private var isEngineReady = false
    private val isAnalysisRunning = AtomicBoolean(false)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        tvStatus = findViewById(R.id.tvStatus)
        progressBar = findViewById(R.id.progressBar)
        webView = findViewById(R.id.webView)
        val btnFetch = findViewById<Button>(R.id.btnFetch)

        // 1. Setup the "Stealth Browser"
        setupHiddenBrowser()
        
        // 2. Permission Check
        checkPermissions()
        
        // 3. Boot Engine
        initEngine()

        etUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val url = s.toString().trim()
                // Auto-trigger if it looks like a valid link and we aren't already busy
                if (url.length > 10 && (url.contains("http") || url.contains("youtu")) && url != lastUrl && !isAnalysisRunning.get()) {
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

    private fun setupHiddenBrowser() {
        // This WebView acts as our "Mozilla" to bypass bot checks
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            // Spoof as a standard Android Chrome to blend in
            userAgentString = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
            mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
        }
        
        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                // Cookies are automatically stored in CookieManager
            }
        }
        
        // Clear old sessions for a fresh start
        CookieManager.getInstance().removeAllCookies(null)
        CookieManager.getInstance().flush()
    }

    private fun initEngine() {
        tvStatus.text = "IGNITING ENGINE..."
        tvStatus.setTextColor(Color.GRAY)
        progressBar.visibility = View.VISIBLE

        CoroutineScope(Dispatchers.IO).launch {
            try {
                // Initialize yt-dlp binary
                YoutubeDL.getInstance().init(applicationContext)
                
                // Silent update attempt
                try {
                    YoutubeDL.getInstance().updateYoutubeDL(applicationContext, YoutubeDL.UpdateChannel.STABLE)
                } catch (e: Exception) { e.printStackTrace() }

                isEngineReady = true
                withContext(Dispatchers.Main) {
                    tvStatus.text = "READY (ARM64)"
                    tvStatus.setTextColor(Color.GREEN)
                    progressBar.visibility = View.INVISIBLE
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvStatus.text = "ENGINE ERROR"
                    tvStatus.setTextColor(Color.RED)
                    showErrorDialog("Init Failed: ${e.message}")
                }
            }
        }
    }

    private fun processUrl(url: String) {
        if (!isEngineReady) {
            Toast.makeText(this, "Engine booting...", Toast.LENGTH_SHORT).show()
            return
        }
        
        isAnalysisRunning.set(true)
        lastUrl = url
        tvStatus.text = "BYPASSING BOT CHECK..."
        tvStatus.setTextColor(Color.parseColor("#FFD700")) // Gold
        progressBar.visibility = View.VISIBLE
        
        // STEP 1: Load URL in hidden WebView to generate valid cookies
        webView.loadUrl(url)
        
        // Wait 4 seconds for JS execution and Cookie generation
        Handler(Looper.getMainLooper()).postDelayed({
            extractCookiesAndAnalyze(url)
        }, 4000)
    }

    private fun extractCookiesAndAnalyze(url: String) {
        val cookies = CookieManager.getInstance().getCookie(url)
        val userAgent = webView.settings.userAgentString
        
        if (cookies == null || cookies.isEmpty()) {
            tvStatus.text = "RETRYING BYPASS..."
            // Give it 2 more seconds
            Handler(Looper.getMainLooper()).postDelayed({ 
                // Fallback: Proceed even if cookies are empty, maybe it's a public video
                 performAnalysis(url, CookieManager.getInstance().getCookie(url) ?: "", userAgent)
            }, 2000)
            return
        }
        
        performAnalysis(url, cookies, userAgent)
    }

    private fun performAnalysis(url: String, cookies: String, userAgent: String) {
        tvStatus.text = "ANALYZING STREAM..."
        
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val request = YoutubeDLRequest(url)
                
                // CRITICAL: Inject Browser Credentials
                if (cookies.isNotEmpty()) request.addHeader("Cookie", cookies)
                request.addHeader("User-Agent", userAgent)
                
                request.addOption("--no-playlist")
                request.addOption("--no-check-certificate")
                request.addOption("--geo-bypass")
                // Force Android client simulation to avoid JS player issues
                request.addOption("--extractor-args", "youtube:player_client=android") 

                val info: VideoInfo = YoutubeDL.getInstance().getInfo(request)
                
                withContext(Dispatchers.Main) {
                    progressBar.visibility = View.INVISIBLE
                    isAnalysisRunning.set(false)
                    showFormatSelector(info, url, cookies, userAgent)
                }

            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    progressBar.visibility = View.INVISIBLE
                    isAnalysisRunning.set(false)
                    tvStatus.text = "FAILED"
                    tvStatus.setTextColor(Color.RED)
                    // Common error: Sign in required. Cookies should fix this.
                    showErrorDialog("Analysis Failed: ${e.message}")
                }
            }
        }
    }

    private fun showFormatSelector(info: VideoInfo, url: String, cookies: String, userAgent: String) {
        val formats = info.formats ?: emptyList()
        val options = ArrayList<VideoOption>()
        val title = info.title ?: "Video"

        val seenQualities = HashSet<String>()
        for (f in formats) {
            // Filter for valid video streams
            if (f.vcodec != "none" && f.height > 0) {
                val q = "${f.height}p"
                if (!seenQualities.contains(q)) {
                    val desc = if (f.acodec != "none") "Standard" else "Video Only"
                    options.add(VideoOption(q, desc, f.formatId ?: ""))
                    seenQualities.add(q)
                }
            }
        }
        
        // Sort high to low
        options.sortByDescending { it.quality.replace("p", "").toIntOrNull() ?: 0 }
        options.add(VideoOption("Audio Only", "MP3", "bestaudio/best"))

        if (options.isEmpty()) {
            tvStatus.text = "NO FORMATS"
            return
        }

        val builder = AlertDialog.Builder(this, R.style.SyriacDialog)
        builder.setTitle(title)
        val adapter = ArrayAdapter(this, android.R.layout.select_dialog_singlechoice, options.map { "${it.quality} | ${it.desc}" })
        
        builder.setAdapter(adapter) { _, which ->
            val selected = options[which]
            startDownload(title, url, selected.formatId, selected.quality, cookies, userAgent)
        }
        
        builder.setOnCancelListener { 
            tvStatus.text = "READY" 
            tvStatus.setTextColor(Color.GRAY)
        }
        builder.show()
    }

    private fun startDownload(title: String, url: String, formatId: String, qualityLabel: String, cookies: String, userAgent: String) {
        tvStatus.text = "DOWNLOADING..."
        tvStatus.setTextColor(Color.GREEN)
        progressBar.visibility = View.VISIBLE
        
        val downloadDir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        if (!downloadDir.exists()) downloadDir.mkdirs()

        CoroutineScope(Dispatchers.IO).launch {
            try {
                val cleanTitle = title.replace(Regex("[^a-zA-Z0-9.-]"), "_")
                val request = YoutubeDLRequest(url)
                
                // Inject Credentials for Download
                if (cookies.isNotEmpty()) request.addHeader("Cookie", cookies)
                request.addHeader("User-Agent", userAgent)
                
                if (qualityLabel == "Audio Only") {
                     request.addOption("-f", "bestaudio/best")
                     request.addOption("-x")
                     request.addOption("--audio-format", "mp3")
                } else {
                     request.addOption("-f", "$formatId+bestaudio/best")
                }
                
                request.addOption("-o", downloadDir.absolutePath + "/%(title)s.%(ext)s")
                request.addOption("--no-mtime")
                request.addOption("--no-check-certificate")
                
                YoutubeDL.getInstance().execute(request, null) { progress, eta, line -> }

                withContext(Dispatchers.Main) {
                    progressBar.visibility = View.INVISIBLE
                    tvStatus.text = "COMPLETE"
                    Toast.makeText(applicationContext, "Saved to Downloads/MyTube", Toast.LENGTH_LONG).show()
                    etUrl.text.clear()
                }

            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    progressBar.visibility = View.INVISIBLE
                    tvStatus.text = "ERROR"
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