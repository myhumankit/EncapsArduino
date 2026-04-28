# script de verrouillage de cartes et des librairies Arduino
# Script Powershell lancé par l'utilisateur

# 1. Privilèges Administrateur (Méthode robuste)
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# 2. Récupérer le VRAI nom d'utilisateur (celui de la session active)
$RealUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name.Split('\')[1]
if ($env:USERNAME_SESSION) { $RealUser = $env:USERNAME_SESSION }
elseif ($env:USERPROFILE) { $RealUser = $env:USERPROFILE.Split('\')[-1] }
$YAML = "C:\Users\$RealUser\.arduinoIDE\arduino-cli.yaml"

Write-Host "--- Diagnostic ---" -ForegroundColor Yellow
Write-Host "Utilisateur detecte : $RealUser"
Write-Host "Fichier YAML cible  : $YAML"

# Préparation de l'objet notification
Add-Type -AssemblyName System.Windows.Forms
$balloon = New-Object System.Windows.Forms.NotifyIcon
$balloon.Icon = [System.Drawing.Icon]::ExtractAssociatedIcon((Get-Process -id $pid).Path)
$balloon.Visible = $true

if (-not (Test-Path $YAML)) {
    Write-Host "ERREUR : Fichier YAML introuvable." -ForegroundColor Red
    $balloon.ShowBalloonTip(5000, "Arduino IDE", "ERREUR : YAML introuvable", "Error")
    Pause ; exit
}

# 3. Extraction des chemins
$DataPath = ""
$UserPath = ""
foreach ($line in Get-Content $YAML) {
    if ($line.Trim().StartsWith("data:")) {
        $DataPath = $line.Replace("data:", "").Trim().Replace('"', '')
    }
    if ($line.Trim().StartsWith("user:")) {
        $UserPath = $line.Replace("user:", "").Trim().Replace('"', '')
    }
}

if (-not $DataPath) {
    Write-Host "ERREUR : 'Dossier des cartes ' non trouve dans le fichier." -ForegroundColor Red
    Get-Content $YAML | Select-Object -First 10
    Pause ; exit
}

# 4. Définition des dossiers
$CardsDir = Split-Path -Path $DataPath -Parent
$LibDir = Join-Path -Path $UserPath -ChildPath "libraries"

Write-Host "Dossier des cartes : $CardsDir" -ForegroundColor Cyan
Write-Host "Dossier des librairies   : $LibDir" -ForegroundColor Cyan

# 5. Fonctions de Verrouillage
$EveryoneSID = "*S-1-1-0"

function Lock-Folders {
    Write-Host "Passage en Lecture Seule..." -ForegroundColor Yellow
    New-Item "$CardsDir\.locked" -ItemType File -Force    # ecrire fich.marqueur de verrouillage
    # 1. On réinitialise les permissions pour qu'elles soient propres (:reset)
    icacls "$CardsDir" /reset /T /C /Q
    
    # 2. On donne uniquement le droit de Lecture/Exécution (RX) à "Tout le monde"
    # /inheritance:r supprime les droits hérités du dossier parent (souvent trop permissifs)
    # :RX = Read & Execute
    icacls "$CardsDir" /inheritance:r /grant:r "${EveryoneSID}:RX" /T /C /Q
	
    if (Test-Path $LibDir) { 
        icacls "$LibDir" /reset /T /C /Q
        icacls "$LibDir" /inheritance:r /grant:r "${EveryoneSID}:RX" /T /C /Q 
    }
    
    Write-Host "ETAT : VERROUILLE (Lecture seule stricte)" -ForegroundColor Red
    $balloon.ShowBalloonTip(5000, "Arduino IDE", "ETAT : VERROUILLE (Lecture Seule)", "Info")
}

function Unlock-Folders {
    Write-Host "Retablissement des droits complets..." -ForegroundColor Yellow
    
    # On remet l'héritage normal (ce qui redonne les droits d'écriture par défaut de Windows)
    icacls "$CardsDir" /reset /T /C /Q
    icacls "$CardsDir" /inheritance:e /T /C /Q
    Remove-Item "$CardsDir\.locked" -ErrorAction SilentlyContinue  # effacer marqueur de verrouillage
	
    if (Test-Path $LibDir) { 
        icacls "$LibDir" /reset /T /C /Q
        icacls "$LibDir" /inheritance:e /T /C /Q
    }
    
    Write-Host "ETAT : DEVERROUILLE (Controle total)" -ForegroundColor Green
    $balloon.ShowBalloonTip(5000, "Arduino IDE", "ETAT : DEVERROUILLE (Edition)", "Info")
}

# 6. Logique de bascule
$TestFile = Join-Path -Path $CardsDir -ChildPath ".lock_test"
try {
    $null = New-Item -Path $TestFile -ItemType File -ErrorAction Stop
    Remove-Item $TestFile -Force
    Lock-Folders
} catch {
    Unlock-Folders
}

# Petit délai pour laisser la notification apparaître avant la fin du script
Start-Sleep -Seconds 3
 Write-Host "`nTermine. Appuyez sur une touche..."
 $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")