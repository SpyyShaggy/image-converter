#!/usr/bin/env python3
"""
Image Converter — элегантный конвертер изображений
PNG / JPEG / WebP ⟷ PNG / JPEG / WebP / ASCII Art

Минималистичный интерфейс · Мягкие тёмные темы · Звуковые клики
"""

import os
import sys
import io
import math
import wave
import struct
import subprocess
import threading
import tempfile
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox
import tkinter as tk


# ═══════════════════════════════════════════════════════════════
#  Цветовые темы — все тёмные, мягкие, не выжигают глаза
# ═══════════════════════════════════════════════════════════════

THEMES = {
    "AMOLED": {
        "bg":           "#000000",
        "bg2":          "#0a0a0a",
        "card":         "#111113",
        "fg":           "#e4e4e7",
        "fg2":          "#71717a",
        "accent":       "#818cf8",
        "accent_hover": "#6366f1",
        "btn_bg":       "#18181b",
        "btn_hover":    "#27272a",
        "entry_bg":     "#09090b",
        "border":       "#27272a",
        "success":      "#34d399",
        "danger":       "#f87171",
        "slider_fg":    "#818cf8",
        "slider_bg":    "#27272a",
    },
    "Тёмная": {
        "bg":           "#1e1e2e",
        "bg2":          "#181825",
        "card":         "#262637",
        "fg":           "#cdd6f4",
        "fg2":          "#6c7086",
        "accent":       "#89b4fa",
        "accent_hover": "#74a8f7",
        "btn_bg":       "#313244",
        "btn_hover":    "#45475a",
        "entry_bg":     "#1e1e2e",
        "border":       "#45475a",
        "success":      "#a6e3a1",
        "danger":       "#f38ba8",
        "slider_fg":    "#89b4fa",
        "slider_bg":    "#45475a",
    },
    "Зелёная": {
        "bg":           "#0c1f17",
        "bg2":          "#091a12",
        "card":         "#122b1f",
        "fg":           "#d1e7dd",
        "fg2":          "#6b9080",
        "accent":       "#4ade80",
        "accent_hover": "#22c55e",
        "btn_bg":       "#1a3d2c",
        "btn_hover":    "#245038",
        "entry_bg":     "#0e2318",
        "border":       "#2d5f45",
        "success":      "#4ade80",
        "danger":       "#f87171",
        "slider_fg":    "#4ade80",
        "slider_bg":    "#2d5f45",
    },
    "Голубая": {
        "bg":           "#0c1929",
        "bg2":          "#091320",
        "card":         "#0f2035",
        "fg":           "#d1e3f7",
        "fg2":          "#6b8db5",
        "accent":       "#60a5fa",
        "accent_hover": "#3b82f6",
        "btn_bg":       "#162d4a",
        "btn_hover":    "#1e3a5f",
        "entry_bg":     "#0e1d30",
        "border":       "#2d5088",
        "success":      "#34d399",
        "danger":       "#f87171",
        "slider_fg":    "#60a5fa",
        "slider_bg":    "#2d5088",
    },
    "Розовая": {
        "bg":           "#1f0c1a",
        "bg2":          "#180914",
        "card":         "#2b1225",
        "fg":           "#f4d1e8",
        "fg2":          "#b06b95",
        "accent":       "#f472b6",
        "accent_hover": "#ec4899",
        "btn_bg":       "#3d1a33",
        "btn_hover":    "#502244",
        "entry_bg":     "#1a0e17",
        "border":       "#5f2d50",
        "success":      "#34d399",
        "danger":       "#f87171",
        "slider_fg":    "#f472b6",
        "slider_bg":    "#5f2d50",
    },
    "Красная": {
        "bg":           "#1a0c0c",
        "bg2":          "#140909",
        "card":         "#251212",
        "fg":           "#f4d1d1",
        "fg2":          "#b06b6b",
        "accent":       "#f87171",
        "accent_hover": "#ef4444",
        "btn_bg":       "#3d1a1a",
        "btn_hover":    "#502222",
        "entry_bg":     "#1a0e0e",
        "border":       "#5f2d2d",
        "success":      "#34d399",
        "danger":       "#fca5a5",
        "slider_fg":    "#f87171",
        "slider_bg":    "#5f2d2d",
    },
}


