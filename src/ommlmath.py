# -*- coding: utf-8 -*-
"""
Построение настоящих формул Word (OMML) вместо линейной записи.

Формула в Word — это дерево элементов m:oMath. Здесь собран минимум,
нужный документу ММОСО'Н: дробь в два этажа, степень, индекс, корень,
скобки нужной высоты, интеграл с пределами.

Авторы: Бугаенко Роман Сергеевич, НИК.
"""
from docx.oxml.ns import qn, nsmap
from docx.oxml import OxmlElement

# пространство имён математики Office
nsmap.setdefault('m', 'http://schemas.openxmlformats.org/officeDocument/2006/math')


def _el(tag):
    return OxmlElement(tag)


def r(text, italic=None):
    """Математический прогон. Переменные Word ставит курсивом сам,
    но для слов-пояснений и цифр курсив надо снимать явно."""
    run = _el('m:r')
    if italic is not None:
        rpr = _el('m:rPr')
        sty = _el('m:sty')
        sty.set(qn('m:val'), 'i' if italic else 'p')
        rpr.append(sty)
        run.append(rpr)
    t = _el('m:t')
    t.text = text
    # пробелы внутри формулы значимы
    t.set(qn('xml:space'), 'preserve')
    run.append(t)
    return run


def txt(text):
    """Прямой текст внутри формулы (единицы измерения, слова)."""
    return r(text, italic=False)


def num(text):
    """Число: прямым начертанием, как принято в ГОСТ."""
    return r(text, italic=False)


def _wrap(tag, ctrl_children, *content):
    node = _el(tag)
    for c in ctrl_children:
        node.append(c)
    for c in content:
        node.append(c)
    return node


def frac(numerator, denominator):
    """Дробь в два этажа."""
    f = _el('m:f')
    fpr = _el('m:fPr')
    ftype = _el('m:type')
    ftype.set(qn('m:val'), 'bar')
    fpr.append(ftype)
    f.append(fpr)
    n = _el('m:num')
    for c in _seq(numerator):
        n.append(c)
    d = _el('m:den')
    for c in _seq(denominator):
        d.append(c)
    f.append(n)
    f.append(d)
    return f


def sup(base, exponent):
    """Степень."""
    s = _el('m:sSup')
    e = _el('m:e')
    for c in _seq(base):
        e.append(c)
    sp = _el('m:sup')
    for c in _seq(exponent):
        sp.append(c)
    s.append(e)
    s.append(sp)
    return s


def sub(base, index):
    """Нижний индекс."""
    s = _el('m:sSub')
    e = _el('m:e')
    for c in _seq(base):
        e.append(c)
    sb = _el('m:sub')
    for c in _seq(index):
        sb.append(c)
    s.append(e)
    s.append(sb)
    return s


def rad(radicand, degree=None):
    """Корень. Без степени — квадратный."""
    rd = _el('m:rad')
    pr = _el('m:radPr')
    hide = _el('m:degHide')
    hide.set(qn('m:val'), '0' if degree is not None else '1')
    pr.append(hide)
    rd.append(pr)
    dg = _el('m:deg')
    if degree is not None:
        for c in _seq(degree):
            dg.append(c)
    rd.append(dg)
    e = _el('m:e')
    for c in _seq(radicand):
        e.append(c)
    rd.append(e)
    return rd


def delim(content, left='(', right=')'):
    """Скобки, растягивающиеся по высоте содержимого."""
    d = _el('m:d')
    pr = _el('m:dPr')
    b = _el('m:begChr')
    b.set(qn('m:val'), left)
    e_ = _el('m:endChr')
    e_.set(qn('m:val'), right)
    pr.append(b)
    pr.append(e_)
    d.append(pr)
    e = _el('m:e')
    for c in _seq(content):
        e.append(c)
    d.append(e)
    return d


def nary(char, lower, upper, content):
    """Знак с пределами: интеграл, сумма."""
    n = _el('m:nary')
    pr = _el('m:naryPr')
    ch = _el('m:chr')
    ch.set(qn('m:val'), char)
    pr.append(ch)
    for tag, val in (('m:limLoc', 'subSup'),
                     ('m:subHide', '0' if lower is not None else '1'),
                     ('m:supHide', '0' if upper is not None else '1')):
        el = _el(tag)
        el.set(qn('m:val'), val)
        pr.append(el)
    n.append(pr)
    sb = _el('m:sub')
    if lower is not None:
        for c in _seq(lower):
            sb.append(c)
    n.append(sb)
    sp = _el('m:sup')
    if upper is not None:
        for c in _seq(upper):
            sp.append(c)
    n.append(sp)
    e = _el('m:e')
    for c in _seq(content):
        e.append(c)
    n.append(e)
    return n


def _seq(x):
    """Один элемент, список элементов или строка -> список узлов."""
    if x is None:
        return []
    if isinstance(x, str):
        return [r(x)]
    if isinstance(x, (list, tuple)):
        out = []
        for i in x:
            out.extend(_seq(i))
        return out
    return [x]


def omath(*content):
    """Собирает m:oMath из содержимого."""
    m = _el('m:oMath')
    for c in _seq(content):
        m.append(c)
    return m


def set_formula(paragraph, *content, center=True):
    """Заменяет содержимое абзаца формулой."""
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    p = paragraph._p
    for child in list(p):
        if not child.tag.endswith('}pPr'):
            p.remove(child)
    para = _el('m:oMathPara')
    pr = _el('m:oMathParaPr')
    jc = _el('m:jc')
    jc.set(qn('m:val'), 'center' if center else 'left')
    pr.append(jc)
    para.append(pr)
    para.append(omath(*content))
    p.append(para)
    if center:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.first_line_indent = None
    return paragraph
