package org.alituama.mytube.ui

import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.os.Environment
import android.text.Editable
import android.text.TextWatcher
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.google.android.material.textfield.TextInputEditText
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.alituama.mytube.R
import org.alituama.mytube.core.DownloadManager
import org.alituama.mytube.core.LibraryManager
import org.alituama.mytube.utils.PermissionHelper
import java.io.File

class MainActivity : AppCompatActivity() {

    private lateinit var tvStatus: TextView
    private lateinit var etUrl: TextInputEditText
    private var isEngineReady = false
    private var lastProcessedUrl = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etUrl = findViewById(R.id.etUrl)
        tvStatus = findViewById(R.id.tvStatus)
        val btnFetch = findViewById<Button>(R.id.btnFetch)

        PermissionHelper.checkAndRequest(this)

        lifecycleScope.launch(Dispatchers.IO) {
            withContext(Dispatchers.Main) { tvStatus.text = "Initializing Engine..." }
            isEngineReady = LibraryManager.initialize(application)
            withContext(Dispatchers.Main) { 
                tvStatus.text = if (isEngineReady) "Ready" else "Engine Error"
                if (etUrl.text.toString().contains("youtu")) executeDownload(etUrl.text.toString())
            }
        }

        etUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val url = s.toString().trim()
                if (url.contains("youtu") && url != lastProcessedUrl && isEngineReady) {
                    lastProcessedUrl = url
                    executeDownload(url)
                }
            }
        })

        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { etUrl.setText(it) }
        }

        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) executeDownload(url)
            else checkClipboard()
        }
    }

    private fun executeDownload(url: String) {
        if (!isEngineReady) return

        val dir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        if (!dir.exists()) dir.mkdirs()

        val manager = DownloadManager(dir)

        lifecycleScope.launch(Dispatchers.IO) {
            manager.startDownload(
                url = url,
                onProgress = { msg ->
                    runOnUiThread { tvStatus.text = msg }
                },
                onSuccess = {
                    runOnUiThread {
                        tvStatus.text = "✅ Download Complete"
                        Toast.makeText(this@MainActivity, "Saved to Downloads", Toast.LENGTH_LONG).show()
                        etUrl.text?.clear()
                        lastProcessedUrl = ""
                    }
                },
                onError = { error ->
                    runOnUiThread {
                        tvStatus.text = "Failed"
                        showError(error)
                    }
                }
            )
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