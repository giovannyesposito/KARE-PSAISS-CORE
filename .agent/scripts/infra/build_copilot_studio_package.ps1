param(
    [string]$ConfigPath,
    [string]$OutputPath,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path

if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
    $ConfigPath = Join-Path $repoRoot ".agent\json\copilot-studio.publish.json"
}

if (-not (Test-Path $ConfigPath)) {
    Write-Error "Config file not found: $ConfigPath"
    exit 1
}

$config = Get-Content $ConfigPath -Raw | ConvertFrom-Json

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $repoRoot $config.outputRoot
}

if ([string]::IsNullOrWhiteSpace($config.libraryName)) {
    Write-Error "Config 'libraryName' is required."
    exit 1
}

$libraryRoot = Join-Path $OutputPath $config.libraryName

function New-DirectoryIfMissing {
    param(
        [string]$Path
    )

    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Resolve-RepoPath {
    param(
        [string]$RelativePath
    )

    return Join-Path $repoRoot $RelativePath
}

function Get-FileStem {
    param(
        [string]$RelativePath
    )

    $name = [System.IO.Path]::GetFileName($RelativePath)
    if ($name.EndsWith(".prompt.md")) {
        return $name.Substring(0, $name.Length - 10)
    }

    return [System.IO.Path]::GetFileNameWithoutExtension($name)
}

function Copy-PublishedFile {
    param(
        [string]$SourceRelativePath,
        [string]$DestinationRelativePath
    )

    $sourcePath = Resolve-RepoPath -RelativePath $SourceRelativePath
    if (-not (Test-Path $sourcePath)) {
        Write-Error "Source file not found: $SourceRelativePath"
        exit 1
    }

    $destinationPath = Join-Path $libraryRoot $DestinationRelativePath
    $destinationDir = Split-Path -Parent $destinationPath
    New-DirectoryIfMissing -Path $destinationDir
    Copy-Item -Path $sourcePath -Destination $destinationPath -Force
}

function Copy-PublishedDirectory {
    param(
        [string]$SourceRelativePath,
        [string]$DestinationRelativePath
    )

    $sourcePath = Resolve-RepoPath -RelativePath $SourceRelativePath
    if (-not (Test-Path $sourcePath)) {
        Write-Error "Source directory not found: $SourceRelativePath"
        exit 1
    }

    $destinationPath = Join-Path $libraryRoot $DestinationRelativePath
    New-DirectoryIfMissing -Path $destinationPath
    Copy-Item -Path (Join-Path $sourcePath "*") -Destination $destinationPath -Recurse -Force
}

function Write-AsciiMarkdown {
    param(
        [string]$DestinationRelativePath,
        [string[]]$Lines
    )

    $destinationPath = Join-Path $libraryRoot $DestinationRelativePath
    $destinationDir = Split-Path -Parent $destinationPath
    New-DirectoryIfMissing -Path $destinationDir
    Set-Content -Path $destinationPath -Value $Lines -Encoding ASCII
}

if ($Clean -and (Test-Path $libraryRoot)) {
    Remove-Item -Path $libraryRoot -Recurse -Force
}

New-DirectoryIfMissing -Path $libraryRoot

$fixedDirectories = @(
    "00-governance",
    "10-core\mind",
    "10-core\agents",
    "10-core\skills",
    "10-core\skills-index",
    "20-workflows\create",
    "20-workflows\story",
    "20-workflows\sprint",
    "20-workflows\quality",
    "20-workflows\risk",
    "20-workflows\decision",
    "20-workflows\status",
    "20-workflows\create-issues-jira",
    "30-context",
    "40-artifacts",
    "90-archive"
)

foreach ($relativeDirectory in $fixedDirectories) {
    New-DirectoryIfMissing -Path (Join-Path $libraryRoot $relativeDirectory)
}

Write-Output "[INFO] Publishing core files"

Copy-PublishedFile -SourceRelativePath ".agent\rules\MIND.md" -DestinationRelativePath "10-core\mind\mind__kare-operacional__current.md"

$publishedAgents = @()
foreach ($agentPath in $config.coreAgents) {
    $agentName = Get-FileStem -RelativePath $agentPath
    $destination = "10-core\agents\agent__{0}__current.md" -f $agentName
    Copy-PublishedFile -SourceRelativePath $agentPath -DestinationRelativePath $destination
    $publishedAgents += $agentName
}

$publishedSkills = @()
foreach ($skillDirectory in $config.skillsDirectories) {
    $skillName = Split-Path -Leaf $skillDirectory
    $destination = "10-core\skills\{0}" -f $skillName
    Copy-PublishedDirectory -SourceRelativePath $skillDirectory -DestinationRelativePath $destination
    $publishedSkills += $skillName
}

$publishedWorkflows = @()
foreach ($workflowPath in $config.workflows) {
    $workflowName = Get-FileStem -RelativePath $workflowPath
    $destination = "20-workflows\{0}\workflow__{0}__current.md" -f $workflowName
    Copy-PublishedFile -SourceRelativePath $workflowPath -DestinationRelativePath $destination
    $publishedWorkflows += $workflowName
}

$publishedContexts = @()
foreach ($contextPath in $config.contexts) {
    $contextName = Split-Path -Leaf $contextPath
    $destination = "30-context\{0}" -f $contextName
    Copy-PublishedDirectory -SourceRelativePath $contextPath -DestinationRelativePath $destination
    $publishedContexts += $contextName
}

$publishedArtifacts = @()
foreach ($artifactPath in $config.artifacts) {
    $artifactName = Split-Path -Leaf $artifactPath
    $destination = "40-artifacts\{0}" -f $artifactName
    $resolvedArtifactPath = Resolve-RepoPath -RelativePath $artifactPath

    if (Test-Path $resolvedArtifactPath -PathType Container) {
        Copy-PublishedDirectory -SourceRelativePath $artifactPath -DestinationRelativePath $destination
    }
    else {
        Copy-PublishedFile -SourceRelativePath $artifactPath -DestinationRelativePath (Join-Path "40-artifacts" $artifactName)
    }

    $publishedArtifacts += $artifactName
}

$commandLines = @(
    "# MAPA DE COMANDOS DO KARE",
    "",
    "Este arquivo lista os workflows publicados para uso no Copilot Studio.",
    ""
)

foreach ($workflowName in $publishedWorkflows) {
    $commandLines += "- /$workflowName"
}

Write-AsciiMarkdown -DestinationRelativePath "00-governance\MAPA_DE_COMANDOS__kare__current.md" -Lines $commandLines

$sourcesLines = @(
    "# FONTES AUTORIZADAS DO KARE",
    "",
    "A knowledge base do Copilot Studio deve consumir somente os documentos desta biblioteca.",
    "",
    "## Core Agents"
)

foreach ($agentName in $publishedAgents) {
    $sourcesLines += "- $agentName"
}

$sourcesLines += ""
$sourcesLines += "## Workflows"

foreach ($workflowName in $publishedWorkflows) {
    $sourcesLines += "- $workflowName"
}

if ($publishedContexts.Count -gt 0) {
    $sourcesLines += ""
    $sourcesLines += "## Contexts"
    foreach ($contextName in $publishedContexts) {
        $sourcesLines += "- $contextName"
    }
}

if ($publishedSkills.Count -gt 0) {
    $sourcesLines += ""
    $sourcesLines += "## Skills"
    foreach ($skillName in $publishedSkills) {
        $sourcesLines += "- $skillName"
    }
}

if ($publishedArtifacts.Count -gt 0) {
    $sourcesLines += ""
    $sourcesLines += "## Artifacts"
    foreach ($artifactName in $publishedArtifacts) {
        $sourcesLines += "- $artifactName"
    }
}

Write-AsciiMarkdown -DestinationRelativePath "00-governance\FONTES_AUTORIZADAS__kare__current.md" -Lines $sourcesLines

$indexLines = @(
    "# INDICE OPERACIONAL DO KARE",
    "",
    "## Agents",
    ""
)

foreach ($agentName in $publishedAgents) {
    $indexLines += "- $agentName"
}

$indexLines += ""
$indexLines += "## Skills"
$indexLines += ""

foreach ($skillName in $publishedSkills) {
    $indexLines += "- $skillName"
}

$indexLines += ""
$indexLines += "## Workflows"
$indexLines += ""

foreach ($workflowName in $publishedWorkflows) {
    $indexLines += "- $workflowName"
}

Write-AsciiMarkdown -DestinationRelativePath "10-core\skills-index\index__kare-core__current.md" -Lines $indexLines

$manifest = [ordered]@{
    libraryName = $config.libraryName
    generatedAt = (Get-Date).ToString("s")
    sourceRoot = $repoRoot
    published = [ordered]@{
        mind = "10-core/mind/mind__kare-operacional__current.md"
        agents = $publishedAgents
        skills = $publishedSkills
        workflows = $publishedWorkflows
        contexts = $publishedContexts
        artifacts = $publishedArtifacts
    }
}

$manifestPath = Join-Path $libraryRoot "package-manifest.json"
$manifest | ConvertTo-Json -Depth 10 | Set-Content -Path $manifestPath -Encoding ASCII

Write-Output "[OK] Copilot Studio package generated at: $libraryRoot"