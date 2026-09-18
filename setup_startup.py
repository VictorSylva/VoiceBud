"""Configure VoiceBud to launch automatically at Windows login (silent background mode).

Usage:
  python setup_startup.py           # Add to Windows Startup
  python setup_startup.py --remove  # Remove from Windows Startup
"""
import os
import subprocess
import sys
import tempfile


def get_startup_paths():
    startup_dir = os.path.join(
        os.environ["APPDATA"],
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
        "Startup",
    )
    shortcut_path = os.path.join(startup_dir, "VoiceBud.lnk")
    project_dir = os.path.abspath(os.path.dirname(__file__))
    pythonw = os.path.join(project_dir, ".venv", "Scripts", "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = os.path.join(project_dir, ".venv", "Scripts", "python.exe")
    main_py = os.path.join(project_dir, "main.py")
    return startup_dir, shortcut_path, project_dir, pythonw, main_py


def install_startup():
    startup_dir, shortcut_path, project_dir, pythonw, main_py = get_startup_paths()
    print(f"Creating Windows startup shortcut at:\n  {shortcut_path}")
    print(f"Target:\n  {pythonw} {main_py}")
    print(f"Working Directory:\n  {project_dir}")

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
        print("\nSUCCESS: VoiceBud will now start automatically whenever you log into Windows!")
        print("It will run silently in the system tray (near the clock).")
    finally:
        if temp_vbs and os.path.exists(temp_vbs):
            os.remove(temp_vbs)


def remove_startup():
    _, shortcut_path, _, _, _ = get_startup_paths()
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)
        print(f"SUCCESS: Removed VoiceBud shortcut from Windows Startup ({shortcut_path}).")
    else:
        print("VoiceBud was not found in Windows Startup.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--remove", "-r", "uninstall"):
        remove_startup()
    else:
        install_startup()