# ═══════════════════════════════════════════════════════════════
#  Генерация звука клика (мягкий «тик» без внешних файлов)
# ═══════════════════════════════════════════════════════════════

_click_wav_path = None


def _generate_click_wav():
    """Генерирует короткий мягкий щелчок в WAV и сохраняет во временный файл."""
    global _click_wav_path
    if _click_wav_path and os.path.isfile(_click_wav_path):
        return _click_wav_path

    sample_rate = 22050
    duration = 0.035  # 35 мс
    freq = 900
    n = int(sample_rate * duration)

    samples = []
    for i in range(n):
        t = i / sample_rate
        amp = math.exp(-t * 120) * 0.4
        val = amp * math.sin(2 * math.pi * freq * t)
        samples.append(int(val * 32767))

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))

    tmp = os.path.join(tempfile.gettempdir(), "imgconv_click.wav")
    with open(tmp, "wb") as f:
        f.write(buf.getvalue())
    _click_wav_path = tmp
    return tmp


def play_click():
    """Воспроизводит звук клика в фоне через PulseAudio / ALSA."""
    def _play():
        wav = _generate_click_wav()
        for cmd in ("paplay", "aplay"):
            try:
                subprocess.run(
                    [cmd, wav],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=2,
                )
                return
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
    threading.Thread(target=_play, daemon=True).start()


# ═══════════════════════════════════════════════════════════════
#  Логика конвертации
# ═══════════════════════════════════════════════════════════════

SUPPORTED_IN = (".png", ".jpg", ".jpeg", ".webp")
SUPPORTED_OUT = ("PNG", "JPEG", "WEBP", "ASCII")

ASCII_CHARS = " .·:;!=+*#%@"


