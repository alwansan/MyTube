import os
import re

PROJECT_ROOT = "."

OLD_VERSION = "0.14.0"
NEW_VERSION = "0.17.2"

changed_files = []

def fix_gradle_file(path):
    global changed_files

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # replace old ffmpeg
    content = re.sub(
        r"com\.github\.yausername\.youtubedl-android:ffmpeg:0\.14\.0",
        f"com.github.yausername.youtubedl-android:ffmpeg:{NEW_VERSION}",
        content
    )

    # replace library if exists
    content = re.sub(
        r"com\.github\.yausername\.youtubedl-android:library:0\.14\.0",
        f"com.github.yausername.youtubedl-android:library:{NEW_VERSION}",
        content
    )

    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        changed_files.append(path)

def scan():
    for root, _, files in os.walk(PROJECT_ROOT):
        for file in files:
            if file.endswith(".gradle"):
                fix_gradle_file(os.path.join(root, file))

scan()

if changed_files:
    print("✅ تم إصلاح مكتبة ffmpeg بنجاح")
    for f in changed_files:
        print(" -", f)
else:
    print("⚠️ لم يتم العثور على ffmpeg 0.14.0")
