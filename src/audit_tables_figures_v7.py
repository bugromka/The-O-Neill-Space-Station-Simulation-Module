# -*- coding: utf-8 -*-
"""Автоматическая сверка таблиц, подписей и встроенных рисунков MMOSON_v7.

Скрипт не заменяет инженерную верификацию из verify_all.py. Он проверяет
редакционные связи: суммы в сводных таблицах, обязательные статусы,
архитектурную формулировку, транспортные итоги, количество подписей и
встроенных PNG, а также то, что две обновлённые ресурсные иллюстрации
действительно попали в DOCX.
"""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import hashlib
import re
import sys
import zipfile

from docx import Document
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DOC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "MMOSON_russian_publication.docx"
FIG = ROOT / "src" / "fig"
errors: list[str] = []
notes: list[str] = []

D = Document(DOC)

def fail(msg: str) -> None:
    errors.append(msg)

def norm(s: str) -> str:
    return " ".join(s.split())

def find_table(predicate, label: str):
    found = []
    for i, t in enumerate(D.tables, 1):
        text = "\n".join(norm(c.text) for r in t.rows for c in r.cells)
        if predicate(text):
            found.append((i, t, text))
    if not found:
        fail(f"не найдена таблица: {label}")
        return None
    return found[0]

def dnum(s: str) -> Decimal:
    s = s.replace(" ", "").replace(" ", "").replace(",", ".")
    m = re.search(r"[-+]?\d+(?:\.\d+)?", s)
    if not m:
        raise ValueError(s)
    return Decimal(m.group(0))

# --- Table-level checks -------------------------------------------------
mass = find_table(lambda s: "ИТОГО СТАНЦИЯ" in s and "Ферменная рама по осям" in s,
                  "сводный массовый баланс")
if mass:
    _, t, _ = mass
    vals = {}
    for r in t.rows:
        label = norm(r.cells[0].text)
        if len(r.cells) >= 3:
            vals[label] = r.cells[2].text
    expected = Decimal("26.85") + Decimal("8.13") + Decimal("1.17") + Decimal("7.55") + Decimal("3.00")
    try:
        got = dnum(vals["ИТОГО СТАНЦИЯ"])
        if got != expected:
            fail(f"массовый баланс: {got} вместо {expected}")
    except Exception as exc:
        fail(f"массовый баланс не разобран: {exc}")

materials = find_table(lambda s: "Материал" in s and "Потребность, млрд т" in s and "Вода" in s,
                       "материальный баланс")
if materials:
    ti, t, text = materials
    required = ["Разработана на концептуальном уровне в главе 8",
                "промышленный график", "квалификация оборудования",
                "полномасштабные испытания"]
    for needle in required:
        if needle not in text:
            fail(f"таблица материального баланса (таблица {ti}): нет «{needle}»")
    try:
        total = sum(dnum(r.cells[1].text) for r in t.rows[1:])
        if total != Decimal("43.55"):
            fail(f"сумма материального баланса: {total} вместо 43.55")
    except Exception as exc:
        fail(f"материальный баланс не разобран: {exc}")

equip = find_table(lambda s: "Оборудование" in s and "44,675 млн т = 0,0447 млрд т" in s,
                   "ведомость оборудования осевого рамно-ферменного комплекса")
if equip:
    ti, t, text = equip
    if "концептуальная" not in text.lower() or "квалификация оборудования" not in text:
        fail(f"таблица оборудования {ti}: не зафиксирован концептуальный статус/квалификация")
    try:
        total = sum(dnum(r.cells[3].text) for r in t.rows[1:-1])
        if total != Decimal("44.675"):
            fail(f"детализация оборудования: {total} вместо 44.675 млн т")
    except Exception as exc:
        fail(f"детализация оборудования не разобрана: {exc}")

stages = find_table(lambda s: "Этап" in s and "Содержание работ" in s and "Соединение цилиндров" in s,
                    "этапы строительства")
