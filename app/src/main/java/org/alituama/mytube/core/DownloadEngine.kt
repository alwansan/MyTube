package org.alituama.mytube.core

import com.yausername.youtubedl_android.YoutubeDL
import com.yausername.youtubedl_android.YoutubeDLRequest
import java.io.File

class DownloadEngine(private val saveDir: File) {

    fun download(url: String, callback: (String, Float, Long) -> Unit) {
        // المحاولة 1: iOS (الأفضل لتجاوز البوت و JS)
        try {
            executeDownload(url, "ios", callback)
        } catch (e: Exception) {
            // المحاولة 2: Android Clients
            try {
                executeDownload(url, "android", callback)
            } catch (e2: Exception) {
                // المحاولة 3: Web (القديم)
                throw Exception("Failed: ${e2.message}")
            }
        }
    }

    private fun executeDownload(url: String, client: String, callback: (String, Float, Long) -> Unit) {
        val request = YoutubeDLRequest(url)
        request.addOption("-o", saveDir.absolutePath + "/%(title)s.%(ext)s")
        request.addOption("-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")
        
        // 🔴 إعدادات تجاوز الحظر وحل مشكلة JS
        request.addOption("--no-check-certificates")
        request.addOption("--geo-bypass")
        
        if (client == "ios") {
            // iOS يستخدم API لا تعتمد على JS المعقد
            request.addOption("--extractor-args", "youtube:player_client=ios,ios_creator")
        } else {
            request.addOption("--extractor-args", "youtube:player_client=android,android_creator")
        }

        // 🔴 تخطي فحص JS الذي يسبب الخطأ في أندرويد
        request.addOption("--extractor-args", "youtube:player_skip=js")

        YoutubeDL.getInstance().execute(request, null) { progress, eta, line ->
            callback(line ?: "Processing", progress, eta)
        }
    }
}