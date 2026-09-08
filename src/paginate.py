# -*- coding: utf-8 -*-
"""Оценка разбиения MMOSON_v7.docx на страницы.

Точную вёрстку делает Word; здесь моделируется поток текста, чтобы
подставить в оглавление ПРАВДОПОДОБНЫЕ номера вместо заглушек.
Погрешность оценки — единицы страниц к концу документа.
"""
from docx import Document
from docx.oxml.ns import qn
from docx.shared import Emu

# Калибровано по фактической вёрстке Word 07.09.2026: приложение В — стр. 116.
# 81 знак — геометрический предел строки; Word переносов не делает, строка
# рвётся по словам и заполняется примерно на 90 %, отсюда 73.
CPL_BASE = 72.0          # знаков в строке при 12 pt на ширине 17,1 см
LINE_CM  = 0.49          # высота строки 12 pt при интерлиньяже 1,15

def _lines(text, size_pt, indent_cm=0.0, first_line_cm=0.0):
    if not text:
        return 1
    cpl = CPL_BASE * (12.0 / size_pt) * (17.1 - indent_cm) / 17.1
    n = len(text) + max(0.0, first_line_cm) / 0.21
    return max(1, int(n / cpl + 0.9999))

def estimate(path='MMOSON_v7.docx', verbose=False):
    d = Document(path)
    sec = d.sections[0]
    page_cm = Emu(sec.page_height - sec.top_margin - sec.bottom_margin).cm
    body = d.element.body

    from docx.text.paragraph import Paragraph
    from docx.table import Table

    page, used = 1, 0.0
    marks = {}                      # закладка -> номер страницы

    def feed(h_cm):
        nonlocal page, used
        if used + h_cm > page_cm:
            page += 1
            used = h_cm
        else:
            used += h_cm

    for child in body.iterchildren():
        if child.tag == qn('w:p'):
            p = Paragraph(child, d)
            # закладки этого абзаца -> текущая страница
            for bm in child.findall(qn('w:bookmarkStart')):
                nm = bm.get(qn('w:name'))
                if nm and nm.startswith('_Toc'):
                    marks[nm] = page
            # разрыв страницы
            if child.findall('.//' + qn('w:br') + '[@' + qn('w:type') + '="page"]'):
                page += 1; used = 0.0
                continue
            # рисунок
            if child.findall('.//' + qn('a:blip')):
                ext = child.findall('.//' + qn('wp:extent'))
                h = Emu(int(ext[0].get('cy'))).cm if ext else 8.0
                feed(h + 0.4)
                continue
            pf = p.paragraph_format
            sizes = [r.font.size.pt for r in p.runs if r.font.size]
            size = sizes[0] if sizes else 12.0
            ind = pf.left_indent.cm if pf.left_indent else 0.0
            fli = pf.first_line_indent.cm if pf.first_line_indent else 0.0
            before = pf.space_before.pt if pf.space_before else 0.0
            after = pf.space_after.pt if pf.space_after else 0.0
            h = (_lines(p.text, size, ind, fli) * LINE_CM * (size / 12.0)
                 + (before + after) / 28.35)
            feed(h)
        elif child.tag == qn('w:tbl'):
            tbl = Table(child, d)
            h = 0.0
            for row in tbl.rows:
                mx = 1
                for c in row.cells:
                    for cp in c.paragraphs:
                        mx = max(mx, _lines(cp.text, 10.0, 0.0, 0.0))
                h += mx * 0.42 + 0.10
            feed(h + 0.3)
    return marks, page

# ── калибровка по фактической вёрстке Word ─────────────────────────────
# Модель потока не воспроизводит вёрстку точно (переносы, вдовы/сироты,
# отрыв таблиц). Поэтому оценка приводится к опорным точкам, снятым
# Романом в Word: кусочно-линейное растяжение шкалы между ними.
# При изменении объёма документа точки снять заново.
ANCHORS = [('ПРИЛОЖЕНИЕ Б', 85), ('ПРИЛОЖЕНИЕ В', 116)]

def calibrate(marks, names):
    """marks: закладка->оценка; names: закладка->текст заголовка."""
    pts = []
    for pref, real in ANCHORS:
        for k, v in marks.items():
            if names.get(k, '').startswith(pref):
                pts.append((v, real)); break
    if not pts:
        return marks
    pts.sort()
    def conv(x):
        if x <= pts[0][0]:
            k = pts[0][1] / pts[0][0] if pts[0][0] else 1.0
            return max(1, int(round(x * k)))
        for (e0, r0), (e1, r1) in zip(pts, pts[1:]):
            if x <= e1:
                if e1 == e0:
                    return r1
                return int(round(r0 + (x - e0) * (r1 - r0) / (e1 - e0)))
        (e0, r0) = pts[-1]
        if len(pts) > 1:
            (ep, rp) = pts[-2]
            k = (r0 - rp) / (e0 - ep) if e0 != ep else 1.0
        else:
            k = r0 / e0 if e0 else 1.0
        return int(round(r0 + (x - e0) * k))
    out = {k: conv(v) for k, v in marks.items()}
    # монотонность по порядку следования в документе
    order = sorted(marks, key=lambda k: (marks[k], k))
    cur = 0
    for k in order:
        cur = max(cur, out[k]); out[k] = cur
    return out


if __name__ == '__main__':
    m, total = estimate()
    print('оценка объёма:', total, 'стр.')
    print('закладок размечено:', len(m))
    ks = sorted(m.items(), key=lambda kv: kv[1])
    print('первая:', ks[0], '| последняя:', ks[-1])
