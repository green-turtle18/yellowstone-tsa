"""Record output validation after run_all has successfully run the test suite."""
from pathlib import Path
import json
import unittest
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]

def main():
    notebooks=[]
    for path in sorted((ROOT/'notebooks').glob('*.ipynb')):
        nb=json.loads(path.read_text())
        cells=[c for c in nb['cells'] if c['cell_type']=='code' and ''.join(c['source']).strip()]
        errors=sum(o.get('output_type')=='error' for c in cells for o in c.get('outputs',[]))
        executed=sum(c.get('execution_count') is not None for c in cells)
        if errors or executed!=len(cells):
            raise RuntimeError(f'Incomplete notebook execution: {path.name}')
        notebooks.append(dict(notebook=str(path.relative_to(ROOT)),executed_code_cells=executed,errors=errors))
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    result=dict(notebooks=notebooks,unit_tests=suite.countTestCases(),status='passed',
        command='python scripts/run_all.py',checked_at=datetime.now(timezone.utc).isoformat(),
        scope='Notebook execution checked here; run_all invokes this only after its tests pass.')
    (ROOT/'reports/validation.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
