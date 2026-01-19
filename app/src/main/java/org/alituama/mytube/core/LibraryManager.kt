package org.alituama.mytube.core

import android.app.Application
import android.util.Log
import com.yausername.youtubedl_android.YoutubeDL

object LibraryManager {
    fun init(app: Application): Boolean {
        return try {
            YoutubeDL.getInstance().init(app)
            try {
                // محاولة تحديث صامتة، إذا فشلت نستخدم المدمج
                YoutubeDL.getInstance().updateYoutubeDL(app, YoutubeDL.UpdateChannel.STABLE)
            } catch (e: Exception) {
                Log.w("MyTube", "Update failed, staying on version: ${YoutubeDL.getInstance().version(app)}")
            }
            true
        } catch (e: Exception) {
            false
        }
    }
}