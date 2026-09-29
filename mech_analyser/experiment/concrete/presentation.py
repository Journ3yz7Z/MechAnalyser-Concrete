"""Shared labels and annotation geometry, without changing regression inputs."""
import html
import re
import numpy as np


def rich(text, size=12, bold=False):
    escaped = html.escape(str(text)).replace('\n', '<br>')
    escaped = re.sub(r'([\u3400-\u9fff]+)', r'<span style="font-family:SimSun">\1</span>', escaped)
    return f'<span style="color:#111111; font-family:Times New Roman; font-size:{size}pt; font-weight:{"bold" if bold else "normal"}">{escaped}</span>'


def parameter_text(a):
    return (a.metadata.get('test_type') or '单轴压缩试验') + '\n' + '\n'.join(f'{k}：{v}' for k,v in parameter_rows(a))


def injection_text(value):
    value = str(value).strip()
    if not value:
        return '未填写'
    try:
        hours = float(value)
        if abs(hours-1/6) < 1e-8:
            return '10 分钟'
        return f'{hours:g} 小时'
    except ValueError:
        return value


def unpressurized(value):
    try:
        return float(str(value).strip().lower().replace('mpa','').strip()) == 0
    except (ValueError, TypeError):
        return False


def parameter_rows(a):
    m = a.metadata
    val = lambda k: str(m.get(k, '')).strip() or '未填写'
    rows = [('材料',val('material')),('水泥/细骨料',f'{m.get("cement_ratio") or "1"}:{val("aggregate_ratio")}'),
            ('含水率',f'{val("water_content")} %'),('压注压强',f'{val("pressure")} MPa'),
            ('压注时间',injection_text(m.get('injection_hours',''))),('养护天数',f'{val("curing_days")} 天')]
    if '三轴' in str(m.get('test_type', '')):
        rows.insert(0, ('围压', f'{val("confining_pressure")} MPa'))
    return [(label,value) for label,value in rows if label != '压注时间' or not unpressurized(m.get('pressure'))]


def poisson_html(a):
    r = a.result
    if r.get('nu') is None:
        return rich('泊松比：无法拟合',12)
    return ('<table cellspacing="0" cellpadding="2" style="font-family:Times New Roman;font-size:13pt"><tr>'
            '<td rowspan="2"><i>ν</i> = −</td><td style="border-bottom:1px solid black"><i>E</i></td>'
            f'<td rowspan="2"> = {r["nu"]:.4f}</td></tr>'
            '<tr><td><i>k</i><sub style="font-family:SimSun">横</sub></td></tr></table>')


def band(a):
    if not len(a.selected):
        return None
    if a.parameters.mode == 'strain':
        return float(a.selected.stress.min()), float(a.selected.stress.max())
    return a.result.get('threshold_low'), a.result.get('threshold_high')


def arrow_x(a, xmin, xmax, lo, hi):
    """Choose a clear x position in the band, avoiding both measured curves."""
    f = a.raw_data.frame
    nearby = f[(f.stress >= lo) & (f.stress <= hi)]
    xs = np.concatenate([nearby.axial.to_numpy(), nearby.hoop.to_numpy()])
    xs = xs[np.isfinite(xs)]
    candidates = xmin + np.array([.62, .48, .32, .76]) * (xmax-xmin)
    if not len(xs):
        return float(candidates[0])
    return float(max(candidates, key=lambda x: np.min(np.abs(xs-x))))


def clear_box(a, ranges, size, preferred, obstacles=()):
    """Find a rectangle clear of curves, zero-axis ticks and band boundaries.

    Coordinates are normalized to the view; no data or regression is altered.
    None requests a separate results area rather than covering measured data.
    """
    (xmin,xmax),(ymin,ymax)=ranges
    w,h=size
    dx,dy=xmax-xmin,ymax-ymin
    f=a.raw_data.frame
    valid=f.valid.to_numpy()
    segments=[]
    for key in ('axial','hoop'):
        x=(f[key].to_numpy()-xmin)/dx
        y=(f.stress.to_numpy()-ymin)/dy
        ok=valid[:-1]&valid[1:]&np.isfinite(x[:-1])&np.isfinite(x[1:])
        segments.append((np.minimum(x[:-1],x[1:])[ok],np.maximum(x[:-1],x[1:])[ok],
                         np.minimum(y[:-1],y[1:])[ok],np.maximum(y[:-1],y[1:])[ok]))
    zero=(0-xmin)/dx
    obstacles=list(obstacles)+[(zero-.045,0,zero+.014,1)]
    bounds=band(a)
    if bounds:
        obstacles += [(0,(v-ymin)/dy-.008,1,(v-ymin)/dy+.008) for v in bounds]
    choices=[preferred]+[(float(x),float(y)) for y in np.linspace(.025,.92-h,25)
                        for x in np.linspace(.025,.975-w,30)]
    choices.sort(key=lambda p:(p[0]-preferred[0])**2+(p[1]-preferred[1])**2)
    for x,y in choices:
        l,b,r,t=x-.008,y-.008,x+w+.008,y+h+.008
        if l<0 or b<0 or r>1 or t>1: continue
        if any(l<rr and r>ll and b<tt and t>bb for ll,bb,rr,tt in obstacles): continue
        if any(np.any((left<r)&(right>l)&(bottom<t)&(top>b)) for left,right,bottom,top in segments): continue
        return x,y
    return None
