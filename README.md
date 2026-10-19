<p align="center">
  <img src="assets/logo.png" width="160" alt="Katana Image Converter" />
</p>

# Katana Image Converter

Локальный десктопный конвертер изображений на Python. Работает оффлайн, без рекламы, лимитов и загрузки файлов на сторонние серверы.

Переводит картинки между **PNG**, **JPEG** и **WebP**, а также умеет делать из них **ASCII-арт** в текстовый файл.

---

## Что умеет

- **Честная конвертация.** Файлы реально перекодируются через Pillow, а не просто переименовываются.
- **Прозрачность без мусора.** При конвертации PNG с альфа-каналом в JPEG прозрачные пиксели ложатся на белый фон, а не заливаются черными артефактами.
- **Настройка сжатия.** Для JPEG и WebP есть слайдер качества (от 10% до 100%).
- **ASCII-генератор.** Переводит фото в текст (`.txt`) с коррекцией пропорций символов (коэффициент 0.45) и выбором ширины строки.
- **6 темных палитр.** AMOLED (чистый черный), темно-серая, зеленая, синяя, розовая и винно-красная. Цвета приглушенные, ночью глаза не режут.
- **Звук клика.** Короткий мягкий щелчок синтезируется прямо в коде через `wave` и играет в фоне через `paplay`/`aplay`. Никаких лишних mp3/wav на диске.

---

## Поддерживаемые форматы

| Из формата | В формат | Особенности |
| :--- | :--- | :--- |
| PNG | PNG, JPEG, WebP, ASCII | Прозрачность переносится в WebP, в JPEG заменяется белым фоном |
| JPEG / JPG | PNG, JPEG, WebP, ASCII | Настройка качества сжатия (10–100%) |
| WebP | PNG, JPEG, WebP, ASCII | Полноценная поддержка Web-формата |

---

## Установка и запуск

Нужен Python 3.9 или новее.

```bash
git clone https://github.com/SpyyShaggy/image-converter.git
cd image-converter
pip install -r requirements.txt
python3 converter.py
```

Зависимости всего две: `customtkinter` для интерфейса и `Pillow` для обработки изображений.

---
<br />

# English Version

Desktop image converter for Linux and other platforms. Runs completely offline, no tracking, no file size limits, and no ads.

Converts images between **PNG**, **JPEG**, and **WebP**, or turns them into plain text **ASCII art**.

## Features

- **Real pixel conversion.** Images are re-encoded through Pillow rather than renamed.
- **Proper alpha channel handling.** Transparent PNGs converted to JPEG are placed on a clean white background instead of rendering black artifacts.
- **Compression slider.** Adjustable quality (10% to 100%) for JPEG and WebP exports.
- **ASCII art engine.** Converts images to `.txt` files with font-aspect compensation (0.45 ratio) and custom character width.
- **6 dark color schemes.** AMOLED (pure black), dark gray, green, blue, pink, and wine red. Low contrast, easy on the eyes.
- **Click feedback.** A short tactile click sound is generated directly in memory via Python's `wave` module and played through `paplay`/`aplay` in a background thread. No audio assets required.

## Installation & Usage

Requires Python 3.9+.

```bash
git clone https://github.com/SpyyShaggy/image-converter.git
cd image-converter
pip install -r requirements.txt
python3 converter.py
```

## Dependencies

- `customtkinter` (modern UI framework)
- `pillow` (image processing)
