"""Subset Matplotlib's fully embedded fonts without rasterizing figures."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
total_before=0;total_after=0
for pdf in sorted((ROOT/'figures').glob('*.pdf')):
    fonts=subprocess.check_output(['pdffonts',str(pdf)]).decode()
    # Rewriting already subset figures is unnecessary.
    if not any('yes no ' in line for line in fonts.splitlines()):continue
    output=ROOT/'.local/tmp'/('subset-'+pdf.name)
    output.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(['gs','-q','-dBATCH','-dNOPAUSE','-dSAFER','-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.5','-dSubsetFonts=true','-dMaxSubsetPct=100',
        '-dEmbedAllFonts=true','-dDownsampleColorImages=false','-dDownsampleGrayImages=false',
        '-dDownsampleMonoImages=false','-sOutputFile='+str(output),str(pdf)],check=True)
    assert output.read_bytes().startswith(b'%PDF')
    total_before+=pdf.stat().st_size;total_after+=output.stat().st_size
    output.replace(pdf)
print('Font subsetting: {} -> {} bytes; vector artwork retained.'.format(total_before,total_after))
