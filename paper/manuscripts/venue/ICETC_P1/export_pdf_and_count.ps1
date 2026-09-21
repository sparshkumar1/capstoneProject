# Opens the built DOCX files in Word, reports the exact page count, exports PDFs, and optionally renders page PNGs for visual QA.
# Usage: powershell -File export_pdf_and_count.ps1 [-RenderDir <folder>]
param([string]$RenderDir = "")
Add-Type -AssemblyName System.Drawing
$base = Join-Path $PSScriptRoot "build"
$w = New-Object -ComObject Word.Application; $w.Visible = $true; $w.DisplayAlerts = 0
foreach ($n in "P1_ICETC_BLINDED", "P1_ICETC_MASTER") {
  $d = $w.Documents.Open("$base\$n.docx", $false, $true)
  $w.ActiveWindow.View.Type = 3
  $d.Repaginate()
  $pages = $d.ComputeStatistics(2)
  "{0}: pages={1} words={2}" -f $n, $pages, $d.ComputeStatistics(0)
  $d.ExportAsFixedFormat("$base\$n.pdf", 17)
  if ($RenderDir -ne "") {
    for ($i = 1; $i -le $pages; $i++) {
      $bytes = $w.ActiveWindow.ActivePane.Pages.Item($i).EnhMetaFileBits
      $img = [System.Drawing.Image]::FromStream((New-Object System.IO.MemoryStream(, $bytes)))
      $bmp = New-Object System.Drawing.Bitmap 1275, 1650
      $g = [System.Drawing.Graphics]::FromImage($bmp); $g.Clear([System.Drawing.Color]::White); $g.InterpolationMode = 'HighQualityBicubic'
      $g.DrawImage($img, 0, 0, 1275, 1650); $g.Dispose()
      $bmp.Save("$RenderDir\$n-page$i.png", [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose(); $img.Dispose()
    }
  }
  $d.Close($false)
}
$w.Quit()
