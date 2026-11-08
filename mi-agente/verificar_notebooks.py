"""Ejecuta las celdas Python de ambos notebooks, incluido await de nivel superior."""
import ast
import asyncio
import json
from pathlib import Path

async def main():
    root = Path(__file__).resolve().parent
    for path in (root.parent / 'notebooks/a2a-test.ipynb', root / 'notebooks/agente-conversacional.ipynb'):
        namespace = {'__name__': '__main__'}
        print(f'NOTEBOOK {path.name}', flush=True)
        for index, cell in enumerate(json.loads(path.read_text(encoding='utf-8'))['cells']):
            if cell['cell_type'] != 'code':
                continue
            print(f'CELDA {index}', flush=True)
            code = compile(''.join(cell['source']), f'{path}:{index}', 'exec', flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
            result = eval(code, namespace)
            if asyncio.iscoroutine(result):
                await result
        print('OK', path.name, flush=True)

if __name__ == '__main__':
    asyncio.run(main())
