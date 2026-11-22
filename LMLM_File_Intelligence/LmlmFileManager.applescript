(*
  LMLM File Intelligence — macOS AppleScript launcher
  Select the companion LmlmFileManager.py when prompted.
  The Python engine handles local folders and Git repositories.
*)

on run
    set helperFile to choose file with prompt "Select LmlmFileManager.py"
    set helperPOSIX to POSIX path of helperFile

    set targetFolder to choose folder with prompt "Choose a local folder or a Git repository to study"
    set targetPOSIX to POSIX path of targetFolder

    set modeChoice to choose from list {"Study files and Git status", "Organize files safely", "Merge selected documents", "Full workflow"} ¬
        with title "LMLM File Intelligence" with prompt "Choose an operation:" default items {"Study files and Git status"}
    if modeChoice is false then return

    set selectedMode to item 1 of modeChoice
    if selectedMode is "Study files and Git status" then
        set modeArg to "study"
    else if selectedMode is "Organize files safely" then
        set modeArg to "organize"
    else if selectedMode is "Merge selected documents" then
        set modeArg to "merge"
    else
        set modeArg to "full"
    end if

    set commandText to "/usr/bin/env python3 " & quoted form of helperPOSIX & " --root " & quoted form of targetPOSIX & " --mode " & modeArg

    if modeArg is "organize" or modeArg is "full" then
        set isRepo to false
        try
            do shell script "/usr/bin/env git -C " & quoted form of targetPOSIX & " rev-parse --show-toplevel"
            set isRepo to true
        end try
        if not isRepo then
            set answer to button returned of (display dialog "This is a local folder. Physical organization moves direct child files into category folders. Continue?" buttons {"Cancel", "Continue"} default button "Cancel" with title "LMLM")
            if answer is "Continue" then
                set commandText to commandText & " --confirm-local-moves"
            else
                display dialog "No files were moved. Choose Study or Merge if you only want read-only inspection or document merging." buttons {"OK"} default button "OK"
                return
            end if
        else
            display dialog "Repository detected. LMLM will create a classification plan only; it will not move source files or change Git history." buttons {"Continue"} default button "Continue" with title "Repository safety"
        end if
    end if

    try
        set resultText to do shell script commandText
        set dialogResult to display dialog resultText buttons {"Open Reports Folder", "OK"} default button "OK" with title "LMLM File Intelligence"
        if button returned of dialogResult is "Open Reports Folder" then
            do shell script "/usr/bin/open " & quoted form of ((POSIX path of (path to documents folder)) & "LMLM-FileIntelligence/")
        end if
    on error errorText number errorNumber
        display alert "LMLM File Intelligence stopped" message (errorText & " (" & errorNumber & ")") as critical
    end try
end run
