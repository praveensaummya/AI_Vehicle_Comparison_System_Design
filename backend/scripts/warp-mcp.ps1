# Warp MCP Server Management Script for Windows PowerShell
# This script manages MCP servers for the AI Vehicle Comparison System

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "status", "restart", "test")]
    [string]$Action
)

# Configuration
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$ConfigFile = Join-Path $ProjectRoot "mcp-config.json"
$LogFile = Join-Path $ProjectRoot "logs\mcp-servers.log"

# Ensure logs directory exists
$LogDir = Split-Path $LogFile -Parent
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Logging function
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    Write-Host $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage
}

# Load MCP configuration
function Get-MCPConfig {
    if (!(Test-Path $ConfigFile)) {
        Write-Log "Configuration file not found: $ConfigFile" "ERROR"
        return $null
    }
    
    try {
        $config = Get-Content $ConfigFile | ConvertFrom-Json
        Write-Log "MCP configuration loaded successfully"
        return $config
    }
    catch {
        Write-Log "Failed to load MCP configuration: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

# Start a single MCP server
function Start-MCPServer {
    param(
        [string]$ServerName,
        [object]$ServerConfig
    )
    
    Write-Log "Starting MCP server: $ServerName"
    
    try {
        # Prepare environment variables
        $env:OPENAI_API_KEY = $ServerConfig.env.OPENAI_API_KEY
        
        # Build command
        $Command = $ServerConfig.command
        $Args = $ServerConfig.args -join " "
        
        Write-Log "Executing: $Command $Args"
        
        # Start the process
        $ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
        $ProcessInfo.FileName = $Command
        $ProcessInfo.Arguments = $Args
        $ProcessInfo.UseShellExecute = $false
        $ProcessInfo.RedirectStandardOutput = $true
        $ProcessInfo.RedirectStandardError = $true
        $ProcessInfo.CreateNoWindow = $true
        
        # Set environment variables
        foreach ($envVar in $ServerConfig.env.PSObject.Properties) {
            $ProcessInfo.Environment[$envVar.Name] = $envVar.Value
        }
        
        $Process = [System.Diagnostics.Process]::Start($ProcessInfo)
        
        # Wait a bit to see if it starts successfully
        Start-Sleep -Seconds 3
        
        if (!$Process.HasExited) {
            Write-Log "MCP server started successfully: $ServerName (PID: $($Process.Id))"
            
            # Store process info in a file for tracking
            $ProcessInfo = @{
                Name = $ServerName
                PID = $Process.Id
                StartTime = Get-Date
            }
            $ProcessFile = Join-Path $ProjectRoot "logs\mcp-processes.json"
            
            # Load existing processes
            $Processes = @()
            if (Test-Path $ProcessFile) {
                $Processes = Get-Content $ProcessFile | ConvertFrom-Json
            }
            
            # Add new process
            $Processes += $ProcessInfo
            $Processes | ConvertTo-Json | Set-Content $ProcessFile
            
            return $true
        }
        else {
            $stdout = $Process.StandardOutput.ReadToEnd()
            $stderr = $Process.StandardError.ReadToEnd()
            Write-Log "MCP server failed to start: $ServerName" "ERROR"
            Write-Log "STDOUT: $stdout" "ERROR"
            Write-Log "STDERR: $stderr" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Exception starting MCP server ${ServerName}: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Stop MCP servers
function Stop-MCPServers {
    $ProcessFile = Join-Path $ProjectRoot "logs\mcp-processes.json"
    
    if (!(Test-Path $ProcessFile)) {
        Write-Log "No MCP server process file found"
        return
    }
    
    try {
        $Processes = Get-Content $ProcessFile | ConvertFrom-Json
        
        foreach ($ProcessInfo in $Processes) {
            try {
                $Process = Get-Process -Id $ProcessInfo.PID -ErrorAction SilentlyContinue
                if ($Process) {
                    Write-Log "Stopping MCP server: $($ProcessInfo.Name) (PID: $($ProcessInfo.PID))"
                    Stop-Process -Id $ProcessInfo.PID -Force
                    Write-Log "MCP server stopped: $($ProcessInfo.Name)"
                }
                else {
                    Write-Log "MCP server process not found: $($ProcessInfo.Name) (PID: $($ProcessInfo.PID))" "WARN"
                }
            }
            catch {
                Write-Log "Error stopping MCP server $($ProcessInfo.Name): $($_.Exception.Message)" "ERROR"
            }
        }
        
        # Clear the process file
        Remove-Item $ProcessFile -Force
        Write-Log "All MCP servers stopped"
    }
    catch {
        Write-Log "Error reading process file: $($_.Exception.Message)" "ERROR"
    }
}

# Get server status
function Get-MCPServerStatus {
    $ProcessFile = Join-Path $ProjectRoot "logs\mcp-processes.json"
    
    Write-Host "`n=== MCP Server Status ===" -ForegroundColor Cyan
    
    if (!(Test-Path $ProcessFile)) {
        Write-Host "  No MCP servers running" -ForegroundColor Yellow
        return
    }
    
    try {
        $Processes = Get-Content $ProcessFile | ConvertFrom-Json
        
        $RunningCount = 0
        foreach ($ProcessInfo in $Processes) {
            $Process = Get-Process -Id $ProcessInfo.PID -ErrorAction SilentlyContinue
            if ($Process) {
                Write-Host "  $($ProcessInfo.Name): RUNNING (PID: $($ProcessInfo.PID))" -ForegroundColor Green
                $RunningCount++
            }
            else {
                Write-Host "  $($ProcessInfo.Name): STOPPED" -ForegroundColor Red
            }
        }
        
        Write-Host "`nTotal servers: $($Processes.Count), Running: $RunningCount" -ForegroundColor Cyan
    }
    catch {
        Write-Log "Error reading server status: $($_.Exception.Message)" "ERROR"
    }
    
    Write-Host ""
}

# Test MCP server connectivity
function Test-MCPServers {
    Write-Log "Testing MCP server connectivity..."
    
    # Test OpenAI MCP server
    try {
        $TestCommand = "npx @akiojin/openai-mcp-server --help"
        $Result = Invoke-Expression $TestCommand 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "OpenAI MCP server test: PASSED" "SUCCESS"
        }
        else {
            Write-Log "OpenAI MCP server test: FAILED" "ERROR"
        }
    }
    catch {
        Write-Log "OpenAI MCP server test failed: $($_.Exception.Message)" "ERROR"
    }
    
    # Test alternative OpenAI MCP server
    try {
        $TestCommand = "npx @mzxrai/mcp-openai --help"
        $Result = Invoke-Expression $TestCommand 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Alternative OpenAI MCP server test: PASSED" "SUCCESS"
        }
        else {
            Write-Log "Alternative OpenAI MCP server test: FAILED" "ERROR"
        }
    }
    catch {
        Write-Log "Alternative OpenAI MCP server test failed: $($_.Exception.Message)" "ERROR"
    }
}

# Main execution
Write-Log "=== Warp MCP Server Manager Started ==="
Write-Log "Action: $Action"

switch ($Action) {
    "start" {
        Write-Log "Starting all MCP servers..."
        
        $Config = Get-MCPConfig
        if ($Config -eq $null) {
            exit 1
        }
        
        $SuccessCount = 0
        foreach ($ServerName in $Config.mcpServers.PSObject.Properties.Name) {
            $ServerConfig = $Config.mcpServers.$ServerName
            if (Start-MCPServer -ServerName $ServerName -ServerConfig $ServerConfig) {
                $SuccessCount++
            }
        }
        
        Write-Log "MCP server startup complete. Successfully started: $SuccessCount"
        Get-MCPServerStatus
    }
    
    "stop" {
        Write-Log "Stopping all MCP servers..."
        Stop-MCPServers
    }
    
    "status" {
        Get-MCPServerStatus
    }
    
    "restart" {
        Write-Log "Restarting all MCP servers..."
        Stop-MCPServers
        Start-Sleep -Seconds 3
        
        $Config = Get-MCPConfig
        if ($Config -ne $null) {
            $SuccessCount = 0
            foreach ($ServerName in $Config.mcpServers.PSObject.Properties.Name) {
                $ServerConfig = $Config.mcpServers.$ServerName
                if (Start-MCPServer -ServerName $ServerName -ServerConfig $ServerConfig) {
                    $SuccessCount++
                }
            }
            
            Write-Log "MCP server restart complete. Successfully started: $SuccessCount"
            Get-MCPServerStatus
        }
    }
    
    "test" {
        Test-MCPServers
    }
}

Write-Log "=== Warp MCP Server Manager Finished ==="
