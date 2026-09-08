# -*- coding: utf-8 -*-
"""Сквозная сверка чисел: текст документа против таблиц и подписей рисунков.

Ищет в документе все вхождения контрольных величин и сообщает,
если одна и та же величина названа по-разному в разных местах.
"""
import re, sys, collections
from docx import Document

D = Document('MMOSON_v7.docx')
paras = [p.text for p in D.paragraphs]
cells = []
for ti, t in enumerate(D.tables):
    for ri in range(len(t.rows)):
        for ci, c in enumerate(t.rows[ri].cells):
            cells.append((ti, ri, ci, c.text.strip()))

ALL = '\n'.join(paras) + '\n' + '\n'.join(c[3] for c in cells)

# контрольные величины: имя -> (регэксп, ожидаемое, где искать несоответствия)
CHECKS = [
 ('электрическая мощность станции', r'\b658\b',   '721'),
 ('тепловая мощность',              r'\b1\s?462\b','1 603'),
 ('площадь радиатора',              r'\b993\b',   '1 006'),
 ('мест в изоляторе',               r'\b550\b',   '10 951'),
 ('поток карантина',                r'5\s?000 чел','100 000 чел/год'),
 ('срок заселения',                 r'около десяти лет|≈10 лет','10 лет'),
 ('точка размещения',               r'L4|L5|Земля — Луна','L1'),
 ('зеркала',                        r'зеркал','убрать по решению Романа'),
 ('солнечный режим',                r'544 ГВт|190 ГВт','убрать: освещение реакторное'),
]
print('='*74)
print('СКВОЗНАЯ СВЕРКА: устаревшие значения, оставшиеся в тексте и таблицах')
print('='*74)
bad = 0
for name, pat, should in CHECKS:
    hits = []
    for i, tx in enumerate(paras):
        if re.search(pat, tx):
            hits.append(('абз.%d' % i, tx[:110]))
    for ti, ri, ci, tx in cells:
        if re.search(pat, tx):
            hits.append(('табл.%d[%d,%d]' % (ti, ri, ci), tx[:110]))
    if hits:
        bad += len(hits)
        print('\n[!] %s — должно быть: %s' % (name, should))
        for w, tx in hits[:12]:
            print('    %-18s %s' % (w, tx))
        if len(hits) > 12:
            print('    ... ещё %d' % (len(hits)-12))
print()
print('='*74)
print('ИТОГО подозрительных мест: %d' % bad)
