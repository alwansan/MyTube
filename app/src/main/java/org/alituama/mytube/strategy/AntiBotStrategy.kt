package org.alituama.mytube.strategy

import com.yausername.youtubedl_android.YoutubeDLRequest

enum class ClientMode {
    ANDROID_MUSIC,
    ANDROID_MAIN,
    IOS,
    TV_EMBEDDED
}

object AntiBotStrategy {
    
    fun configureRequest(request: YoutubeDLRequest, mode: ClientMode) {
        request.addOption("--no-check-certificates")
        request.addOption("--geo-bypass")
        request.addOption("--no-mtime")
        request.addOption("--compat-options", "no-youtube-unavailable-videos")

        when (mode) {
            ClientMode.ANDROID_MUSIC -> {
                request.addOption("--extractor-args", "youtube:player_client=android_music")
                request.addOption("--user-agent", "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")
            }
            ClientMode.ANDROID_MAIN -> {
                request.addOption("--extractor-args", "youtube:player_client=android")
            }
            ClientMode.IOS -> {
                request.addOption("--extractor-args", "youtube:player_client=ios")
            }
            ClientMode.TV_EMBEDDED -> {
                request.addOption("--extractor-args", "youtube:player_client=android_tv")
            }
        }
    }
}