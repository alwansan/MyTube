import os
import shutil

# ==========================================
# 1. تنظيف المشروع من ملفات الويب القديمة
# ==========================================
files_to_remove = [
    "package.json", "package-lock.json", "yarn.lock", "vite.config.ts",
    "tsconfig.json", "tsconfig.app.json", "tsconfig.node.json", "index.html",
    "tailwind.config.js", "postcss.config.js", "eslint.config.js",
    "eslint.dualite.config.js", "netlify.toml", "README.md"
]
folders_to_remove = ["src", "public", "node_modules", "dist"]

print("🧹 جاري تنظيف المشروع من ملفات React/Web...")

for f in files_to_remove:
    if os.path.exists(f):
        os.remove(f)
        print(f"❌ تم حذف الملف: {f}")

for d in folders_to_remove:
    if os.path.exists(d):
        shutil.rmtree(d)
        print(f"❌ تم حذف المجلد: {d}")

# ==========================================
# 2. تعريف ملفات تطبيق الأندرويد (Kotlin)
# ==========================================
print("\n🏗️ جاري بناء هيكلية Android Native...")

# هيكلية المجلدات
dirs_to_create = [
    "app/src/main/java/org/alituama/mytube",
    "app/src/main/res/layout",
    "app/src/main/res/values",
    "app/src/main/res/drawable",
    "app/src/main/res/xml",
    "gradle/wrapper"
]

for d in dirs_to_create:
    os.makedirs(d, exist_ok=True)

