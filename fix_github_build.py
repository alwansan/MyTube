import os
import re
import subprocess

# مجلد المشروع
project_dir = os.path.dirname(os.path.realpath(__file__))

# 1️⃣ إضافة mavenCentral لكل build.gradle.kts
for gradle_file in ["build.gradle.kts", "app/build.gradle.kts"]:
    path = os.path.join(project_dir, gradle_file)
    if os.path.exists(path):
        with open(path, "r") as f:
            content = f.read()
        if "mavenCentral()" not in content:
            content = re.sub(r"repositories\s*{", "repositories {\n    mavenCentral()", content)
            with open(path, "w") as f:
                f.write(content)
            print(f"✅ Added mavenCentral() in {gradle_file}")

# 2️⃣ استبدال youtubedl-android القديم بإصدار حديث موجود
app_build_file = os.path.join(project_dir, "app/build.gradle.kts")
if os.path.exists(app_build_file):
    with open(app_build_file, "r") as f:
        content = f.read()
    new_content = re.sub(
        r'implementation\(".*youtubedl-android.*"\)',
        'implementation("io.github.junkfood02.youtubedl-android:library:0.17.2")',
        content
    )
    with open(app_build_file, "w") as f:
        f.write(new_content)
    print("✅ Updated youtubedl-android dependency to 0.17.2")

# 3️⃣ تفعيل AndroidX في gradle.properties
gradle_props = os.path.join(project_dir, "gradle.properties")
with open(gradle_props, "a") as f:
    f.write("\nandroid.useAndroidX=true\nandroid.enableJetifier=true\n")
print("✅ Enabled AndroidX and Jetifier in gradle.properties")

# 4️⃣ تنظيف المشروع قبل البناء
print("🔄 Cleaning project...")
subprocess.run(["./gradlew", "clean"], cwd=project_dir)

# 5️⃣ محاولة بناء APK Debug
print("🏗️ Building APK Debug...")
subprocess.run(["./gradlew", "assembleDebug", "--stacktrace"], cwd=project_dir)
