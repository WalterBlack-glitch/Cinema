# Cine Studio — local engine installer (ComfyUI portable + SDXL).
# Robust + resumable. Safe to re-run; skips finished steps.
$ErrorActionPreference = 'Stop'
$base = Join-Path $env:USERPROFILE 'CineStudioLocal'
New-Item -ItemType Directory -Force -Path $base | Out-Null
$log = Join-Path $base 'install.log'
function Log($m){ $t = Get-Date -Format 'HH:mm:ss'; "$t  $m" | Tee-Object -FilePath $log -Append }

Log "=== Cine Studio local engine install ==="
Log "Destino: $base"

# 1) 7zr.exe (extractor para .7z)
$sevenzr = Join-Path $base '7zr.exe'
if (-not (Test-Path $sevenzr)) {
  Log "Descargando 7zr.exe..."
  curl.exe -L -o $sevenzr 'https://www.7-zip.org/a/7zr.exe'
}

# 2) ComfyUI portable (.7z, ~1.5-2GB) — resumable
$archive = Join-Path $base 'comfy_portable.7z'
$portable = Join-Path $base 'ComfyUI_windows_portable'
if (-not (Test-Path $portable)) {
  Log "Descargando ComfyUI portable (resumible)..."
  curl.exe -L -C - -o $archive 'https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia.7z'
  Log "Extrayendo (puede tardar)..."
  & $sevenzr x $archive "-o$base" -y | Out-Null
  if (Test-Path $portable) { Remove-Item $archive -Force -ErrorAction SilentlyContinue }
} else { Log "ComfyUI ya extraido, salto." }

# 3) Localizar carpeta de checkpoints
$ckptDir = Get-ChildItem -Path $base -Recurse -Directory -Filter 'checkpoints' -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -match 'models[\\/]checkpoints' } | Select-Object -First 1 -ExpandProperty FullName
if (-not $ckptDir) { $ckptDir = Join-Path $portable 'ComfyUI\models\checkpoints'; New-Item -ItemType Directory -Force -Path $ckptDir | Out-Null }
Log "checkpoints: $ckptDir"

# 4) SDXL base 1.0 (~6.5GB) — resumable, skip if present & big enough
$ckpt = Join-Path $ckptDir 'sd_xl_base_1.0.safetensors'
$need = $true
if (Test-Path $ckpt) { if ((Get-Item $ckpt).Length -gt 6GB) { $need = $false; Log "SDXL ya presente, salto." } }
if ($need) {
  Log "Descargando SDXL base 1.0 (~6.5GB, resumible)..."
  curl.exe -L -C - -o $ckpt 'https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors'
}

# 5) Marcar listo + guardar rutas
$runbat = Get-ChildItem -Path $portable -Recurse -Filter 'run_nvidia_gpu.bat' -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
@{ portable = $portable; run_bat = $runbat; checkpoint = $ckpt } | ConvertTo-Json | Set-Content -Path (Join-Path $base 'ready.json') -Encoding utf8
Log "LISTO. Arranca con: $runbat"
Log "=== fin ==="
