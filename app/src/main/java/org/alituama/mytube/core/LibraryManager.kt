package org.alituama.mytube.core

import android.app.Application
import android.util.Log
import com.yausername.youtubedl_android.YoutubeDL

object LibraryManager {
    fun initialize(app: Application): Boolean {
        return try {
            YoutubeDL.getInstance().init(app)
            try {
                YoutubeDL.getInstance().updateYoutubeDL(app, YoutubeDL.UpdateChannel.STABLE)
            } catch (e: Exception) {
                Log.w("MyTube", "Update failed, using embedded version")
            }
            true
        } catch (e: Exception) {
            Log.e("MyTube", "Init failed", e)
            false
        }
    }
}