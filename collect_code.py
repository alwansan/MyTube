import os

# الامتدادات التي نريد قراءتها (أكواد التطبيق)
ALLOWED_EXTENSIONS = {
    '.kt', '.java',             # كود الأندرويد
    '.xml',                     # الواجهات والإعدادات
    '.kts', '.gradle',          # ملفات Gradle
    '.properties',              # إعدادات المشروع
    '.py',                      # سكربتات بايثون الخاصة بك
    '.json', '.txt', '.md'      # ملفات نصية أخرى
}

# المجلدات التي سيتم تجاهلها (لتقليل حجم الملف وعدم نسخ ملفات النظام)
IGNORED_DIRS = {
    '.git', '.gradle', '.idea', 'build', 'gradle', 
    'captures', 'cxx', 'output'
}

OUTPUT_FILE = "full_project_code.txt"

def is_text_file(filename):
    return any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS)

def collect_project_code():
    project_root = os.getcwd() # المجلد الحالي
    
    print(f"🔄 Scanning project in: {project_root}")
    print(f"📄 Writing code to: {OUTPUT_FILE}...\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        # كتابة رأس الملف
        outfile.write(f"=== PROJECT DUMP: {os.path.basename(project_root)} ===\n\n")

        for root, dirs, files in os.walk(project_root):
            # إزالة المجلدات غير المرغوب فيها من البحث
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

            for file in files:
                if is_text_file(file):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, project_root)
                    
                    # لا تقرأ ملف المخرجات نفسه أو ملفات السكربت هذا
                    if file == OUTPUT_FILE or file == "collect_code.py":
                        continue

                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as infile:
                            content = infile.read()
                            
                            # تنسيق الفاصل بين الملفات
                            outfile.write("="*50 + "\n")
                            outfile.write(f"FILE: {relative_path}\n")
                            outfile.write("="*50 + "\n")
                            outfile.write(content + "\n\n")
                            print(f"✅ Added: {relative_path}")
                    except Exception as e:
                        print(f"❌ Error reading {relative_path}: {e}")

    print(f"\n🎉 Done! All code is saved in '{OUTPUT_FILE}'")

if __name__ == "__main__":
    collect_project_code()
