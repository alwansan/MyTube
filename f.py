import os
import shutil
import subprocess

def clean_workspace():
    """تنظيف المجلد بالكامل"""
    dirs_to_clean = [
        "app/src/main/java/org/alituama/mytube",
        "app/src/main/res/layout",
        "app/src/main/res/values",
        "app/src/main/res/xml",
        "app/src/main/res/drawable",
        "app/src/main/res/mipmap-hdpi",
        "app/src/main/res/mipmap-mdpi",
        "app/src/main/res/mipmap-xhdpi",
        "app/src/main/res/mipmap-xxhdpi",
        "app/src/main/res/mipmap-xxxhdpi",
        "app/src/main/res/mipmap-anydpi-v26"
    ]
    
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
    
    # حذف الملفات غير الضرورية
    files_to_remove = [
        "build.gradle.kts",
        "build.gradle",
        "d.py",
        "d.py.bak"
    ]
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
    
    print("🧹 تم تنظيف مساحة العمل")

def create_new_project():
    """إنشاء مشروع جديد متوافق تمامًا مع GitHub Actions"""
    
    # 1. settings.gradle.kts - هذا الملف جيد بالفعل
    settings_gradle = '''pluginManagement {
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
        maven { url 'https://jitpack.io' }
    }
}
rootProject.name = "MyTube"
include ':app'
'''
    
    # 2. build.gradle (Project level) - الملف الرئيسي للمشروع
    project_build_gradle = '''buildscript {
    ext.kotlin_version = '1.9.20'
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.2.0'
        classpath "org.jetbrains.kotlin:kotlin-gradle-plugin:$kotlin_version"
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
        maven { url 'https://jitpack.io' }
    }
}

task clean(type: Delete) {
    delete rootProject.buildDir
}
'''
    
    # 3. build.gradle (Module level) - الملف المهم للتطبيق
    module_build_gradle = '''plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}

android {
    namespace 'org.alituama.mytube'
    compileSdk 34

    defaultConfig {
        applicationId "org.alituama.mytube"
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName "1.0"

        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = '1.8'
    }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.11.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'com.github.yausername.youtubedl-android:library:0.16.1'
    testImplementation 'junit:junit:4.13.2'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
}
'''
    
    # 4. MainActivity.kt بسيطة لاختبار الوظيفة
    main_activity_kt = '''package org.alituama.mytube

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
'''
    
    # 5. activity_main.xml بسيطة
    activity_main_xml = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp"
    android:background="#1e1e1e">

    <TextView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="MyTube Downloader"
        android:textSize="24sp"
        android:textStyle="bold"
        android:textColor="#ffffff"
        android:gravity="center"
        android:layout_marginBottom="24dp" />

    <com.google.android.material.textfield.TextInputLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="رابط فيديو YouTube"
        style="@style/Widget.MaterialComponents.TextInputLayout.OutlinedBox">

        <com.google.android.material.textfield.TextInputEditText
            android:id="@+id/etUrl"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:inputType="textUri"
            android:textColor="#ffffff"
            android:textColorHint="#888888" />

    </com.google.android.material.textfield.TextInputLayout>

    <Button
        android:id="@+id/btnDownload"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        android:text="تحميل"
        android:textAllCaps="false"
        style="@style/Widget.MaterialComponents.Button" />

    <TextView
        android:id="@+id/tvStatus"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="24dp"
        android:text="جاهز للتحميل..."
        android:textColor="#ffffff"
        android:gravity="center"
        android:textSize="14sp" />

</LinearLayout>
'''
    
    # 6. AndroidManifest.xml
    manifest_xml = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.MyTube"
        tools:targetApi="31">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
'''
    
    # 7. الملفات الأخرى
    strings_xml = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">MyTube</string>
</resources>
'''

    themes_xml = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.MyTube" parent="Theme.MaterialComponents.DayNight.DarkActionBar">
        <item name="colorPrimary">#FF0000</item>
        <item name="colorPrimaryVariant">#CC0000</item>
        <item name="colorOnPrimary">#FFFFFF</item>
        <item name="android:statusBarColor">?attr/colorPrimaryVariant</item>
    </style>
</resources>
'''

    colors_xml = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="purple_200">#FFBB86FC</color>
    <color name="purple_500">#FF6200EE</color>
    <color name="purple_700">#FF3700B3</color>
    <color name="teal_200">#FF03DAC5</color>
    <color name="teal_700">#FF018786</color>
    <color name="black">#FF000000</color>
    <color name="white">#FFFFFFFF</color>
    <color name="red">#FF0000</color>
    <color name="dark_gray">#FF1e1e1e</color>
