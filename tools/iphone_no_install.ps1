param(
    [ValidateSet('cloud','signed')]
    [string]$Mode = 'cloud'
)
# NOTE: PowerShell variables are case-insensitive. Do not reuse $Mode as $mode.

$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$OutputDir = Join-Path $Root 'ios_output'
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

function Write-Title([string]$Text) {
    Write-Host ''
    Write-Host '==============================================' -ForegroundColor Cyan
    Write-Host ('  ' + $Text) -ForegroundColor Cyan
    Write-Host '==============================================' -ForegroundColor Cyan
}

function Get-PlainText([Security.SecureString]$Secure) {
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Secure)
    try { return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
}

Write-Title '12/D DIL PROGRAMI - iPHONE OLUSTUR'
Write-Host 'Ekstra Git, GitHub CLI veya Mac kurulumu gerekmez.' -ForegroundColor Green
Write-Host 'Windows PowerShell GitHub API ile buluttaki macOS build makinesini tetikler.'
Write-Host ''

$TokenSecure = Read-Host 'GitHub Personal Access Token (ekranda gorunmez)' -AsSecureString
$Token = Get-PlainText $TokenSecure
if ([string]::IsNullOrWhiteSpace($Token)) { throw 'GitHub token girilmedi.' }

$Headers = @{
    Authorization = "Bearer $Token"
    Accept = 'application/vnd.github+json'
    'X-GitHub-Api-Version' = '2022-11-28'
    'User-Agent' = '12D-Dil-Programi-iPhone-Builder'
}

function Invoke-GH {
    param(
        [Parameter(Mandatory=$true)][string]$Method,
        [Parameter(Mandatory=$true)][string]$Uri,
        $Body = $null,
        [switch]$Allow404
    )
    try {
        if ($null -eq $Body) {
            return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $Headers
        }
        $json = $Body | ConvertTo-Json -Depth 20 -Compress
        return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $Headers -Body $json -ContentType 'application/json'
    }
    catch {
        $status = $null
        try { $status = [int]$_.Exception.Response.StatusCode } catch {}
        if ($Allow404 -and ($status -eq 404 -or $status -eq 409)) { return $null }

        if ($status -eq 403 -and $Uri -eq 'https://api.github.com/user/repos') {
            Write-Host ''
            Write-Host '[HATA] GitHub tokeni yeni repository olusturmaya yetkili degil.' -ForegroundColor Red
            Write-Host 'Repositoryyi GitHub sitesinden elle olusturup ayni adi tekrar girebilirsin.'
            Write-Host 'Ya da tokena repository olusturma/yazma yetkisi ver.'
            exit 13
        }

        if ($status -eq 409 -and $Uri -like '*/git/blobs') {
            Write-Host ''
            Write-Host '[HATA] GitHub repository bos oldugu icin blob yazilamadi.' -ForegroundColor Red
            Write-Host 'Bu surum normalde bos repoyu otomatik baslatir.'
            Write-Host 'BAT dosyasini yeniden calistir. Sorun surerse logu gonder.'
            exit 14
        }

        throw
    }
}

Write-Host '[1/7] GitHub hesabi kontrol ediliyor...'
$Me = Invoke-GH -Method GET -Uri 'https://api.github.com/user'
$Owner = $Me.login
Write-Host ("      GitHub: @" + $Owner) -ForegroundColor Green

$defaultRepo = '12D-Dil-Programi-Mobile'
$RepoName = Read-Host "Repository adi [$defaultRepo]"
if ([string]::IsNullOrWhiteSpace($RepoName)) { $RepoName = $defaultRepo }
$RepoName = ($RepoName -replace '[^A-Za-z0-9._-]', '-')

$RepoApi = "https://api.github.com/repos/$Owner/$RepoName"
$Repo = Invoke-GH -Method GET -Uri $RepoApi -Allow404

