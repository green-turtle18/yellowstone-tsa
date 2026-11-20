"""Refresh existing handoff archive members from their current source files."""
from pathlib import Path
import os
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    for archive, base in [
        (ROOT/'reports/person1_handoff.zip', ROOT),
        (ROOT/'supplements/gap_research/gap_research_handoff.zip', ROOT/'supplements/gap_research'),
        (ROOT/'supplements/q6_removals/q6_completion_handoff.zip', ROOT/'supplements/q6_removals'),
    ]:
        with zipfile.ZipFile(archive) as old:
            names = [n for n in old.namelist() if not n.endswith('/')]
        if base == ROOT:
            names = sorted(set(names) | {'scripts/refresh_handoffs.py'})
        for name in names:
            source = (base/name).resolve()
            if not source.is_relative_to(base.resolve()) or not source.is_file():
                raise ValueError(f'Missing or unsafe archive member: {name}')
        temporary = archive.with_suffix('.zip.tmp')
        try:
            with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as out:
                for name in names:
                    out.write(base/name, name)
            os.replace(temporary, archive)
        finally:
            temporary.unlink(missing_ok=True)
        print(f'Refreshed {archive.relative_to(ROOT)}')

if __name__ == '__main__':
    main()
