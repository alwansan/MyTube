package org.alituama.mytube.ui

import android.Manifest
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
import org.alituama.mytube.R
import org.alituama.mytube.core.DownloadEngine
import org.alituama.mytube.core.LibraryManager
import java.io.File

class MainActivity : AppCompatActivity() {

    private lateinit var tvStatus: TextView
    private lateinit var etUrl: TextInputEditText
    private var isReady = false
    private var lastUrl = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        tvStatus = findViewById(R.id.tvStatus)
        val btnFetch = findViewById<Button>(R.id.btnFetch)
        val tvCredits = findViewById<TextView>(R.id.tvCredits)

        setupPermissions()
        initializeApp()

        // التنفيذ التلقائي
        etUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val url = s.toString().trim()
                if (url.contains("youtu") && url != lastUrl && isReady) {
                    lastUrl = url
                    startDownloadProcess(url)
                }
            }
        })

        // الاستقبال من المشاركة
        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { etUrl.setText(it) }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) startDownloadProcess(url)
            else checkClipboard()
        }
    }

    private fun initializeApp() {
        lifecycleScope.launch(Dispatchers.IO) {
            withContext(Dispatchers.Main) { tvStatus.text = "Initializing System..." }
            
            val initResult = LibraryManager.init(application)
            
            withContext(Dispatchers.Main) { tvStatus.text = "Updating Engine..." }
            val updateResult = LibraryManager.update(application)
            
            isReady = true
            withContext(Dispatchers.Main) { 
                tvStatus.text = "Ready ($updateResult)"
                // فحص إذا كان هناك رابط تم لصقه أثناء التهيئة
                if (etUrl.text.toString().contains("youtu")) {
                    startDownloadProcess(etUrl.text.toString())
                }
            }
        }
    }

    private fun startDownloadProcess(url: String) {
        tvStatus.setTextColor(Color.LTGRAY)
        tvStatus.text = "Starting Engine..."
        
        val dir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        if (!dir.exists()) dir.mkdirs()

        val engine = DownloadEngine(dir)

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                withContext(Dispatchers.Main) { tvStatus.text = "Downloading..." }
                
                engine.download(url) { line, progress, eta ->
                    runOnUiThread {
                        tvStatus.text = "$progress% | ETA: $eta s"
                    }
                }

                withContext(Dispatchers.Main) {
                    tvStatus.setTextColor(Color.GREEN)
                    tvStatus.text = "✅ Success!"
                    Toast.makeText(this@MainActivity, "Video Saved!", Toast.LENGTH_LONG).show()
                    etUrl.text?.clear()
                    lastUrl = ""
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvStatus.setTextColor(Color.RED)
                    tvStatus.text = "Failed"
                    AlertDialog.Builder(this@MainActivity)
                        .setTitle("Download Error")
                        .setMessage(e.message)
                        .setPositiveButton("OK", null)
                        .show()
                }
            }
        }
    }

    private fun setupPermissions() {
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
}