Write-Host '[2/7] GitHub repository hazirlaniyor...'
if ($null -eq $Repo) {
    $Repo = Invoke-GH -Method POST -Uri 'https://api.github.com/user/repos' -Body @{
        name = $RepoName
        private = $true
        description = '12/D Dil Programi Android + iPhone mobile app'
        auto_init = $true
    }
    Write-Host '      Yeni private repository olusturuldu.' -ForegroundColor Green
} else {
    Write-Host '      Repository zaten var; guncellenecek.' -ForegroundColor Green
}

if ($null -ne $Repo.permissions -and $Repo.permissions.push -eq $false) {
    Write-Host ''
    Write-Host '[HATA] Bu tokenin repository yazma yetkisi yok.' -ForegroundColor Red
    Write-Host 'GitHub tokeninda Contents/Repository write yetkisi vermelisin.'
    Write-Host 'Repository: ' $Repo.full_name
    exit 12
}

$Branch = if ($Repo.default_branch) { $Repo.default_branch } else { 'main' }
if ([string]::IsNullOrWhiteSpace($Branch)) { $Branch = 'main' }

# Files that should never be pushed to the cloud build repo.
$skipDirs = @('.git','.buildozer','__pycache__','.venv','.iosvenv','.buildvenv','.gradle','node_modules','ios_output','ipa_output','bin','dist','build')
$skipNames = @('android_build.log','mobile_error.log','ios_build.log')

Write-Host '[3/7] Proje dosyalari GitHub icin hazirlaniyor...'
$AllFiles = Get-ChildItem -Path $Root -Recurse -File | Where-Object {
    $full = $_.FullName
    $relative = ($full.Substring($Root.Length) -replace '^[\\/]+','')
    $parts = $relative -split '[\\/]'
    $blocked = $false
    foreach ($d in $skipDirs) {
        if ($parts -contains $d) { $blocked = $true; break }
    }
    if ($skipNames -contains $_.Name) { $blocked = $true }
    if ($_.Extension -eq '.zip' -and $_.DirectoryName -eq $Root) { $blocked = $true }
    -not $blocked
}

if ($AllFiles.Count -lt 1) { throw 'Yuklenecek proje dosyasi bulunamadi.' }
Write-Host ("      " + $AllFiles.Count + ' dosya bulundu.')

# Resolve current HEAD/tree. GitHub's raw Git Database API returns 409
# when a repository is completely empty. In that case initialize the repo
# through the Contents API first, then continue with blobs/trees/commits.
$Ref = Invoke-GH -Method GET -Uri "$RepoApi/git/ref/heads/$Branch" -Allow404

if ($null -eq $Ref) {
    Write-Host '      Repository bos; ilk commit otomatik olusturuluyor...' -ForegroundColor Yellow

    $InitText = "12/D Dil Programi - iOS cloud build repository`n"
    $InitBytes = [Text.Encoding]::UTF8.GetBytes($InitText)
    $InitBase64 = [Convert]::ToBase64String($InitBytes)

    try {
        Invoke-GH -Method PUT -Uri "$RepoApi/contents/.12d-init.txt" -Body @{
            message = 'Initialize 12D iOS build repository'
            content = $InitBase64
        } | Out-Null
    }
    catch {
        Write-Host ''
        Write-Host '[HATA] Bos GitHub repository otomatik baslatilamadi.' -ForegroundColor Red
        Write-Host 'Tokenin Contents: Read and write yetkisi oldugunu kontrol et.'
        throw
    }

    Start-Sleep -Seconds 2

    # Refresh repository metadata/default branch after the first commit.
    $Repo = Invoke-GH -Method GET -Uri $RepoApi
    $Branch = if ($Repo.default_branch) { $Repo.default_branch } else { 'main' }
    if ([string]::IsNullOrWhiteSpace($Branch)) { $Branch = 'main' }

    $Ref = Invoke-GH -Method GET -Uri "$RepoApi/git/ref/heads/$Branch" -Allow404
    if ($null -eq $Ref) {
        throw 'Repository ilk commit sonrasi hala HEAD olusturmadi.'
    }

    Write-Host '      Ilk commit olusturuldu. Dosya yukleme devam ediyor.' -ForegroundColor Green
}

