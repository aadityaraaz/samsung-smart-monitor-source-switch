Option Explicit
Dim shell, files, target, q
Set shell = CreateObject("WScript.Shell")
Set files = CreateObject("Scripting.FileSystemObject")
target = files.BuildPath(files.GetParentFolderName(WScript.ScriptFullName), files.GetBaseName(WScript.ScriptFullName) & ".cmd")
q = Chr(34)
shell.Run "cmd.exe /d /s /c " & q & q & target & q & " <nul" & q, 0, False
