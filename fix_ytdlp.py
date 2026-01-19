import os
import re

NEW_VERSION = "0.17.2"
changed = []

def patch_file(path):
    global changed
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()

    original = data

    # old styles
    data = re.sub(
        r"com\.github\.yausername:?youtubedl-android[:\w\-]*:[0-9.]+",
        f"com.github.yausername.youtubedl-android:library:{NEW_VERSION}",
        data
    )

    if data != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(data)
        changed.append(path)

for root, _, files in os.walk("."):
    for file in files:
        if file.endswith(".gradle"):
            patch_file(os.path.join(root, file))

if changed:
    print("✅ تم تحديث youtubedl-android بنجاح")
    for f in changed:
        print(" -", f)
else:
    print("❌ لم يتم العثور على youtubedl-android داخل المشروع")
