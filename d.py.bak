import os
import subprocess

# تصحيح ملف settings.gradle.kts
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
        maven { url 'https://jitpack.io' }
    }
}
rootProject.name = "MyTube"
include ':app'
"""

# كتابة الملف
with open("settings.gradle.kts", "w", encoding="utf-8") as f:
    f.write(settings_gradle_content)

print("✅ تم تصحيح ملف settings.gradle.kts")

# Git operations
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Fix: Correct settings.gradle.kts syntax"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ تم الرفع إلى GitHub")
except subprocess.CalledProcessError as e:
    print(f"❌ خطأ في Git: {e}")