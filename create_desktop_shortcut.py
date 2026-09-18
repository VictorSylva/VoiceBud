"""Create a Desktop shortcut for VoiceBud that runs silently in the background.

Usage:
  .\\.venv\\Scripts\\python.exe create_desktop_shortcut.py
"""
import os
import subprocess
import tempfile


def create_desktop_shortcut():
    # User's Desktop folder
    desktop_dir = os.path.join(os.environ["USERPROFILE"], "Desktop")
    shortcut_path = os.path.join(desktop_dir, "VoiceBud.lnk")
    project_dir = os.path.abspath(os.path.dirname(__file__))
    pythonw = os.path.join(project_dir, ".venv", "Scripts", "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = os.path.join(project_dir, ".venv", "Scripts", "python.exe")
    main_py = os.path.join(project_dir, "main.py")

    print(f"Creating Desktop shortcut at:\n  {shortcut_path}")
    print(f"Target: {pythonw} \"{main_py}\"")
    print(f"Working Directory: {project_dir}")

    # Build clean VBS script to generate the .lnk file
    lines = [
        'Set ws = CreateObject("WScript.Shell")',
        f'Set s = ws.CreateShortcut("{shortcut_path}")',
        f's.TargetPath = "{pythonw}"',
        f's.Arguments = Chr(34) & "{main_py}" & Chr(34)',
        f's.WorkingDirectory = "{project_dir}"',
        's.Description = "VoiceBud - Offline Dictation"',
        's.Save',
    ]
    vbs_content = "\r\n".join(lines) + "\r\n"

    temp_vbs = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".vbs", delete=False, mode="w", encoding="utf-8") as f:
            f.write(vbs_content)
            temp_vbs = f.name

        subprocess.run(["cscript.exe", "//Nologo", temp_vbs], check=True)
        print("\nSUCCESS: VoiceBud Desktop shortcut created!")
        print("You can now double-click 'VoiceBud' on your Desktop to run it silently in the system tray.")
    finally:
        if temp_vbs and os.path.exists(temp_vbs):
            os.remove(temp_vbs)


if __name__ == "__main__":
    create_desktop_shortcut()
