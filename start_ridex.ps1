# ============================================================
# RideX - Stop All Services
# Windows PowerShell
# ============================================================

$ErrorActionPreference = "SilentlyContinue"

# ============================================================
# CONFIGURATION
# ============================================================

$RIDEX_DIR = "C:\Users\rangaraju\Desktop\AI2026 Tools\RideX"
$PID_DIR = Join-Path $RIDEX_DIR "pids"

$Ports = @(
    8000,
    8001,
    8002,
    8003,
    8004,
    8005,
    8006,
    8007,
    8008
)

# ============================================================
# HEADER
# ============================================================

Write-Host ""
Write-Host "============================================================"
Write-Host "                 RideX Stopping"
Write-Host "============================================================"
Write-Host ""
Write-Host "Project : $RIDEX_DIR"
Write-Host "PID Dir : $PID_DIR"
Write-Host ""

# ============================================================
# CHECK PROJECT DIRECTORY
# ============================================================

if (-not (Test-Path $RIDEX_DIR)) {
    Write-Host "ERROR: RideX directory not found:"
    Write-Host $RIDEX_DIR
    exit 1
}

# ============================================================
# STEP 1 - STOP SERVICES USING PID FILES
# ============================================================

Write-Host "------------------------------------------------------------"
Write-Host "Stopping services using PID files..."
Write-Host "------------------------------------------------------------"
Write-Host ""

if (Test-Path $PID_DIR) {

    $PidFiles = Get-ChildItem `
        -Path $PID_DIR `
        -Filter "*.pid" `
        -File `
        -ErrorAction SilentlyContinue

    if ($PidFiles.Count -eq 0) {

        Write-Host "No PID files found."

    }
    else {

        foreach ($PidFile in $PidFiles) {

            $ServiceName = $PidFile.BaseName
            $PIDText = Get-Content $PidFile.FullName -ErrorAction SilentlyContinue

            if ([string]::IsNullOrWhiteSpace($PIDText)) {

                Write-Host "$ServiceName : Empty PID file"
                Remove-Item $PidFile.FullName -Force
                continue
            }

            $PID = 0

            if (-not [int]::TryParse($PIDText.Trim(), [ref]$PID)) {

                Write-Host "$ServiceName : Invalid PID $PIDText"
                Remove-Item $PidFile.FullName -Force
                continue
            }

            Write-Host "Stopping $ServiceName (PID $PID)..."

            $Process = Get-Process `
                -Id $PID `
                -ErrorAction SilentlyContinue

            if ($null -ne $Process) {

                # ------------------------------------------------
                # Graceful stop
                # ------------------------------------------------

                Stop-Process `
                    -Id $PID `
                    -ErrorAction SilentlyContinue

                Start-Sleep -Seconds 2

                # ------------------------------------------------
                # Check whether process stopped
                # ------------------------------------------------

                $Process = Get-Process `
                    -Id $PID `
                    -ErrorAction SilentlyContinue

                if ($null -ne $Process) {

                    Write-Host "  Process still running."
                    Write-Host "  Force stopping PID $PID..."

                    Stop-Process `
                        -Id $PID `
                        -Force `
                        -ErrorAction SilentlyContinue

                    Start-Sleep -Seconds 1
                }

                # ------------------------------------------------
                # Final verification
                # ------------------------------------------------

                $Process = Get-Process `
                    -Id $PID `
                    -ErrorAction SilentlyContinue

                if ($null -eq $Process) {
                    Write-Host "  $ServiceName stopped."
                }
                else {
                    Write-Host "  WARNING: Could not stop $ServiceName."
                }

            }
            else {

                Write-Host "  $ServiceName was not running."
            }

            # ----------------------------------------------------
            # Remove PID file
            # ----------------------------------------------------

            Remove-Item `
                $PidFile.FullName `
                -Force `
                -ErrorAction SilentlyContinue
        }
    }
}
else {

    Write-Host "PID directory not found:"
    Write-Host $PID_DIR
}

# ============================================================
# STEP 2 - FIND REMAINING RIDEX UVICORN PROCESSES
# ============================================================

Write-Host ""
Write-Host "------------------------------------------------------------"
Write-Host "Checking for remaining RideX Uvicorn processes..."
Write-Host "------------------------------------------------------------"
Write-Host ""

$RemainingProcesses = Get-CimInstance Win32_Process |
Where-Object {
    $_.Name -match "^python(\.exe)?$" -and
    $_.CommandLine -match "uvicorn" -and
    $_.CommandLine -match "AI2026 Tools\\RideX"
}

if ($null -eq $RemainingProcesses) {

    Write-Host "No remaining RideX Uvicorn processes found."

}
else {

    foreach ($ProcessInfo in $RemainingProcesses) {

        $RemainingPID = $ProcessInfo.ProcessId

        Write-Host "Stopping remaining RideX process:"
        Write-Host "  PID: $RemainingPID"

        Stop-Process `
            -Id $RemainingPID `
            -Force `
            -ErrorAction SilentlyContinue
    }
}

# ============================================================
# STEP 3 - CHECK RIDE X PORTS
# ============================================================

Write-Host ""
Write-Host "------------------------------------------------------------"
Write-Host "Checking RideX ports..."
Write-Host "------------------------------------------------------------"
Write-Host ""

$AnyPortInUse = $false

foreach ($Port in $Ports) {

    $Connection = Get-NetTCPConnection `
        -LocalPort $Port `
        -State Listen `
        -ErrorAction SilentlyContinue

    if ($null -eq $Connection) {

        Write-Host "Port $Port : FREE"

    }
    else {

        $AnyPortInUse = $true

        $PIDs = $Connection |
        Select-Object -ExpandProperty OwningProcess -Unique

        Write-Host "Port $Port : STILL IN USE"
        Write-Host "  PID(s): $($PIDs -join ', ')"
    }
}

# ============================================================
# STEP 4 - FINAL STATUS
# ============================================================

Write-Host ""
Write-Host "============================================================"

if ($AnyPortInUse) {

    Write-Host "WARNING: Some RideX ports are still in use."

}
else {

    Write-Host "              RideX stopped successfully"

}

Write-Host "============================================================"
Write-Host ""

# ============================================================
# INFORMATION
# ============================================================

Write-Host "RideX project:"
Write-Host $RIDEX_DIR

Write-Host ""
Write-Host "Ports checked:"
Write-Host "8000  API Gateway"
Write-Host "8001  User Service"
Write-Host "8002  Driver Service"
Write-Host "8003  Ride Service"
Write-Host "8004  Matching Service"
Write-Host "8005  Pricing Service"
Write-Host "8006  Payment Service"
Write-Host "8007  Notification Service"
Write-Host "8008  Rating/Safety Service"

Write-Host ""
