' Ssuljaengi Silent Launcher (No Windows Version)
' This VBScript runs the batch launcher with NO visible windows at all

Set WshShell = CreateObject("WScript.Shell")

' Get the directory where this script is located
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Run the batch file completely hidden
WshShell.Run Chr(34) & scriptDir & "\START_APP_SILENT.bat" & Chr(34), 0, False

' Show a notification balloon (Windows 10+)
Set objNotify = CreateObject("WScript.Shell")
objNotify.Popup "Ssuljaengi is starting..." & vbCrLf & vbCrLf & "The app will open in your browser shortly." & vbCrLf & vbCrLf & "No terminal windows will be shown.", 10, "Ssuljaengi Launcher", 64

' Clean up
Set WshShell = Nothing
Set objNotify = Nothing