# محتوى الملفات
files_content = {
    # ------------------------------------
    # ملفات Gradle (نظام البناء)
    # ------------------------------------
    "build.gradle.kts": """// ملف المشروع الرئيسي
plugins {
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.20" apply false
}
""",

    "settings.gradle.kts": """
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven { url = java.net.URI("https://jitpack.io") }
    }
}
rootProject.name = "MyTube"
include(":app")
""",

    "app/build.gradle.kts": """
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "org.alituama.mytube"
    compileSdk = 34

    defaultConfig {
        applicationId = "org.alituama.mytube"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = "1.8"
    }
    buildFeatures {
        viewBinding = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    
    // مكتبة التحميل القوية (YoutubeDL-Android)
    implementation("com.github.yausername.youtubedl-android:library:0.14.0")
    implementation("com.github.yausername.youtubedl-android:ffmpeg:0.14.0") // لدعم الدمج و 4K
    
    // للمعالجة في الخلفية
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
}
""",

    # ------------------------------------
    # Android Manifest (الإعدادات والصلاحيات)
    # ------------------------------------
    "app/src/main/AndroidManifest.xml": """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@android:drawable/ic_menu_save"
        android:label="MyTube"
        android:supportsRtl="true"
        android:theme="@style/Theme.MyTube.Dialog"
        tools:targetApi="31">

        <!-- النشاط الرئيسي (نافذة عائمة + يقبل المشاركة) -->
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.MyTube.Dialog">
            
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>

            <!-- هنا السر: استقبال الروابط من يوتيوب -->
            <intent-filter>
                <action android:name="android.intent.action.SEND" />
                <category android:name="android.intent.category.DEFAULT" />
                <data android:mimeType="text/plain" />
            </intent-filter>
        </activity>
    </application>
</manifest>
""",

    # ------------------------------------
    # التصميم (Themes & Colors)
    # ------------------------------------
    "app/src/main/res/values/themes.xml": """<resources xmlns:tools="http://schemas.android.com/tools">
    <!-- الثيم الشفاف (النافذة العائمة) -->
    <style name="Theme.MyTube.Dialog" parent="Theme.Material3.DayNight.Dialog">
        <item name="android:windowBackground">@android:color/transparent</item>
        <item name="android:windowIsTranslucent">true</item>
        <item name="android:backgroundDimEnabled">true</item>
        <!-- جعل النافذة تأخذ عرض الشاشة تقريباً -->
        <item name="android:windowMinWidthMajor">90%</item>
        <item name="android:windowMinWidthMinor">90%</item>
        <item name="colorPrimary">#FF0000</item>
        <item name="colorOnPrimary">#FFFFFF</item>
    </style>
</resources>
""",

    "app/src/main/res/values/colors.xml": """<resources>
    <color name="black">#FF000000</color>
    <color name="white">#FFFFFFFF</color>
    <color name="youtube_red">#FF0000</color>
    <color name="card_bg">#1F1F1F</color>
</resources>
""",

    # ------------------------------------
    # واجهة المستخدم (Layout)
    # ------------------------------------
    "app/src/main/res/layout/activity_main.xml": """<?xml version="1.0" encoding="utf-8"?>
<androidx.cardview.widget.CardView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:cardCornerRadius="24dp"
    app:cardBackgroundColor="#1F1F1F"
    app:cardElevation="8dp">

    <androidx.constraintlayout.widget.ConstraintLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:padding="20dp">

        <!-- العنوان -->
        <TextView
            android:id="@+id/tvTitle"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="MyTube Downloader"
            android:textColor="#FFFFFF"
            android:textSize="22sp"
            android:textStyle="bold"
            app:layout_constraintStart_toStartOf="parent"
            app:layout_constraintTop_toTopOf="parent" />

        <!-- حقل النص مع زر اللصق -->
        <com.google.android.material.textfield.TextInputLayout
            android:id="@+id/inputLayout"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_marginTop="16dp"
            android:hint="YouTube Link"
            android:textColorHint="#AAAAAA"
            style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
            app:boxStrokeColor="#FF0000"
            app:hintTextColor="#FF0000"
            app:endIconMode="clear_text"
            app:startIconDrawable="@android:drawable/ic_menu_paste_holo_light"
            app:layout_constraintEnd_toEndOf="parent"
            app:layout_constraintStart_toStartOf="parent"
            app:layout_constraintTop_toBottomOf="@id/tvTitle">

            <com.google.android.material.textfield.TextInputEditText
                android:id="@+id/etUrl"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:textColor="#FFFFFF"
                android:inputType="textUri" />
        </com.google.android.material.textfield.TextInputLayout>

        <!-- زر البحث -->
        <Button
            android:id="@+id/btnFetch"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="10dp"
            android:text="Fetch Formats"
            android:textColor="#FFFFFF"
            android:textStyle="bold"
            android:backgroundTint="#FF0000"
            app:layout_constraintTop_toBottomOf="@id/inputLayout" />

        <!-- حالة التحميل -->
        <TextView
            android:id="@+id/tvStatus"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="15dp"
            android:text="Ready to download"
            android:textColor="#AAAAAA"
            android:textSize="14sp"
            app:layout_constraintStart_toStartOf="parent"
            app:layout_constraintTop_toBottomOf="@id/btnFetch" />

        <!-- الحقوق المتحركة -->
        <TextView
            android:id="@+id/tvCredits"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="25dp"
            android:text="By Ali Tuama"
            android:textSize="14sp"
            android:textStyle="bold"
            app:layout_constraintBottom_toBottomOf="parent"
            app:layout_constraintEnd_toEndOf="parent"
            app:layout_constraintStart_toStartOf="parent"
            app:layout_constraintTop_toBottomOf="@id/tvStatus" />

    </androidx.constraintlayout.widget.ConstraintLayout>
</androidx.cardview.widget.CardView>
""",

    # ------------------------------------
    # كود Kotlin (المنطق والبرمجة)
    # ------------------------------------
    "app/src/main/java/org/alituama/mytube/MainActivity.kt": """package org.alituama.mytube

import android.animation.ArgbEvaluator
import android.animation.ObjectAnimator
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.os.Environment
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.google.android.material.textfield.TextInputEditText
import com.yausername.youtubedl_android.YoutubeDL
import com.yausername.youtubedl_android.YoutubeDLRequest
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // 1. تهيئة مكتبة التحميل
        try {
            YoutubeDL.getInstance().init(application)
        } catch (e: Exception) {
            Toast.makeText(this, "Error initializing libs", Toast.LENGTH_LONG).show()
        }

        val etUrl = findViewById<TextInputEditText>(R.id.etUrl)
        val btnFetch = findViewById<Button>(R.id.btnFetch)
        val tvStatus = findViewById<TextView>(R.id.tvStatus)
        val tvCredits = findViewById<TextView>(R.id.tvCredits)

        // 2. تشغيل انيميشن الحقوق
        animateCredits(tvCredits)

        // 3. التعامل مع المشاركة (Share Intent)
        // عند مشاركة رابط من يوتيوب، سيتم وضعه هنا تلقائياً
        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            val sharedText = intent.getStringExtra(Intent.EXTRA_TEXT)
            if (sharedText != null) {
                etUrl.setText(sharedText)
                startDownload(sharedText, tvStatus) // بدء تلقائي
            }
        }

        // 4. زر البحث واللصق
        btnFetch.setOnClickListener {
            val url = etUrl.text.toString()
            if (url.isNotEmpty()) {
                startDownload(url, tvStatus)
            } else {
                // لصق تلقائي إذا كان الحقل فارغاً
                val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                val clipData = clipboard.primaryClip
                if (clipData != null && clipData.itemCount > 0) {
                    val pasteText = clipData.getItemAt(0).text.toString()
                    etUrl.setText(pasteText)
                    startDownload(pasteText, tvStatus)
                }
            }
        }
    }

    private fun startDownload(url: String, statusView: TextView) {
        statusView.text = "Initializing download..."
        
        // المسار: /storage/emulated/0/Download/MyTube
        val downloadDir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "MyTube")
        if (!downloadDir.exists()) downloadDir.mkdirs()

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // إعدادات التحميل: أفضل فيديو + أفضل صوت
                val request = YoutubeDLRequest(url)
                request.addOption("-o", downloadDir.absolutePath + "/%(title)s.%(ext)s")
                request.addOption("-f", "bestvideo+bestaudio/best") 
                
                withContext(Dispatchers.Main) {
                    statusView.text = "Downloading... (Check notifications)"
                }

                // بدء التحميل
                YoutubeDL.getInstance().execute(request) { progress, eta ->
                    runOnUiThread {
                        statusView.text = "Progress: $progress% (ETA: $eta s)"
                    }
                }

                withContext(Dispatchers.Main) {
                    statusView.text = "✅ Download Complete!"
                    Toast.makeText(this@MainActivity, "Saved to MyTube folder", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    statusView.text = "❌ Error: ${e.message}"
                }
            }
        }
    }

    private fun animateCredits(view: TextView) {
        val colorAnim = ObjectAnimator.ofInt(view, "textColor",
            Color.RED, Color.YELLOW, Color.WHITE, Color.RED)
        colorAnim.setDuration(3000)
        colorAnim.setEvaluator(ArgbEvaluator())
        colorAnim.repeatCount = ObjectAnimator.INFINITE
        colorAnim.repeatMode = ObjectAnimator.RESTART
        colorAnim.start()
    }
}
""",

    # ------------------------------------
    # ملفات XML مساعدة
    # ------------------------------------
    "app/src/main/res/xml/data_extraction_rules.xml": """<?xml version="1.0" encoding="utf-8"?>
<data-extraction-rules>
    <cloud-backup><include domain="root" /><include domain="file" /></cloud-backup>
    <device-transfer><include domain="root" /><include domain="file" /></device-transfer>
</data-extraction-rules>
""",
    "app/src/main/res/xml/backup_rules.xml": """<?xml version="1.0" encoding="utf-8"?>
<full-backup-content>
    <include domain="file" path="." />
    <include domain="root" path="." />
</full-backup-content>
""",
    
    # تحديد نسخة Gradle لضمان عمل GitHub Actions
    "gradle/wrapper/gradle-wrapper.properties": """distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-8.2-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
"""
}

# 3. كتابة الملفات
print("📝 جاري كتابة ملفات الكود...")
for path, content in files_content.items():
    with open(path, "w") as f:
        f.write(content.strip())
    print(f"✅ تم إنشاء: {path}")

print("\n🎉 تم تحويل المشروع بنجاح!")
print("الآن، ارفع التغييرات إلى GitHub ليقوم ببناء الـ APK:")
print("1. git add .")
print("2. git commit -m 'Initial Native Android Commit'")
print("3. git push")
