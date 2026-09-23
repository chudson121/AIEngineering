[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Position = 0)]
    [string]$Root = (Get-Location).Path
)

$resolvedRoot = (Resolve-Path -LiteralPath $Root).Path
$excludedFolder = [IO.Path]::DirectorySeparatorChar + 'ci-cd-pipeline' + [IO.Path]::DirectorySeparatorChar

$filesToRename = Get-ChildItem -LiteralPath $resolvedRoot -File -Recurse | Where-Object {
    $relativePath = $_.FullName.Substring($resolvedRoot.Length)
    $relativePath -notlike "$excludedFolder*" -and
    -not $_.Name.Equals('README.md', [StringComparison]::OrdinalIgnoreCase) -and
    $_.Name -cne $_.Name.ToLowerInvariant()
}

$renamePlan = foreach ($file in $filesToRename) {
    $targetPath = Join-Path $file.DirectoryName $file.Name.ToLowerInvariant()
    [PSCustomObject]@{
        Source = $file.FullName
        Target = $targetPath
    }
}

$collisions = $renamePlan | Group-Object { $_.Target.ToLowerInvariant() } | Where-Object Count -gt 1
if ($collisions) {
    $collisionDetails = $collisions | ForEach-Object {
        $_.Group | ForEach-Object { "  $($_.Source) -> $($_.Target)" }
    }
    throw "Cannot continue because lowercasing would create filename collisions:`n$($collisionDetails -join [Environment]::NewLine)"
}

foreach ($rename in $renamePlan) {
    if ((Test-Path -LiteralPath $rename.Target) -and
        $rename.Source -ine $rename.Target) {
        throw "Cannot continue because the target already exists: $($rename.Target)"
    }
}

foreach ($rename in $renamePlan) {
    if ($PSCmdlet.ShouldProcess($rename.Source, "Rename to $($rename.Target)")) {
        $temporaryName = ".lowercase-$([Guid]::NewGuid().ToString('N'))-$([IO.Path]::GetFileName($rename.Source))"
        $temporaryPath = Join-Path (Split-Path -Parent $rename.Source) $temporaryName
        Rename-Item -LiteralPath $rename.Source -NewName $temporaryName
        Rename-Item -LiteralPath $temporaryPath -NewName ([IO.Path]::GetFileName($rename.Target))
    }
}

Write-Output "Processed $($renamePlan.Count) file(s)."