$ParentSha = $Ref.object.sha
$CurrentCommit = Invoke-GH -Method GET -Uri "$RepoApi/git/commits/$ParentSha"
$BaseTreeSha = $CurrentCommit.tree.sha

# Create blobs.
$TreeEntries = @()
$i = 0
foreach ($File in $AllFiles) {
    $i++
    $rel = (($File.FullName.Substring($Root.Length) -replace '^[\\/]+','') -replace '\\','/')
    Write-Progress -Activity 'GitHub dosyalari yukleniyor' -Status "$i / $($AllFiles.Count) - $rel" -PercentComplete (($i / [double]$AllFiles.Count) * 100)

    $bytes = [IO.File]::ReadAllBytes($File.FullName)
    $b64 = [Convert]::ToBase64String($bytes)
    $Blob = Invoke-GH -Method POST -Uri "$RepoApi/git/blobs" -Body @{ content = $b64; encoding = 'base64' }
    $gitFileMode = if ($File.Extension -in @('.sh','.command')) { '100755' } else { '100644' }
    $TreeEntries += @{ path = $rel; mode = $gitFileMode; type = 'blob'; sha = $Blob.sha }
}
Write-Progress -Activity 'GitHub dosyalari yukleniyor' -Completed

if ($TreeEntries.Count -lt 1) {
    throw 'GitHub tree icin hic dosya girdisi olusturulamadi.'
}
$TreeBody = @{ tree = $TreeEntries }
if ($BaseTreeSha) { $TreeBody.base_tree = $BaseTreeSha }
Write-Host ('      ' + $TreeEntries.Count + ' dosya GitHub tree listesine eklendi.') -ForegroundColor Green
$NewTree = Invoke-GH -Method POST -Uri "$RepoApi/git/trees" -Body $TreeBody

$CommitBody = @{
    message = '12D Dil Programi iOS cloud build update'
    tree = $NewTree.sha
}
if ($ParentSha) { $CommitBody.parents = @($ParentSha) } else { $CommitBody.parents = @() }
$NewCommit = Invoke-GH -Method POST -Uri "$RepoApi/git/commits" -Body $CommitBody

if ($ParentSha) {
    Invoke-GH -Method PATCH -Uri "$RepoApi/git/refs/heads/$Branch" -Body @{ sha = $NewCommit.sha; force = $true } | Out-Null
} else {
    Invoke-GH -Method POST -Uri "$RepoApi/git/refs" -Body @{ ref = "refs/heads/$Branch"; sha = $NewCommit.sha } | Out-Null
}
Write-Host '      Proje GitHub repositoryye gonderildi.' -ForegroundColor Green

$WorkflowFile = if ($Mode -eq 'signed') { 'ios-signed-ipa.yml' } else { 'ios-cloud-build.yml' }
$ArtifactName = if ($Mode -eq 'signed') { '12D-Dil-Programi-iPhone-IPA' } else { '12D-Dil-Programi-iOS-Xcode-Project' }

if ($Mode -eq 'signed') {
    Write-Host '[4/7] Apple imzalama ayarlari kontrol ediliyor...'
    $required = @('IOS_CERTIFICATE_P12_BASE64','IOS_CERTIFICATE_PASSWORD','IOS_PROVISIONING_PROFILE_BASE64','IOS_TEAM_ID')
    $Secrets = Invoke-GH -Method GET -Uri "$RepoApi/actions/secrets?per_page=100"
    $names = @($Secrets.secrets | ForEach-Object { $_.name })
    $missing = @($required | Where-Object { $names -notcontains $_ })
    if ($missing.Count -gt 0) {
        Write-Host ''
        Write-Host '[DURDU] Gercek iPhone IPA icin Apple signing bilgileri eksik:' -ForegroundColor Yellow
        $missing | ForEach-Object { Write-Host ('  - ' + $_) }
        Write-Host ''
        Write-Host 'Bu Apple zorunlulugudur. Degerleri bana gonderme.'
        Write-Host 'GitHub Secrets sayfasi tarayicida aciliyor...'
        Start-Process "https://github.com/$Owner/$RepoName/settings/secrets/actions"
        Write-Host 'Secrets eklendikten sonra IPHONE_OLUSTUR.bat dosyasini tekrar acip [2] sec.'
        exit 20
    }
    Write-Host '      Apple signing secret adlari mevcut.' -ForegroundColor Green
} else {
    Write-Host '[4/7] Cloud build modu hazir.'
}

