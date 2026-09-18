Set WshShell = CreateObject("WScript.Shell")
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptDir
pythonwPath = scriptDir & "\.venv\Scripts\pythonw.exe"
mainPyPath = scriptDir & "\main.py"
WshShell.Run Chr(34) & pythonwPath & Chr(34) & " " & Chr(34) & mainPyPath & Chr(34), 0, False
