#!/usr/bin/env python3
"""把 assets/ 下的图片、字体、特效元数据打包成 assets.js（data URL）。

为什么不直接 <img src="assets/...">：双击打开 file:// 时浏览器不让读图片像素，
角色换色就做不了。data URL 没这个限制。

用法：改了 assets/ 里的东西后跑一次  python3 tools/build_assets.py
"""
import base64, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / 'assets', ROOT / 'assets.js'
MIME = {'.png': 'image/png', '.woff2': 'font/woff2'}

assets, fxmeta = {}, {}
for p in sorted(SRC.rglob('*')):
    if p.suffix in MIME:
        key = p.relative_to(SRC).with_suffix('').as_posix()  # 例如 sprites/hero、fx/zap
        assets[key] = f'data:{MIME[p.suffix]};base64,' + base64.b64encode(p.read_bytes()).decode()
    elif p.suffix == '.json' and p.parent.name == 'fx':  # pixelfx 导出的序列帧信息
        m = json.loads(p.read_text())['meta']
        f, px = m['size'], m['pixelfx']
        frames = json.loads(p.read_text())['frames']
        first = frames[0]['frame'] if isinstance(frames, list) else next(iter(frames.values()))['frame']
        fxmeta[p.stem] = {'w': first['w'], 'h': first['h'], 'cols': px['columns'], 'n': len(frames),
                          'fps': px['fps'], 'loop': px['loop'], 'pivot': px['pivot']}

OUT.write_text('// 自动生成，别手改：python3 tools/build_assets.py\n'
               f'window.ASSETS = {json.dumps(assets)};\n'
               f'window.FXMETA = {json.dumps(fxmeta)};\n')
print(f'{len(assets)} assets, {len(fxmeta)} fx -> {OUT.name} ({OUT.stat().st_size // 1024} KB)')
