package org.alituama.mytube.core

import com.yausername.youtubedl_android.YoutubeDL
import com.yausername.youtubedl_android.YoutubeDLRequest
import org.alituama.mytube.utils.BotBypasser
import java.io.File

class DownloadEngine(private val downloadDir: File) {

    fun download(url: String, callback: (String, Float, Long) -> Unit): Boolean {
        // المحاولة 1: عميل Android (الأكثر استقراراً)
        try {
            val request = createRequest(url)
            BotBypasser.applyAntiBotConfig(request, "ANDROID")
            execute(request, callback)
            return true
        } catch (e: Exception) {
            // المحاولة 2: عميل iOS (احتياطي)
            try {
                val request = createRequest(url)
                BotBypasser.applyAntiBotConfig(request, "IOS")
                execute(request, callback)
                return true
            } catch (e2: Exception) {
                // المحاولة 3: وضع التوافق (بدون تحديد عميل)
                throw Exception("All methods failed. Last error: ${e2.message}")
            }
        }
    }

    private fun createRequest(url: String): YoutubeDLRequest {
        val request = YoutubeDLRequest(url)
        request.addOption("-o", downloadDir.absolutePath + "/%(title)s.%(ext)s")
        // صيغة مضمونة لتعمل بدون دمج معقد
        request.addOption("-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")
        return request
    }

    private fun execute(request: YoutubeDLRequest, callback: (String, Float, Long) -> Unit) {
        YoutubeDL.getInstance().execute(request, null) { progress, eta, line ->
            callback(line ?: "Processing", progress, eta)
        }
    }
}