def convert_image(input_path, output_format, quality=90, ascii_width=120, save_path=None):
    """
    Конвертирует изображение в указанный формат.
    Возвращает путь к сохранённому файлу.
    """
    img = Image.open(input_path)
    stem = Path(input_path).stem

    if output_format == "ASCII":
        ascii_text = _image_to_ascii(img, ascii_width)
        if not save_path:
            save_path = str(Path(input_path).with_suffix(".txt"))
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(ascii_text)
        return save_path

    # Обработка альфа-канала для JPEG (не поддерживает прозрачность)
    if output_format == "JPEG" and img.mode in ("RGBA", "LA", "PA", "P"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        if img.mode in ("RGBA", "LA", "PA"):
            background.paste(img, mask=img.split()[-1])
        img = background
    elif img.mode not in ("RGB", "RGBA", "L"):
        img = img.convert("RGBA" if output_format in ("PNG", "WEBP") else "RGB")

    ext_map = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp"}
    ext = ext_map[output_format]

    if not save_path:
        save_path = str(Path(input_path).with_suffix(ext))

    save_kwargs = {}
    if output_format == "JPEG":
        if img.mode != "RGB":
            img = img.convert("RGB")
        save_kwargs["quality"] = quality
        save_kwargs["optimize"] = True
    elif output_format == "WEBP":
        save_kwargs["quality"] = quality
        save_kwargs["method"] = 4
    elif output_format == "PNG":
        save_kwargs["optimize"] = True

    img.save(save_path, output_format, **save_kwargs)
    return save_path


def _image_to_ascii(img, width=120):
    """Преобразует PIL Image в ASCII-арт строку."""
    img = img.convert("L")
    w, h = img.size
    aspect = h / w
    new_h = int(width * aspect * 0.45)
    img = img.resize((width, new_h), Image.Resampling.LANCZOS)

    pixels = img.getdata()
    n_chars = len(ASCII_CHARS)
    lines = []
    for row in range(new_h):
        line = ""
        for col in range(width):
            px = pixels[row * width + col]
            idx = px * (n_chars - 1) // 255
            line += ASCII_CHARS[idx]
        lines.append(line.rstrip())
    return "\n".join(lines)


def get_image_info(path):
    """Возвращает словарь с информацией об изображении."""
    try:
        img = Image.open(path)
        w, h = img.size
        fmt = img.format or Path(path).suffix[1:].upper()
        mode = img.mode
        size_bytes = os.path.getsize(path)
        return {
            "width": w,
            "height": h,
            "format": fmt,
            "mode": mode,
            "size": size_bytes,
            "size_str": _fmt_size(size_bytes),
        }
    except Exception:
        return None


def _fmt_size(n):
    for unit in ("Б", "КБ", "МБ", "ГБ"):
        if n < 1024:
            return f"{n:.1f} {unit}" if n != int(n) else f"{int(n)} {unit}"
        n /= 1024
    return f"{n:.1f} ТБ"


# ═══════════════════════════════════════════════════════════════
#  GUI-приложение
# ═══════════════════════════════════════════════════════════════

class ImageConverterApp(ctk.CTk):
    """Основное окно конвертера изображений."""

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Image Converter")
        self.geometry("580x780")
        self.minsize(480, 640)
        self.resizable(True, True)

        self.current_file = None
        self.preview_photo = None
        self.theme_name = "AMOLED"
        self.c = THEMES[self.theme_name]

        # Предварительно генерируем звук клика
        threading.Thread(target=_generate_click_wav, daemon=True).start()

        self._build_ui()
        self._apply_theme()

    # ─── Построение UI ──────────────────────────────────────

    def _build_ui(self):
        # Контейнер-скролл
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        # ── Заголовок ──
        self.header = ctk.CTkFrame(self.main_frame, corner_radius=0, height=54)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        self.title_label = ctk.CTkLabel(
            self.header, text="✦  Image Converter",
            font=ctk.CTkFont(family="Inter", size=17, weight="bold"),
        )
        self.title_label.pack(side="left", padx=18, pady=12)

        self.theme_menu = ctk.CTkOptionMenu(
            self.header,
            values=list(THEMES.keys()),
            command=self._on_theme_change,
            width=130,
            height=30,
            font=ctk.CTkFont(size=12),
            dropdown_font=ctk.CTkFont(size=12),
        )
        self.theme_menu.set(self.theme_name)
        self.theme_menu.pack(side="right", padx=18, pady=12)

        theme_icon = ctk.CTkLabel(
            self.header, text="🎨",
            font=ctk.CTkFont(size=14),
        )
        theme_icon.pack(side="right")

        # ── Основной контент ──
        self.content = ctk.CTkFrame(self.main_frame, corner_radius=0)
        self.content.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        # --- Зона предпросмотра (кликабельная для выбора файла) ---
        self.preview_card = ctk.CTkFrame(self.content, corner_radius=14, height=260)
        self.preview_card.pack(fill="x", pady=(10, 6))
        self.preview_card.pack_propagate(False)

        self.preview_inner = ctk.CTkFrame(self.preview_card, corner_radius=12)
        self.preview_inner.pack(fill="both", expand=True, padx=3, pady=3)

        self.preview_label = ctk.CTkLabel(
            self.preview_inner,
            text="🖼\n\nКликните для выбора\nизображения",
            font=ctk.CTkFont(size=14),
            cursor="hand2",
        )
        self.preview_label.pack(fill="both", expand=True)
        self.preview_label.bind("<Button-1>", lambda e: self._click_and(self._select_file))

        # --- Инфо о файле ---
        self.info_label = ctk.CTkLabel(
            self.content, text="Файл не выбран",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self.info_label.pack(fill="x", padx=4, pady=(4, 10))

        # --- Кнопка выбора файла ---
        self.select_btn = ctk.CTkButton(
            self.content,
            text="📁  Выбрать файл…",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38,
            corner_radius=10,
            command=lambda: self._click_and(self._select_file),
        )
        self.select_btn.pack(fill="x", padx=4, pady=(0, 14))

        # ── Разделитель ──
        self.sep1 = ctk.CTkFrame(self.content, height=1, corner_radius=0)
        self.sep1.pack(fill="x", padx=4, pady=(0, 14))

        # --- Формат вывода ---
        fmt_header = ctk.CTkLabel(
            self.content, text="Формат",
            font=ctk.CTkFont(size=11),
            anchor="w",
        )
        fmt_header.pack(fill="x", padx=4, pady=(0, 4))
        self.fmt_header_lbl = fmt_header

        self.format_var = tk.StringVar(value="PNG")
        self.fmt_frame = ctk.CTkFrame(self.content, corner_radius=10)
        self.fmt_frame.pack(fill="x", padx=4, pady=(0, 14))

        self.fmt_buttons = {}
        for fmt in SUPPORTED_OUT:
            btn = ctk.CTkButton(
                self.fmt_frame,
                text=fmt,
                width=0,
                height=36,
                corner_radius=8,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda f=fmt: self._click_and(lambda: self._set_format(f)),
            )
            btn.pack(side="left", fill="x", expand=True, padx=2, pady=4)
            self.fmt_buttons[fmt] = btn

        # --- Качество (для JPEG / WEBP) ---
        self.quality_frame = ctk.CTkFrame(self.content, corner_radius=10)
        self.quality_frame.pack(fill="x", padx=4, pady=(0, 10))

        self.quality_label = ctk.CTkLabel(
            self.quality_frame, text="Качество",
            font=ctk.CTkFont(size=11),
            anchor="w",
        )
        self.quality_label.pack(fill="x", padx=12, pady=(8, 0))

        slider_row = ctk.CTkFrame(self.quality_frame, fg_color="transparent")
        slider_row.pack(fill="x", padx=12, pady=(4, 8))

        self.quality_slider = ctk.CTkSlider(
            slider_row,
            from_=10, to=100,
            number_of_steps=18,
            command=self._on_quality_change,
        )
        self.quality_slider.set(90)
        self.quality_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.quality_value_lbl = ctk.CTkLabel(
            slider_row, text="90%",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=44,
        )
        self.quality_value_lbl.pack(side="right")

        # --- Ширина ASCII ---
        self.ascii_frame = ctk.CTkFrame(self.content, corner_radius=10)
        self.ascii_frame.pack(fill="x", padx=4, pady=(0, 14))

        self.ascii_label = ctk.CTkLabel(
            self.ascii_frame, text="Ширина ASCII (символов)",
            font=ctk.CTkFont(size=11),
            anchor="w",
        )
        self.ascii_label.pack(fill="x", padx=12, pady=(8, 4))

        self.ascii_width_entry = ctk.CTkEntry(
            self.ascii_frame,
            placeholder_text="120",
            font=ctk.CTkFont(size=13),
            height=34,
            corner_radius=8,
        )
        self.ascii_width_entry.insert(0, "120")
        self.ascii_width_entry.pack(fill="x", padx=12, pady=(0, 8))

        # --- Скрыть ASCII по умолчанию ---
        self.ascii_frame.pack_forget()

        # ── Разделитель ──
        self.sep2 = ctk.CTkFrame(self.content, height=1, corner_radius=0)
        self.sep2.pack(fill="x", padx=4, pady=(0, 14))

        # --- Кнопка конвертации ---
        self.convert_btn = ctk.CTkButton(
            self.content,
            text="✨  Конвертировать",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=46,
            corner_radius=12,
            command=lambda: self._click_and(self._convert),
        )
        self.convert_btn.pack(fill="x", padx=4, pady=(0, 10))

        # --- Статусная строка ---
        self.status_label = ctk.CTkLabel(
            self.content, text="",
            font=ctk.CTkFont(size=11),
            anchor="w",
        )
        self.status_label.pack(fill="x", padx=4, pady=(0, 4))

        # Обновляем состояние UI
        self._update_format_buttons()

    # ─── Обработчики событий ────────────────────────────────

    def _click_and(self, fn):
        """Воспроизводит клик и вызывает fn."""
        play_click()
        self.after(30, fn)

    def _on_theme_change(self, name):
        play_click()
        if name in THEMES:
            self.theme_name = name
            self.c = THEMES[name]
            self._apply_theme()

    def _on_quality_change(self, val):
        self.quality_value_lbl.configure(text=f"{int(val)}%")

    def _set_format(self, fmt):
        self.format_var.set(fmt)
        self._update_format_buttons()

        # Показать / скрыть настройки качества и ASCII
        if fmt in ("JPEG", "WEBP"):
            self.quality_frame.pack(fill="x", padx=4, pady=(0, 10),
                                    after=self.fmt_frame)
            self.ascii_frame.pack_forget()
        elif fmt == "ASCII":
            self.quality_frame.pack_forget()
            self.ascii_frame.pack(fill="x", padx=4, pady=(0, 14),
                                  after=self.fmt_frame)
        else:  # PNG
            self.quality_frame.pack_forget()
            self.ascii_frame.pack_forget()

    def _update_format_buttons(self):
        """Подсвечивает активную кнопку формата."""
        active = self.format_var.get()
        c = self.c
        for fmt, btn in self.fmt_buttons.items():
            if fmt == active:
                btn.configure(
                    fg_color=c["accent"],
                    hover_color=c["accent_hover"],
                    text_color="#ffffff",
                )
            else:
                btn.configure(
                    fg_color=c["btn_bg"],
                    hover_color=c["btn_hover"],
                    text_color=c["fg2"],
                )

    def _select_file(self):
        """Открывает диалог выбора файла."""
        path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Изображения", "*.png *.jpg *.jpeg *.webp"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("WebP", "*.webp"),
                ("Все файлы", "*.*"),
            ],
        )
        if path and os.path.isfile(path):
            self.current_file = path
            self._update_preview()
            self.status_label.configure(text="", text_color=self.c["fg2"])

    def _update_preview(self):
        """Обновляет предпросмотр и информацию о файле."""
        if not self.current_file:
            return

        info = get_image_info(self.current_file)
        if not info:
            self.info_label.configure(text="⚠ Ошибка чтения файла")
            return

        # Информация
        name = os.path.basename(self.current_file)
        if len(name) > 40:
            name = name[:18] + "…" + name[-18:]
        self.info_label.configure(
            text=f"📄  {name}   ·   {info['width']}×{info['height']}   ·   {info['format']}   ·   {info['size_str']}",
            text_color=self.c["fg"],
        )

        # Превью
        try:
            img = Image.open(self.current_file)
            # Размер контейнера превью
            pw, ph = 540, 240
            img.thumbnail((pw, ph), Image.Resampling.LANCZOS)

            # Compositing for RGBA images
            if img.mode == "RGBA":
                checker = Image.new("RGB", img.size, (30, 30, 30))
                checker.paste(img, mask=img.split()[-1])
                img = checker
            elif img.mode != "RGB":
                img = img.convert("RGB")

            self.preview_photo = ctk.CTkImage(
                light_image=img, dark_image=img,
                size=(img.width, img.height),
            )
            self.preview_label.configure(
                text="",
                image=self.preview_photo,
            )
        except Exception as e:
            self.preview_label.configure(
                text=f"⚠ Ошибка превью:\n{e}",
                image=None,
            )

    def _convert(self):
        """Запускает конвертацию выбранного файла."""
        if not self.current_file or not os.path.isfile(self.current_file):
            messagebox.showwarning("Нет файла", "Сначала выберите изображение для конвертации.")
            return

        out_fmt = self.format_var.get()
        quality = int(self.quality_slider.get())

        ascii_w = 120
        if out_fmt == "ASCII":
            try:
                ascii_w = int(self.ascii_width_entry.get())
                if ascii_w < 20:
                    ascii_w = 20
                if ascii_w > 400:
                    ascii_w = 400
            except ValueError:
                ascii_w = 120

        # Определяем расширение и предлагаем путь
        ext_map = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp", "ASCII": ".txt"}
        default_ext = ext_map[out_fmt]
        default_name = Path(self.current_file).stem + f"_converted{default_ext}"
        default_dir = os.path.dirname(self.current_file)

        ftypes = {
            "PNG": [("PNG", "*.png")],
            "JPEG": [("JPEG", "*.jpg *.jpeg")],
            "WEBP": [("WebP", "*.webp")],
            "ASCII": [("Текст", "*.txt")],
        }

        save_path = filedialog.asksaveasfilename(
            title="Сохранить как",
            initialdir=default_dir,
            initialfile=default_name,
            defaultextension=default_ext,
            filetypes=ftypes.get(out_fmt, [("Все", "*.*")]),
        )

        if not save_path:
            return

        self.status_label.configure(text="⏳ Конвертация…", text_color=self.c["accent"])
        self.convert_btn.configure(state="disabled")
        self.update_idletasks()

        def worker():
            try:
                result = convert_image(
                    self.current_file, out_fmt,
                    quality=quality,
                    ascii_width=ascii_w,
                    save_path=save_path,
                )
                out_size = _fmt_size(os.path.getsize(result))
                self.after(0, lambda: self._on_convert_done(result, out_size))
            except Exception as e:
                self.after(0, lambda: self._on_convert_error(str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _on_convert_done(self, path, size_str):
        self.convert_btn.configure(state="normal")
        name = os.path.basename(path)
        self.status_label.configure(
            text=f"✓  Сохранено: {name}  ({size_str})",
            text_color=self.c["success"],
        )
        play_click()

    def _on_convert_error(self, err):
        self.convert_btn.configure(state="normal")
        self.status_label.configure(
            text=f"✗  Ошибка: {err}",
            text_color=self.c["danger"],
        )

    # ─── Применение темы ────────────────────────────────────

    def _apply_theme(self):
        """Применяет текущую цветовую схему ко всем виджетам."""
        c = self.c

        # Корневое окно
        self.configure(fg_color=c["bg"])

        # Основной фрейм
        self.main_frame.configure(fg_color=c["bg"])

        # Заголовок
        self.header.configure(fg_color=c["bg2"])
        self.title_label.configure(text_color=c["fg"])

        # Тема-меню
        self.theme_menu.configure(
            fg_color=c["btn_bg"],
            button_color=c["accent"],
            button_hover_color=c["accent_hover"],
            text_color=c["fg"],
            dropdown_fg_color=c["card"],
            dropdown_text_color=c["fg"],
            dropdown_hover_color=c["btn_hover"],
        )

        # Контент
        self.content.configure(fg_color=c["bg"])

        # Карточка превью
        self.preview_card.configure(fg_color=c["border"])
        self.preview_inner.configure(fg_color=c["card"])
        self.preview_label.configure(
            text_color=c["fg2"],
            fg_color=c["card"],
        )

        # Инфо
        self.info_label.configure(text_color=c["fg2"])

        # Кнопка выбора
        self.select_btn.configure(
            fg_color=c["btn_bg"],
            hover_color=c["btn_hover"],
            text_color=c["fg"],
            border_color=c["border"],
            border_width=1,
        )

        # Разделители
        self.sep1.configure(fg_color=c["border"])
        self.sep2.configure(fg_color=c["border"])

        # Метка формата
        self.fmt_header_lbl.configure(text_color=c["fg2"])

        # Фрейм формата
        self.fmt_frame.configure(fg_color=c["card"])

        # Кнопки формата — обновляются отдельно
        self._update_format_buttons()

        # Качество
        self.quality_frame.configure(fg_color=c["card"])
        self.quality_label.configure(text_color=c["fg2"])
        self.quality_slider.configure(
            fg_color=c["slider_bg"],
            progress_color=c["slider_fg"],
            button_color=c["accent"],
            button_hover_color=c["accent_hover"],
        )
        self.quality_value_lbl.configure(text_color=c["fg"])

        # ASCII
        self.ascii_frame.configure(fg_color=c["card"])
        self.ascii_label.configure(text_color=c["fg2"])
        self.ascii_width_entry.configure(
            fg_color=c["entry_bg"],
            text_color=c["fg"],
            border_color=c["border"],
            placeholder_text_color=c["fg2"],
        )

        # Кнопка конвертации
        self.convert_btn.configure(
            fg_color=c["accent"],
            hover_color=c["accent_hover"],
            text_color="#ffffff",
        )

        # Статус
        self.status_label.configure(text_color=c["fg2"])


# ═══════════════════════════════════════════════════════════════
#  Точка входа
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = ImageConverterApp()
    app.mainloop()
