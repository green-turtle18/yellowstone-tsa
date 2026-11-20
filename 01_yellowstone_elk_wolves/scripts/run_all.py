"""One-command rebuild, analysis, report, notebook execution and numerical checks."""
import os
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPL_IGNORE_SYSTEM_FONTS','1')
os.environ.setdefault('MPLCONFIGDIR','/tmp/yellowstone-mpl')
commands=[['scripts/build_master_dataset.py'],['scripts/analysis.py'],['scripts/summarize_results.py'],
          ['scripts/prepare_notebooks.py'],['scripts/run_notebooks.py'],['supplements/gap_research/build_supplement.py'],['-m','unittest','discover','-s','tests','-v'],['scripts/validate_outputs.py'],['presentation/build_slides.py'],['scripts/refresh_handoffs.py']]
for args in commands:
    print('Running:', ' '.join(args),flush=True)
    subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
print('Completed. Results remain provisional; see reports/HANDOFF.md.')