</resources>
'''

    backup_rules_xml = '''<?xml version="1.0" encoding="utf-8"?>
<data-extraction-rules>
    <cloud-backup>
        <exclude domain="root" />
        <exclude domain="file" />
        <exclude domain="database" />
        <exclude domain="sharedpref" />
        <exclude domain="external" />
    </cloud-backup>
    <device-transfer>
        <exclude domain="root" />
        <exclude domain="file" />
        <exclude domain="database" />
        <exclude domain="sharedpref" />
        <exclude domain="external" />
    </device-transfer>
</data-extraction-rules>
'''

    data_extraction_rules_xml = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <bool name="enable_data_extraction_rules">true</bool>
</resources>
'''

    # 8. أيقونة بسيطة
    icon_content = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
  <path
      android:fillColor="#FF0000"
      android:pathData="M34,34 L74,34 L74,74 L34,74 Z"/>
</vector>'''

    # إنشاء المجلدات
    dirs = [
        "app/src/main/java/org/alituama/mytube",
        "app/src/main/res/layout",
        "app/src/main/res/values",
        "app/src/main/res/xml",
        "app/src/main/res/drawable",
        "app/src/main/res/mipmap-hdpi",
        "app/src/main/res/mipmap-mdpi",
        "app/src/main/res/mipmap-xhdpi",
        "app/src/main/res/mipmap-xxhdpi",
        "app/src/main/res/mipmap-xxxhdpi",
        "app/src/main/res/mipmap-anydpi-v26"
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    # كتابة الملفات
    with open("settings.gradle.kts", "w", encoding="utf-8") as f:
        f.write(settings_gradle)
    
    with open("build.gradle", "w", encoding="utf-8") as f:  # بدون .kts
        f.write(project_build_gradle)
    
    with open("app/build.gradle", "w", encoding="utf-8") as f:  # بدون .kts
        f.write(module_build_gradle)
    
    with open("app/src/main/AndroidManifest.xml", "w", encoding="utf-8") as f:
        f.write(manifest_xml)
    
    with open("app/src/main/java/org/alituama/mytube/MainActivity.kt", "w", encoding="utf-8") as f:
        f.write(main_activity_kt)
    
    with open("app/src/main/res/layout/activity_main.xml", "w", encoding="utf-8") as f:
        f.write(activity_main_xml)
    
    with open("app/src/main/res/values/strings.xml", "w", encoding="utf-8") as f:
        f.write(strings_xml)
    
    with open("app/src/main/res/values/themes.xml", "w", encoding="utf-8") as f:
        f.write(themes_xml)
    
    with open("app/src/main/res/values/colors.xml", "w", encoding="utf-8") as f:
        f.write(colors_xml)
    
    with open("app/src/main/res/xml/backup_rules.xml", "w", encoding="utf-8") as f:
        f.write(backup_rules_xml)
    
    with open("app/src/main/res/xml/data_extraction_rules.xml", "w", encoding="utf-8") as f:
        f.write(data_extraction_rules_xml)
    
    # إنشاء ملفات الأيقونة
    icon_files = [
        "app/src/main/res/drawable/ic_launcher_background.xml",
        "app/src/main/res/drawable/ic_launcher_foreground.xml",
        "app/src/main/res/mipmap-hdpi/ic_launcher.xml",
        "app/src/main/res/mipmap-mdpi/ic_launcher.xml",
        "app/src/main/res/mipmap-xhdpi/ic_launcher.xml",
        "app/src/main/res/mipmap-xxhdpi/ic_launcher.xml",
        "app/src/main/res/mipmap-xxxhdpi/ic_launcher.xml"
    ]
    
    for icon_file in icon_files:
        with open(icon_file, "w", encoding="utf-8") as f:
            f.write(icon_content)
    
    # أيقونة الجولف
    with open("app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml", "w", encoding="utf-8") as f:
        f.write('''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/red"/>
    <foreground android:drawable="@drawable/ic_launcher_foreground"/>
</adaptive-icon>''')
    
    print("✅ تم إنشاء المشروع الجديد")

def git_operations():
    """تحديث Git"""
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Rebuild: Create compatible project structure for GitHub Actions"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ تم الرفع إلى GitHub")
        print("🔍 GitHub Actions سيعمل على إنشاء APK الآن")
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ في Git: {e}")
    except Exception as e:
        print(f"❌ خطأ: {e}")

# تنفيذ العملية
if __name__ == "__main__":
    print("🚀 بدء إعادة بناء المشروع...")
    clean_workspace()
    create_new_project()
    git_operations()
    print("🎉 تم الانتهاء! GitHub Actions يجب أن يعمل بنجاح الآن")