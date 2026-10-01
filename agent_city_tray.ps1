param(
    [Parameter(Mandatory=$true)][string]$ProjectRoot,
    [Parameter(Mandatory=$true)][string]$Pythonw,
    [Parameter(Mandatory=$true)][int]$LauncherPid
)

$ErrorActionPreference = "SilentlyContinue"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$dataDir = Join-Path $ProjectRoot "data"
$statusPath = Join-Path $dataDir "launcher_status.json"
$commandPath = Join-Path $dataDir "launcher_command.json"
$iconPath = Join-Path $ProjectRoot "static\assets\app\agent-city.ico"
$launcherPath = Join-Path $ProjectRoot "agent_city_launcher.pyw"
$runKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$runName = "Agent City"

New-Item -ItemType Directory -Force -Path $dataDir | Out-Null

function Write-LauncherCommand([string]$command) {
    $temp = $commandPath + ".tmp"
    @{
        command = $command
        requested_at = (Get-Date).ToString("o")
    } | ConvertTo-Json | Set-Content -Encoding UTF8 $temp
    Move-Item -Force $temp $commandPath
}

function Get-LauncherStatus {
    if (-not (Test-Path $statusPath)) {
        return $null
    }

    try {
        return Get-Content -Raw $statusPath | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Get-StartupEnabled {
    try {
        $props = Get-ItemProperty -Path $runKey -Name $runName -ErrorAction Stop
        return $null -ne $props.PSObject.Properties[$runName]
    } catch {
        return $false
    }
}

function Set-StartupEnabled([bool]$enabled) {
    if ($enabled) {
        $value = '"' + $Pythonw + '" "' + $launcherPath + '" --startup'
        New-Item -Path $runKey -Force | Out-Null
        New-ItemProperty -Path $runKey -Name $runName -Value $value -PropertyType String -Force | Out-Null
    } else {
        Remove-ItemProperty -Path $runKey -Name $runName -ErrorAction SilentlyContinue
    }
}

$notify = New-Object System.Windows.Forms.NotifyIcon
if (Test-Path $iconPath) {
    try {
        $notify.Icon = New-Object System.Drawing.Icon($iconPath)
    } catch {
        $notify.Icon = [System.Drawing.SystemIcons]::Application
    }
} else {
    $notify.Icon = [System.Drawing.SystemIcons]::Application
}
$notify.Text = "Agent City - Starting"
$notify.Visible = $true

$menu = New-Object System.Windows.Forms.ContextMenuStrip

$statusItem = New-Object System.Windows.Forms.ToolStripMenuItem
$statusItem.Text = "Status: Starting"
$statusItem.Enabled = $false
[void]$menu.Items.Add($statusItem)

[void]$menu.Items.Add((New-Object System.Windows.Forms.ToolStripSeparator))

$openItem = New-Object System.Windows.Forms.ToolStripMenuItem
$openItem.Text = "Open Agent City"
$openItem.Add_Click({ Write-LauncherCommand "open" })
[void]$menu.Items.Add($openItem)

$restartItem = New-Object System.Windows.Forms.ToolStripMenuItem
$restartItem.Text = "Restart Agent City"
$restartItem.Add_Click({ Write-LauncherCommand "restart" })
[void]$menu.Items.Add($restartItem)

$startupItem = New-Object System.Windows.Forms.ToolStripMenuItem
$startupItem.Text = "Start with Windows"
$startupItem.CheckOnClick = $false
$startupItem.Checked = Get-StartupEnabled
$startupItem.Add_Click({
    $next = -not (Get-StartupEnabled)
    Set-StartupEnabled $next
    $startupItem.Checked = $next
})
[void]$menu.Items.Add($startupItem)

[void]$menu.Items.Add((New-Object System.Windows.Forms.ToolStripSeparator))

$quitItem = New-Object System.Windows.Forms.ToolStripMenuItem
$quitItem.Text = "Quit Agent City"
$quitItem.Add_Click({ Write-LauncherCommand "quit" })
[void]$menu.Items.Add($quitItem)

$notify.ContextMenuStrip = $menu
$notify.Add_DoubleClick({ Write-LauncherCommand "open" })

$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 1000
$timer.Add_Tick({
    $status = Get-LauncherStatus
    if ($null -ne $status) {
        $state = [string]$status.state
        if ([string]::IsNullOrWhiteSpace($state)) {
            $state = "Unknown"
        }

        $statusItem.Text = "Status: " + $state
        $text = "Agent City - " + $state
        if ($text.Length -gt 63) {
            $text = $text.Substring(0, 63)
        }
        $notify.Text = $text
    }

    try {
        $process = Get-Process -Id $LauncherPid -ErrorAction Stop
    } catch {
        $timer.Stop()
        $notify.Visible = $false
        [System.Windows.Forms.Application]::ExitThread()
    }
})
$timer.Start()

try {
    [System.Windows.Forms.Application]::Run()
} finally {
    $timer.Stop()
    $notify.Visible = $false
    $notify.Dispose()
    $menu.Dispose()
}
