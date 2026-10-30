$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
python -m poc_aditivos --saida .\saida_demo
python -m unittest discover -s tests -v
