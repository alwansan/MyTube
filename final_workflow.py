from pathlib import Path

print("🔧 Preparing Android build environment...")

# مسار المشروع
root = Path(".")

# ===============================
# 1. gradle.properties
# ===============================
gradle_props = root / "gradle.properties"

gradle_content = """\
android.useAndroidX=true
android.enableJetifier=true
org.gradle.jvmargs=-Xmx4g
kotlin.code.style=official
"""

gradle_props.write_text(gradle_content, encoding="utf-8")
print("✅ gradle.properties created")

# ===============================
# 2. local.properties (لـ CI)
# ===============================
local_props = root / "local.properties"
local_props.write_text(
    "sdk.dir=/usr/local/lib/android/sdk\n",
    encoding="utf-8"
)
print("✅ local.properties created")

# ===============================
# 3. تحقق من وجود app module
# ===============================
app_dir = root / "app"
if not app_dir.exists():
    print("❌ app/ directory not found — Android project is broken")
    exit(1)

print("✅ Android app module detected")

print("\n🚀 Project is ready for GitHub Actions APK build")
