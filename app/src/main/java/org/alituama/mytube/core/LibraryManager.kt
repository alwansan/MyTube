package org.alituama.mytube.core

import android.app.Application
import android.util.Log
import com.yausername.youtubedl_android.YoutubeDL

object LibraryManager {
    fun init(app: Application): String {
        return try {
            // 1. التهيئة الأولية (فك الضغط)
            YoutubeDL.getInstance().init(app)
            "Initialized"
        } catch (e: Exception) {
            "Init Error: ${e.message}"
        }
    }

    fun update(app: Application): String {
        return try {
            // 2. تحديث المحرك لتجاوز مشكلة Unsupported Client
            // هذا يسحب أحدث نسخة من yt-dlp GitHub
            YoutubeDL.getInstance().updateYoutubeDL(app, YoutubeDL.UpdateChannel.STABLE)
            "Updated to Latest Version"
        } catch (e: Exception) {
            "Update Failed (Using Embedded): ${e.message}"
        }
    }
}