if stages:
    text = stages[2]
    for needle in ["неподвижных осевых соединительных ферм", "продольного соединения боковых оболочек нет"]:
        if needle not in text:
            fail(f"этапы строительства: нет «{needle}»")
    if "Монтаж внешнего соединения и подшипниковых узлов" in text:
        fail("вернулась старая формулировка внешнего/продольного соединения")

transport = find_table(lambda s: "Заселение 500 000 чел. по транспорту" in s,
                       "сводка транспортного заселения")
if transport:
    text = transport[2]
    for needle in ["15,4 суток на цилиндр", "7,7 суток на станцию", "2 700 чел./ч"]:
        if needle not in text:
            fail(f"сводка транспортного заселения: нет «{needle}»")

strength = find_table(lambda s: "18Ni(300)" in s and "Допускаемое σ" in s,
                      "таблица материалов силового пояса")
if strength and not any("запас 1,53" in norm(c.text) for t in D.tables for r in t.rows for c in r.cells):
    fail("документ не содержит канонический коэффициент запаса 1,53")

# --- Caption/image checks -----------------------------------------------
caption_nums = []
for p in D.paragraphs:
    m = re.match(r"Рисунок\s+(\d+)\s+—", norm(p.text))
    if m:
        caption_nums.append(int(m.group(1)))
if caption_nums[:23] != list(range(1, 24)) or len(caption_nums) < 46:
    fail(f"подписи рисунков: ожидался основной ряд 1..23 и перечень, получено {caption_nums}")
if len(D.inline_shapes) != 23:
    fail(f"встроенные рисунки: ожидалось 23, найдено {len(D.inline_shapes)}")

# Match the two updated embedded files to their generated source images.
with zipfile.ZipFile(DOC) as z:
    media = sorted(n for n in z.namelist() if n.startswith("word/media/") and n.lower().endswith(".png"))
    if len(media) != 23:
        fail(f"PNG в архиве DOCX: ожидалось 23, найдено {len(media)}")
    for archive_name, source_name in [("word/media/image9.png", "fig09_thermal.png"),
                                      ("word/media/image15.png", "fig16_resources.png"),
                                      ("word/media/image21.png", "fig21_volatiles.png")]:
        if archive_name not in z.namelist():
            fail(f"в архиве нет {archive_name}")
            continue
        source = FIG / source_name
        if not source.exists():
            fail(f"нет эталонного рисунка {source}")
            continue
        doc_hash = hashlib.sha256(z.read(archive_name)).hexdigest()
        src_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        if doc_hash != src_hash:
            fail(f"встроенный {archive_name} не совпадает с {source_name}")
        try:
            with Image.open(source) as im:
                if im.width < 500 or im.height < 250:
                    fail(f"слишком маленький рисунок {source_name}: {im.size}")
        except Exception as exc:
            fail(f"не читается рисунок {source_name}: {exc}")

# Text-level architecture guard.
all_text = "\n".join(norm(p.text) for p in D.paragraphs)
all_text += "\n" + "\n".join(norm(c.text) for t in D.tables for r in t.rows for c in r.cells)
for needle in ["Оборудование на боковой обшивке", "оборудование не закрепляется на вращающейся оболочке",
               "боковые оболочки между собой не соединены", "Продольной конструкции вдоль межцилиндрового зазора нет"]:
    if needle not in all_text:
        fail(f"архитектурная оговорка отсутствует: {needle}")

print("=" * 76)
print("АВТОМАТИЧЕСКАЯ СВЕРКА ТАБЛИЦ, ПОДПИСЕЙ И РИСУНКОВ")
print("=" * 76)
print(f"Документ: {DOC}")
print(f"Абзацев: {len(D.paragraphs)}; таблиц: {len(D.tables)}; рисунков: {len(D.inline_shapes)}")
if errors:
    print("ОШИБКИ:")
    for e in errors:
        print("  -", e)
    print(f"Результат: FAIL ({len(errors)} ошибок)")
    raise SystemExit(1)
print("Сводные суммы, статусы, архитектурные ограничения, подписи и встроенные рисунки согласованы.")
print("Результат: PASS")
