
param(
    [Parameter(Mandatory=$true)]
    [string]$RepoUrl
)

$ErrorActionPreference = "Stop"

git init
git add .
git commit -m "Initial Crete accident data pipeline"
git branch -M main
git remote add origin $RepoUrl
git push -u origin main
