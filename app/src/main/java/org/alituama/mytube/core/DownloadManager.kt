package org.alituama.mytube.core

import com.yausername.youtubedl_android.YoutubeDL
import com.yausername.youtubedl_android.YoutubeDLRequest
import org.alituama.mytube.strategy.AntiBotStrategy
import org.alituama.mytube.strategy.ClientMode
import java.io.File

class DownloadManager(private val saveDir: File) {

    fun startDownload(url: String, onProgress: (String) -> Unit, onSuccess: () -> Unit, onError: (String) -> Unit) {
        
        val strategies = listOf(
            ClientMode.ANDROID_MUSIC,
            ClientMode.ANDROID_MAIN,
            ClientMode.IOS,
            ClientMode.TV_EMBEDDED
        )

        var lastError = ""

        for (mode in strategies) {
            try {
                onProgress("Trying Strategy: ${mode.name}...")
                
                val request = YoutubeDLRequest(url)
                request.addOption("-o", saveDir.absolutePath + "/%(title)s.%(ext)s")
                request.addOption("-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")
                
                AntiBotStrategy.configureRequest(request, mode)

                YoutubeDL.getInstance().execute(request, null) { progress, eta, _ ->
                    onProgress("$progress% | ETA: $eta s")
                }
                
                onSuccess()
                return 

            } catch (e: Exception) {
                lastError = e.message ?: "Unknown Error"
                continue
            }
        }
        
        onError("All strategies failed. Last error: $lastError")
    }
}