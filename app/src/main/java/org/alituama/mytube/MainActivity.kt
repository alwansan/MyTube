package org.alituama.mytube

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        val urlInput = findViewById<EditText>(R.id.etUrl)
        val downloadBtn = findViewById<Button>(R.id.btnDownload)
        val statusText = findViewById<TextView>(R.id.tvStatus)
        
        downloadBtn.setOnClickListener {
            val url = urlInput.text.toString().trim()
            if (url.isEmpty()) {
                Toast.makeText(this, "الرجاء إدخال رابط", Toast.LENGTH_SHORT).show()
            } else {
                statusText.text = "جارٍ معالجة: $url"
                // في المستقبل: إضافة وظيفة التحميل هنا
                Toast.makeText(this, "الوظيفة قيد التطوير", Toast.LENGTH_SHORT).show()
            }
        }
    }
}
