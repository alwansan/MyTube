import os
import urllib.request
import subprocess

# روابط ملفات Gradle Wrapper الرسمية
GRADLE_WRAPPER_URLS = {
    "gradlew": "https://raw.githubusercontent.com/gradle/gradle/v8.5.0/gradlew",
    "gradlew.bat": "https://raw.githubusercontent.com/gradle/gradle/v8.5.0/gradlew.bat",
    "gradle/wrapper/gradle-wrapper.jar": "https://github.com/gradle/gradle/raw/v8.5.0/gradle/wrapper/gradle-wrapper.jar"
}

def download_gradle_wrapper():
    print("🔄 Downloading missing Gradle Wrapper files...")
    
    # التأكد من وجود مجلد wrapper
    if not os.path.exists("gradle/wrapper"):
        os.makedirs("gradle/wrapper")

    for file_path, url in GRADLE_WRAPPER_URLS.items():
        try:
            print(f"   Downloading {file_path}...")
            urllib.request.urlretrieve(url, file_path)
            if file_path.endswith("gradlew"):
                os.chmod(file_path, 0o755) # إعطاء صلاحية التنفيذ
        except Exception as e:
            print(f"❌ Failed to download {file_path}: {e}")

def fix_app_build_gradle():
    print("🔧 Fixing app/build.gradle.kts (Adding Namespace)...")
    file_path = "app/build.gradle.kts"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    with open(file_path, "r") as f:
        content = f.read()

    # التحقق من وجود namespace، إذا لم يكن موجوداً يتم إضافته
    # هذا ضروري جداً في نسخ Gradle الحديثة لتجنب خطأ processDebugResources
    if 'namespace =' not in content and 'namespace ="' not in content:
        # البحث عن بداية بلوك android {
        if "android {" in content:
            # إضافة namespace org.alituama.mytube
            new_content = content.replace("android {", 'android {\n    namespace = "org.alituama.mytube"', 1)
            
            # تحديث compileSdk ليكون متوافقاً مع المكتبات الحديثة
            if "compileSdk = 33" in new_content:
                new_content = new_content.replace("compileSdk = 33", "compileSdk = 34")
            
            with open(file_path, "w") as f:
                f.write(new_content)
            print("✅ Namespace added and SDK updated.")
        else:
            print("⚠️ Could not find 'android {' block.")
    else:
        print("✅ Namespace already exists.")

def fix_android_manifest():
    print("🔧 Checking AndroidManifest.xml...")
    file_path = "app/src/main/AndroidManifest.xml"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    with open(file_path, "r") as f:
        content = f.read()
    
    # في النسخ الحديثة، الـ package في المانيفيست يجب أن يبقى ولكن الـ namespace في الغرادل هو الأهم
    # سنقوم فقط بالتأكد من صحة الملف بشكل عام
    print("✅ AndroidManifest check skipped (Focusing on build.gradle).")

def git_push_changes():
    print("🚀 Pushing fixes to GitHub...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Fix: Add Gradle Wrapper and fix namespace for build"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! Check GitHub Actions now.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")

if __name__ == "__main__":
    download_gradle_wrapper()
    fix_app_build_gradle()
    fix_android_manifest()
    git_push_changes()
