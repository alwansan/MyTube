import os
import subprocess

# تصحيح ملف settings.gradle.kts ليدعم Kotlin DSL بشكل صحيح
settings_gradle_content = """pluginManagement {
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
        maven {
            url = uri("https://jitpack.io")
        }
    }
}
rootProject.name = "MyTube"
include(":app")
"""

# كتابة الملف
with open("settings.gradle.kts", "w", encoding="utf-8") as f:
    f.write(settings_gradle_content)

print("✅ تم تصحيح ملف settings.gradle.kts")

# Git operations
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Fix: Correct settings.gradle.kts Kotlin DSL syntax"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ تم الرفع إلى GitHub")
except subprocess.CalledProcessError as e:
    print(f"❌ خطأ في Git: {e}")