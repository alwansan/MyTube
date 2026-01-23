import subprocess

try:
    # تأكد أن الريبو مربوط
    subprocess.run(
        ["git", "remote", "add", "origin", "https://github.com/alwansan/MyTube.git"],
        check=False
    )

    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Update: MyTube engine"], check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], check=True)

    print("✅ Project uploaded to GitHub successfully.")

except Exception as e:
    print("❌ Git error:", e)
