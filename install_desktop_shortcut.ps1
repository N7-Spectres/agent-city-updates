param()

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$launcherPath = Join-Path $projectRoot "agent_city_launcher.pyw"
$customIconPath = Join-Path $projectRoot "static\assets\app\agent-city.ico"

if (-not (Test-Path $launcherPath)) {
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show(
        "Agent City launcher was not found at $launcherPath",
        "Agent City",
        "OK",
        "Error"
    ) | Out-Null
    exit 1
}

$pythonw = Join-Path $projectRoot ".venv\Scripts\pythonw.exe"

if (-not (Test-Path $pythonw)) {
    $pythonwCommand = Get-Command pythonw.exe -ErrorAction SilentlyContinue
    if ($pythonwCommand) {
        $pythonw = $pythonwCommand.Source
    }
}

if (-not (Test-Path $pythonw)) {
    $pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        $candidate = Join-Path (Split-Path -Parent $pythonCommand.Source) "pythonw.exe"
        if (Test-Path $candidate) {
            $pythonw = $candidate
        }
    }
}

if (-not (Test-Path $pythonw)) {
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show(
        "Agent City could not find pythonw.exe. Make sure the same Python environment you use to run Agent City is still installed.",
        "Agent City",
        "OK",
        "Error"
    ) | Out-Null
    exit 1
}

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Agent City.lnk"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $pythonw
$shortcut.Arguments = '"' + $launcherPath + '"'
$shortcut.WorkingDirectory = $projectRoot
$shortcut.Description = "Launch Agent City"
$shortcut.WindowStyle = 7

# This path is intentionally stable even before the custom icon ships.
# Assets can add the .ico later without changing the launcher/shortcut contract.
$shortcut.IconLocation = $customIconPath + ",0"
$shortcut.Save()

Add-Type -AssemblyName PresentationFramework
[System.Windows.MessageBox]::Show(
    "Agent City is ready on your desktop. Double-click the Agent City icon to start or reopen it.",
    "Agent City",
    "OK",
    "Information"
) | Out-Null
