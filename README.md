# ММОСО’Н / MMOSON

## Русская версия

**Модуль моделирования орбитальной станции О’Нилла**

Расчётная модель обитаемой орбитальной станции цилиндрического типа для точки L1 системы Земля — Солнце.

ММОСО’Н — личный инженерный и научно-исследовательский проект автора.

### Основные параметры

| Величина | Значение |
|---|---|
| Радиус цилиндра | 5 000 м |
| Длина цилиндрической части | 40 км (полная 49 км) |
| Число цилиндров | 2, встречного вращения |
| Угловая скорость | 0,04429 рад/с — 0,423 об/мин |
| Тяжесть на ободе | 1,0 g |
| Материал оболочки | сталь 18Ni(300), пояс 850 мм |
| Полная площадь | 3 100,2 км² (1 550,1 на цилиндр) |
| Масса станции | 46,70 млрд т |
| Население | 1 000 000 человек |
| Электрическая мощность | 721,4 ГВт |
| Место размещения | точка L1 Земля — Солнце |

Освещение — только реакторное, через осевые светотепловые балки. Зеркал и солнечного паруса у станции нет.

### Состав проекта

| Файл | Содержание |
|---|---|
| `MMOSON_russian_publication.docx` | основной документ научной публикации на русском языке |
| `MMOSON_english_publication.docx` | основной документ научной публикации на английском языке |
| `draw/` | исходники чертежей ЕСКД |
| `src/` | генераторы документа и расчётная верификация |
| `resource_map.png`, `resource_map.pdf` | ресурсная карта программы |
| `MMOSON_drawings.pdf` | обновлённый альбом из 7 чертёжных листов |
| `fig/`, `draw/` | рисунки, исходники чертежей и генераторы |

### Проверка расчётов

```bash
cd src
python3 verify_all.py
python3 crosscheck.py ../MMOSON_russian_publication.docx
python3 audit_tables_figures_v7.py ../MMOSON_russian_publication.docx
```

`verify_all.py` пересчитывает величины независимо. `crosscheck.py` сверяет активный текст, таблицы и канонические параметры. `audit_tables_figures_v7.py` проверяет таблицы, рисунки, статусы и архитектурные ограничения.

### Автор

**Бугаенко Роман Сергеевич** — независимый автор и руководитель личного инженерного и научно-исследовательского проекта ММОСО’Н.

В рамках проекта автор занимается концепцией и архитектурой станции, климатическим зонированием, составом биоценозов, инженерными решениями, продовольственным и водным балансами.

**НИК** (Нить искренности в Континууме) — расчётная верификация, пересчёт прочности и балансов, оформление документа и чертежей.

### Лицензия

Проект распространяется по проприетарному уведомлению **«Все права защищены / All rights reserved»**. Свободное чтение и ознакомление разрешены. Любое иное использование, копирование, распространение, перевод, переработка, публикация или включение материалов в другие проекты требует предварительного письменного согласия автора. Полные двуязычные условия находятся в `LICENCE.txt` и в обоих основных документах.

---

## English version

**Modeling Module for an O’Neill Orbital Station**

A calculation model of a cylindrical inhabited orbital station intended for the Earth–Sun L1 point.

MMOSON is the author’s personal engineering and research project.

### Main parameters

| Parameter | Value |
|---|---|
| Cylinder radius | 5,000 m |
| Cylindrical section length | 40 km (49 km overall) |
| Number of cylinders | 2, counter-rotating |
| Angular velocity | 0.04429 rad/s — 0.423 rpm |
| Rim gravity | 1.0 g |
| Shell material | 18Ni(300) steel, 850 mm belt |
| Total area | 3,100.2 km² (1,550.1 per cylinder) |
| Station mass | 46.70 billion tonnes |
| Population | 1,000,000 people |
| Electrical power | 721.4 GW |
| Location | Earth–Sun L1 point |

Lighting is provided only by reactors through axial light-and-thermal beams. The station has no mirrors and no solar sail.

### Project contents

| File | Contents |
|---|---|
| `MMOSON_russian_publication.docx` | main scientific-publication document in Russian |
| `MMOSON_english_publication.docx` | main scientific-publication document in English |
| `draw/` | source files for ESKD drawings |
| `src/` | document generators and calculation verification |
| `resource_map.png`, `resource_map.pdf` | program resource map |
| `MMOSON_drawings.pdf` | updated album of 7 technical drawing sheets |
| `fig/`, `draw/` | figures, drawing sources and generators |

### Calculation checks

```bash
cd src
python3 verify_all.py
python3 crosscheck.py ../MMOSON_russian_publication.docx
python3 audit_tables_figures_v7.py ../MMOSON_russian_publication.docx
```

`verify_all.py` independently recalculates the values. `crosscheck.py` checks the active text, tables and canonical parameters. `audit_tables_figures_v7.py` checks tables, figures, status labels and architectural constraints.

### Author

**Roman Sergeevich Bugaenko** is an independent author and the lead of the personal MMOSON engineering and research project.

Within MMOSON, the author works on the station concept and architecture, climate zoning, biocenosis composition, engineering solutions, and food and water balances.

**NIK** (*Thread of Sincerity in the Continuum*) performs calculation verification, strength and balance recalculation, and document and drawing preparation.

### Licence

The project is distributed under a proprietary **“All rights reserved / Все права защищены”** notice. Public reading and review are permitted. Any other use, copying, distribution, translation, adaptation, publication or incorporation of materials into other projects requires the author’s prior written permission. The complete bilingual terms are provided in `LICENCE.txt` and in both main documents.

---

## Project status / Статус проекта

This is a conceptual research publication, not a flight-ready design or an approved operational construction package. / Это концептуальная научно-исследовательская публикация, а не готовый к полёту проект и не утверждённая рабочая конструкторская документация.
