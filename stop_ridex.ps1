# ============================================================
# RideX - Stop All Services - Windows PowerShell
# ============================================================

$ErrorActionPreference = "SilentlyContinue"

# ============================================================
# CONFIGURATION
# ============================================================

$RIDEX_DIR = "C:\Users\rangaraju\Desktop\AI2026 Tools\RideX"
$PID_DIR = Join-Path $RIDEX_DIR "pids"

Write-Host ""
Write-Host "============================================================"
Write-Host "                 RideX Stopping"
Write-Host "============================================================"
Write-Host ""

# ============================================================
# STOP USING PID FILES
# ============================================================

if (Test-Path $PID_DIR) {

    $PidFiles = Get-ChildItem `
        -Path $PID_DIR `
        -Filter "*.pid" `
        -File

    foreach ($PidFile in $PidFiles) {

        $Service = $PidFile.BaseName
        $PID = Get-Content $PidFile.FullName

        if (-not $PID) {
            Remove-Item $PidFile.FullName -Force
            continue
        }

        Write-Host "Stopping $Service (PID $PID)..."

        $Process = Get-Process `
            -Id ([int]$PID) `
            -ErrorAction SilentlyContinue

        if ($Process) {

            # Graceful stop
            Stop-Process `
                -Id ([int]$PID) `
                -ErrorAction SilentlyContinue

            Start-Sleep -Seconds 1

            # Check again
            $Process = Get-Process `
                -Id ([int]$PID) `
                -ErrorAction SilentlyContinue

            if ($Process) {

                Write-Host "Force stopping $Service..."

                Stop-Process `
                    -Id ([int]$PID) `
                    -Force `
                    -ErrorAction SilentlyContinue
            }

            Write-Host "$Service stopped."
        }
        else {

            Write-Host "$Service was not running."
        }

        Remove-Item `
            $PidFile.FullName `
            -Force `
            -ErrorAction SilentlyContinue
    }
}

# ============================================================
# FALLBACK: FIND RIDE X UVICORN PROCESSES
# ============================================================

Write-Host ""
Write-Host "Checking for remaining RideX Uvicorn processes..."

$Processes = Get-CimInstance Win32_Process |
Where-Object {
    $_.Name -match "^python(\.exe)?$" -and
    $_.CommandLine -match "uvicorn" -and
    $_.CommandLine -match "AI2026 Tools\\RideX"
}

foreach ($Process in $Processes) {

    Write-Host "Stopping remaining RideX PID $($Process.ProcessId)..."

    Stop-Process `
        -Id $Process.ProcessId `
        -Force `
        -ErrorAction SilentlyContinue
}

# ============================================================
# VERIFY PORTS
# ============================================================

Write-Host ""
Write-Host "Checking RideX ports..."

$Ports = @(8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008)

foreach ($Port in $Ports) {

    $Connection = Get-NetTCPConnection `
        -LocalPort $Port `
        -State Listen `
        -ErrorAction SilentlyContinue

    if ($Connection) {
        Write-Host "WARNING: Port $Port is still in use."
    }
    else {
        Write-Host "Port $Port is free."
    }
}

# ============================================================
# DONE
# ============================================================

Write-Host ""
Write-Host "============================================================"
Write-Host "              RideX stopped"
Write-Host "============================================================"
Write-Host ""
