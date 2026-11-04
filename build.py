"""Rebuild everything from cached raw data: python build.py  (add --fetch to also fetch missing YouTube metadata)."""
import subprocess, sys, os
here = os.path.dirname(os.path.abspath(__file__))
def run(s): print('==', s, flush=True); subprocess.run([sys.executable, '-I', os.path.join(here, 'scripts', s)], check=True, cwd=here)
run('build_mentions.py')
if '--fetch' in sys.argv: run('fetch_meta.py')
run('rank.py')