Write-Host '[5/7] GitHub macOS iPhone build baslatiliyor...'
$DispatchAt = [DateTime]::UtcNow.AddMinutes(-1)
Invoke-GH -Method POST -Uri "$RepoApi/actions/workflows/$WorkflowFile/dispatches" -Body @{ ref = $Branch } | Out-Null
Write-Host '      Workflow tetiklendi.' -ForegroundColor Green

Write-Host '[6/7] Build sonucu bekleniyor...'
$Run = $null
for ($findTry = 0; $findTry -lt 24 -and $null -eq $Run; $findTry++) {
    Start-Sleep -Seconds 5
    $Runs = Invoke-GH -Method GET -Uri "$RepoApi/actions/workflows/$WorkflowFile/runs?event=workflow_dispatch&branch=$Branch&per_page=10"
    $Run = @($Runs.workflow_runs | Where-Object { ([DateTime]$_.created_at) -ge $DispatchAt } | Sort-Object created_at -Descending | Select-Object -First 1)
    if ($Run.Count -gt 0) { $Run = $Run[0] } else { $Run = $null }
}
if ($null -eq $Run) { throw 'Baslatilan GitHub Actions build kaydi bulunamadi.' }

Write-Host ("      Run ID: " + $Run.id)
Write-Host ("      " + $Run.html_url)

while ($true) {
    $Run = Invoke-GH -Method GET -Uri "$RepoApi/actions/runs/$($Run.id)"
    $now = Get-Date -Format 'HH:mm:ss'
    Write-Host ("      [$now] status=" + $Run.status + ' conclusion=' + $Run.conclusion)
    if ($Run.status -eq 'completed') { break }
    Start-Sleep -Seconds 15
}

if ($Run.conclusion -ne 'success') {
    Write-Host ''
    Write-Host ('[HATA] iPhone build basarisiz: ' + $Run.conclusion) -ForegroundColor Red
    Write-Host $Run.html_url
    Start-Process $Run.html_url
    exit 30
}

Write-Host '[7/7] iPhone build sonucu indiriliyor...'
$Artifacts = Invoke-GH -Method GET -Uri "$RepoApi/actions/runs/$($Run.id)/artifacts?per_page=100"
$Artifact = @($Artifacts.artifacts | Where-Object { $_.name -eq $ArtifactName } | Select-Object -First 1)
if ($Artifact.Count -lt 1) {
    $Artifact = @($Artifacts.artifacts | Select-Object -First 1)
}
if ($Artifact.Count -lt 1) { throw 'Build basarili fakat indirilecek artifact bulunamadi.' }
$Artifact = $Artifact[0]

$OutFile = if ($Mode -eq 'signed') {
    Join-Path $OutputDir '12D_Dil_Programi_iPhone_IPA.zip'
} else {
    Join-Path $OutputDir '12D_Dil_Programi_iOS_Xcode_Project.zip'
}

Invoke-WebRequest -Uri $Artifact.archive_download_url -Headers $Headers -OutFile $OutFile -UseBasicParsing

Write-Host ''
Write-Title 'iPHONE BUILD TAMAMLANDI'
Write-Host ('Dosya: ' + $OutFile) -ForegroundColor Green
if ($Mode -eq 'signed') {
    Write-Host 'ZIP icinde imzali .ipa bulunur. Bu build Apple signing bilgilerinle olusturuldu.' -ForegroundColor Green
} else {
    Write-Host 'Bu Cloud Build Xcode/iOS derleme sonucudur; gercek iPhone kurulumu icin imzali IPA modu gerekir.' -ForegroundColor Yellow
}
Write-Host ''
Start-Process explorer.exe -ArgumentList $OutputDir
