"""Execute plain-Python notebook cells without requiring a Jupyter server.

Captures stdout, final expressions and Matplotlib figures into standard notebook
outputs. No magics or shell cells supported; failures stop execution immediately.
"""
import ast
import base64
import contextlib
import io
import json
import os
from pathlib import Path
import sys
os.environ.setdefault('MPL_IGNORE_SYSTEM_FONTS','1')
os.environ.setdefault('MPLCONFIGDIR','/tmp/yellowstone-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]


def run(path):
    nb=json.loads(path.read_text());env={'__name__':'__main__'};count=0
    for i,c in enumerate(nb['cells']):
        if c['cell_type']!='code':continue
        count+=1;c['outputs']=[];c['execution_count']=count
        source=''.join(c['source']);tree=ast.parse(source);buf=io.StringIO();val=None
        print(f'{path.name} cell {i}',flush=True)
        with contextlib.redirect_stdout(buf),contextlib.redirect_stderr(buf):
            if tree.body and isinstance(tree.body[-1],ast.Expr):
                exec(compile(ast.Module(body=tree.body[:-1],type_ignores=[]),str(path),'exec'),env)
                val=eval(compile(ast.Expression(tree.body[-1].value),str(path),'eval'),env)
            else:exec(compile(tree,str(path),'exec'),env)
        if buf.getvalue():c['outputs'].append({'output_type':'stream','name':'stdout','text':buf.getvalue().splitlines(True)})
        if val is not None:
            data={'text/plain':repr(val)}
            if hasattr(val,'_repr_html_'):
                html=val._repr_html_()
                if html:data['text/html']=html
            c['outputs'].append({'output_type':'execute_result','execution_count':count,'metadata':{},'data':data})
        for num in plt.get_fignums():
            f=plt.figure(num);b=io.BytesIO();f.savefig(b,format='png',dpi=110,bbox_inches='tight')
            c['outputs'].append({'output_type':'display_data','metadata':{},'data':{'image/png':base64.b64encode(b.getvalue()).decode(),'text/plain':'Matplotlib figure'}})
        plt.close('all')
    nb['metadata']['execution']={'runner':'scripts/run_notebooks.py','python':sys.version.split()[0],'status':'all cells executed'}
    path.write_text(json.dumps(nb,indent=1)+'\n')
    return env


if __name__=='__main__':
    os.chdir(ROOT)
    paths=[ROOT/p for p in sys.argv[1:]] if len(sys.argv)>1 else sorted((ROOT/'notebooks').glob('*.ipynb'))
    for p in paths:run(p)
