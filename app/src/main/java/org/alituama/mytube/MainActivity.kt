package org.alituama.mytube

import android.Manifest
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.text.Editable
import android.text.TextWatcher
import android.util.Log
import android.widget.Button
import android.widget.ProgressBar
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
import java.net.URL

class MainActivity : AppCompatActivity() {

    private lateinit var etUrl: TextInputEditText
    private lateinit var tvStatus: TextView
    private lateinit var progressBar: ProgressBar
    private var isInitialized = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        initViews()
        checkPermissions()
        initializeDownloader()

        // معالجة مشاركة النصوص
        handleSharedIntent()

        // مراقبة التغييرات في الحقل
        etUrl.addTextChangedListener(object : TextWatcher {
            override fun afterTextChanged(s: Editable?) {
                val text = s.toString().trim()
                if (isValidYouTubeUrl(text)) {
                    // يمكن إضافة وظيفة تحميل تلقائي هنا
                }
            }
            
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
        })
    }

    private fun initViews() {
        etUrl = findViewById(R.id.etUrl)
        tvStatus = findViewById(R.id.tvStatus)
        progressBar = findViewById(R.id.progressBar)
        val btnDownload = findViewById<Button>(R.id.btnDownload)

        btnDownload.setOnClickListener {
            val url = etUrl.text.toString().trim()
            if (url.isNotEmpty()) {
                startDownload(url)
            } else {
                checkClipboardAndDownload()
            }
        }
    }

    private fun initializeDownloader() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                withContext(Dispatchers.Main) {
                    tvStatus.text = "جاري التهيئة..."
                    progressBar.visibility = ProgressBar.VISIBLE
                }
                
                YoutubeDL.getInstance().init(application)
                
                withContext(Dispatchers.Main) {
                    tvStatus.text = "جاهز للتحميل"
                    progressBar.visibility = ProgressBar.GONE
                    isInitialized = true
                    
                    // محاولة تحميل الرابط إذا كان موجوداً
                    val savedUrl = etUrl.text.toString().trim()
                    if (savedUrl.isNotEmpty() && isValidYouTubeUrl(savedUrl)) {
                        startDownload(savedUrl)
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    tvStatus.text = "خطأ في التهيئة: ${e.message}"
                    progressBar.visibility = ProgressBar.GONE
                    Log.e("MainActivity", "Initialization error", e)
                }
            }
        }
    }

    private fun startDownload(url: String) {
        if (!isInitialized) {
            Toast.makeText(this, "التطبيق لم يكتمل تهيئته", Toast.LENGTH_SHORT).show()
            return
        }

        if (!isValidYouTubeUrl(url)) {
            Toast.makeText(this, "رابط YouTube غير صحيح", Toast.LENGTH_SHORT).show()
            return
        }

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                withContext(Dispatchers.Main) {
                    tvStatus.text = "جاري التحميل..."
                    progressBar.visibility = ProgressBar.VISIBLE
                }

                val downloadDir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
                if (!downloadDir.exists()) {
                    downloadDir.mkdirs()
                }

                val request = YoutubeDLRequest(url)
                request.addOption("-o", "${downloadDir.absolutePath}/%(title)s.%(ext)s")
                request.addOption("-f", "best[height<=1080][ext=mp4]")
                
                // تجاوز JavaScript
                request.addOption("--extractor-args", "youtube:player_client=android,youtube:player_skip=webpage")
                request.addOption("--no-check-certificates")
                request.addOption("--no-playlist")

                val response = YoutubeDL.getInstance().execute(request)

                withContext(Dispatchers.Main) {
                    progressBar.visibility = ProgressBar.GONE
                    if (response.error) {
                        tvStatus.text = "فشل التحميل"
                        showErrorDialog("خطأ: ${response.outcome}")
                    } else {
                        tvStatus.text = "تم التحميل بنجاح!"
                        Toast.makeText(this@MainActivity, "تم حفظ الفيديو", Toast.LENGTH_LONG).show()
                        etUrl.setText("")
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    progressBar.visibility = ProgressBar.GONE
                    tvStatus.text = "خطأ: ${e.message}"
                    showErrorDialog(e.message ?: "خطأ غير معروف")
                    Log.e("MainActivity", "Download error", e)
                }
            }
        }
    }

    private fun checkClipboardAndDownload() {
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clip = clipboard.primaryClip
        if (clip != null && clip.itemCount > 0) {
            val text = clip.getItemAt(0).text.toString()
            if (isValidYouTubeUrl(text)) {
                etUrl.setText(text)
                startDownload(text)
            } else {
                Toast.makeText(this, "لا يوجد رابط YouTube في الحافظة", Toast.LENGTH_SHORT).show()
            }
        } else {
            Toast.makeText(this, "الحافظة فارغة", Toast.LENGTH_SHORT).show()
        }
    }

    private fun handleSharedIntent() {
        if (intent?.action == Intent.ACTION_SEND) {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { sharedText ->
                if (isValidYouTubeUrl(sharedText)) {
                    etUrl.setText(sharedText)
                    startDownload(sharedText)
                }
            }
        }
    }

    private fun isValidYouTubeUrl(url: String): Boolean {
        return url.contains("youtube.com/watch") || 
               url.contains("youtu.be/") ||
               url.contains("youtube.com/shorts/")
    }

    private fun showErrorDialog(message: String) {
        AlertDialog.Builder(this)
            .setTitle("خطأ")
            .setMessage(message)
            .setPositiveButton("موافق", null)
            .show()
    }

    private fun checkPermissions() {
        val permissions = mutableListOf<String>()
        
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            permissions.add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
        }
        
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            permissions.add(Manifest.permission.READ_EXTERNAL_STORAGE)
        }
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                permissions.add(Manifest.permission.POST_NOTIFICATIONS)
            }
        }

        if (permissions.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, permissions.toTypedArray(), 100)
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == 100) {
            val allGranted = grantResults.all { it == PackageManager.PERMISSION_GRANTED }
            if (!allGranted) {
                Toast.makeText(this, "الصلاحيات مطلوبة للتحميل", Toast.LENGTH_SHORT).show()
            }
        }
    }
}