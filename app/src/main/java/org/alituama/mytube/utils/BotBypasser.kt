package org.alituama.mytube.utils

import com.yausername.youtubedl_android.YoutubeDLRequest

object BotBypasser {
    
    fun applyAntiBotConfig(request: YoutubeDLRequest, mode: String) {
        request.addOption("--no-check-certificates")
        request.addOption("--geo-bypass")
        request.addOption("--no-mtime")
        
        when (mode) {
            "ANDROID" -> {
                // أفضل وضع حالياً
                request.addOption("--extractor-args", "youtube:player_client=android")
                request.addOption("--user-agent", "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")
            }
            "IOS" -> {
                request.addOption("--extractor-args", "youtube:player_client=ios")
                request.addOption("--user-agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1")
            }
            "TV" -> {
                // الوضع الذي حاولت استخدامه سابقاً (يتطلب نسخة حديثة جداً)
                request.addOption("--extractor-args", "youtube:player_client=android_tv")
            }
        }
    }
}