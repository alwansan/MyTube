import os
import subprocess

# تصحيح ملف build.gradle.kts ليدعم Kotlin DSL بشكل صحيح
build_gradle_content = """plugins {
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
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("com.github.yausername.youtubedl-android:library:0.16.1")
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
}
"""

# كتابة الملف
with open("build.gradle.kts", "w", encoding="utf-8") as f:
    f.write(build_gradle_content)

print("✅ تم تصحيح ملف build.gradle.kts")

# Git operations
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Fix: Correct build.gradle.kts Kotlin DSL syntax"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ تم الرفع إلى GitHub")
except subprocess.CalledProcessError as e:
    print(f"❌ خطأ في Git: {e}")