<#
.SYNOPSIS
    Automates committing, tagging, building, zipping, and releasing a Python app to GitHub.

.EXAMPLE
    .\release.ps1 -Version "v0.7.5" -CommitMessage "Added UI uniformity, csv export, and few other minor changes."
#>

param (
    [Parameter(Mandatory=$true)]
    [string]$Version,       # Example: "v0.7.4"

    [Parameter(Mandatory=$true)]
    [string]$CommitMessage  # Example: "added UI uniformity, csv export..."
)

# Stop script execution if a command fails
$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting Release Process for $Version..." -ForegroundColor Cyan

# ---------------------------------------------------------
# Step 0: Cleanup
# ---------------------------------------------------------
Write-Host "`n[0/5] Cleaning up transient directories..." -ForegroundColor Yellow
$TransientDirs = "dist", "build", "Output"
foreach ($Dir in $TransientDirs) {
    if (Test-Path $Dir) {
        Write-Host "Removing $Dir..." -ForegroundColor Gray
        Remove-Item -Recurse -Force $Dir
    }
}

# ---------------------------------------------------------
# Step 1: Git Operations (Commit, Push, Tag)
# ---------------------------------------------------------
Write-Host "`n[1/5] Committing and pushing code to Git..." -ForegroundColor Yellow
git add .
git commit -m $CommitMessage

if ($LASTEXITCODE -ne 0) {
    Write-Host "Git commit failed or nothing to commit. Continuing anyway..." -ForegroundColor DarkGray
}

git push origin main

# Ensure Version does not have 'v' for internal metadata but keep for tag
$VersionTag = $Version
if ($VersionTag -notmatch "^v") { $VersionTag = "v$VersionTag" }
$NumericVersion = $Version -replace "^v", ""

Write-Host "Creating and pushing tag $VersionTag..." -ForegroundColor Yellow
$OldPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
git tag $VersionTag -m $VersionTag
git push origin $VersionTag
$ErrorActionPreference = $OldPreference


# ---------------------------------------------------------
# Step 2: Virtual Environment & Dependencies
# ---------------------------------------------------------
Write-Host "`n[2/5] Activating Virtual Environment and installing requirements..." -ForegroundColor Yellow
. .\venv_release\Scripts\Activate.ps1
pip install -r requirements.txt


# ---------------------------------------------------------
# Step 3: Build Executable with PyInstaller
# ---------------------------------------------------------
Write-Host "`n[3/5] Building executable..." -ForegroundColor Yellow

# Run PyInstaller from the packaging directory to keep its context local
# We force the dist and build paths to remain in the project root
pushd packaging
pyinstaller --clean --distpath ../dist --workpath ../build fsQCA_pro.spec
popd

# ---------------------------------------------------------
# Step 4: Zip the Output
# ---------------------------------------------------------
Write-Host "`n[4/5] Zipping the executable..." -ForegroundColor Yellow
$ExePath = ".\dist\fsQCA_pro.exe"
$ZipName = "fsQCA_pro.zip"
$ZipPath = ".\dist\$ZipName"

if (Test-Path $ExePath) {
    Compress-Archive -Path $ExePath -DestinationPath $ZipPath -Force
    Write-Host "Successfully created $ZipPath" -ForegroundColor Green
} else {
    Write-Error "Could not find $ExePath! PyInstaller build may have failed."
    exit 1
}

# ---------------------------------------------------------
# Step 4.5: Build Inno Setup Installer (Optional)
# ---------------------------------------------------------
$ISCC = Get-Command iscc -ErrorAction SilentlyContinue
if ($ISCC) {
    Write-Host "`n[4.5/5] Building Inno Setup Installer..." -ForegroundColor Yellow
    & iscc /DAppVersion=$NumericVersion "packaging\fsQCA_pro.iss"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully created fsQCA_pro_setup.exe" -ForegroundColor Green
    } else {
        Write-Host "Inno Setup build failed." -ForegroundColor Red
    }
} else {
    Write-Host "`n[4.5/5] Inno Setup (iscc) not found in PATH. Skipping installer build." -ForegroundColor Gray
}

# ---------------------------------------------------------
# Step 4.6: Host Installer for Direct Download (Microsoft Store)
# ---------------------------------------------------------
$MsixPath = ".\Output\fsQCA_pro_setup.msix"
$ExeInstallerPath = ".\Output\fsQCA_pro_setup.exe"
$HostFile = $null

if (Test-Path $MsixPath) {
    $HostFile = $MsixPath
} elseif (Test-Path $ExeInstallerPath) {
    $HostFile = $ExeInstallerPath
}

if ($HostFile) {
    Write-Host "`n[4.6/5] Hosting installer for direct download..." -ForegroundColor Yellow
    $FileName = Split-Path $HostFile -Leaf

    # Create a temporary folder for the branch update
    $TempDir = Join-Path $env:TEMP ([Guid]::NewGuid().ToString())
    New-Item -ItemType Directory -Path $TempDir | Out-Null

    try {
        git clone --branch installer-host --single-branch "https://github.com/ghanekark/fsqca_pro.git" $TempDir

        # Create versioned directory in the host branch
        $HostVersionDir = Join-Path $TempDir $NumericVersion
        if (!(Test-Path $HostVersionDir)) { New-Item -ItemType Directory -Path $HostVersionDir | Out-Null }

        # Copy the new installer
        Copy-Item $HostFile -Destination (Join-Path $HostVersionDir $FileName) -Force

        pushd $TempDir
        git add .
        git commit -m "Update installer for $NumericVersion"
        git push origin installer-host
        popd

        Write-Host "Successfully hosted on ghanekark.github.io/fsqca_pro/$NumericVersion/$FileName" -ForegroundColor Green
    } catch {
        Write-Host "Failed to host installer." -ForegroundColor Red
    } finally {
        if (Test-Path $TempDir) { Remove-Item -Recurse -Force $TempDir }
    }
}


# ---------------------------------------------------------
# Step 5: GitHub CLI Release
# ---------------------------------------------------------
Write-Host "`n[5/5] Uploading release to GitHub..." -ForegroundColor Yellow

# We temporarily disable "Stop" on error to check if release exists
$OldPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"

$ReleaseExists = $false
gh release view $VersionTag 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { $ReleaseExists = $true }

$ErrorActionPreference = $OldPreference

if ($ReleaseExists) {
    Write-Host "Release $VersionTag already exists. Updating details and overwriting assets..." -ForegroundColor Yellow
    gh release edit $VersionTag -t "Release $VersionTag" -n $CommitMessage
    gh release upload $VersionTag $ZipPath --clobber
    if (Test-Path $MsixPath) { gh release upload $VersionTag $MsixPath --clobber }
    if (Test-Path $ExeInstallerPath) { gh release upload $VersionTag $ExeInstallerPath --clobber }
} else {
    Write-Host "Creating new release $VersionTag..." -ForegroundColor Yellow
    gh release create $VersionTag $ZipPath -t "Release $VersionTag" -n $CommitMessage
    if (Test-Path $MsixPath) { gh release upload $VersionTag $MsixPath }
    if (Test-Path $ExeInstallerPath) { gh release upload $VersionTag $ExeInstallerPath }
}

Write-Host "`n✅ Release $VersionTag successfully published!" -ForegroundColor Green