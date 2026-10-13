import threading
import requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime


class CurrencyApp:
    COLORS = {
        "bg_main": "#d8dcd6",
        "bg_panel": "#f9fcff",
        "text": "#333333",
        "accent": "#6495ed",
        "status_ok": "#2e7d32",
        "status_load": "#4a90e2",
        "entry_bg": "#ffffff",
        "label_bg": "#f0f4f8",
        "border": "#dcdcdc",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Курсы: Крипта и Валюта")
        self.root.geometry("720x440")
        self.root.configure(bg=self.COLORS["bg_main"])

        self.CRYPTOS = {
            "bitcoin": "Bitcoin (BTC)",
            "ethereum": "Ethereum (ETH)",
            "solana": "Solana (SOL)",
            "ripple": "XRP (XRP)",
            "cardano": "Cardano (ADA)",
            "dogecoin": "Dogecoin (DOGE)",
            "polkadot": "Polkadot (DOT)"
        }

        self.FIAT_CURRENCIES = {
            "USD": "Доллар США",
            "EUR": "Евро",
            "RUB": "Российский рубль",
            "CNY": "Китайский юань",
            "JPY": "Японская йена",
            "GBP": "Британский фунт",
            "AUD": "Австралийский доллар",
            "CAD": "Канадский доллар",
        }

        self.CRYPTO_CONVERT_TO = {
            "RUB": "Российский рубль",
            "USD": "Доллар США",
            "EUR": "Евро",
            "USDT": "Tether (USDT)",
            "BNB": "Binance Coin (BNB)",
            "DOGE": "Dogecoin (DOGE)"
        }

        self.API_FIAT = "https://open.er-api.com/v6/latest/"
        self.API_CRYPTO_PRICE = "https://api.coingecko.com/api/v3/simple/price"

        self._last_results = []

        self._setup_styles()
        self._create_menu()
        self._create_top_row()
        self._create_controls()
        self._create_table()

    # Стили
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=self.COLORS["bg_main"])
        style.configure("TLabel", background=self.COLORS["label_bg"], foreground=self.COLORS["text"])
        style.configure("TEntry", fieldbackground=self.COLORS["entry_bg"], foreground=self.COLORS["text"], padding=4)

        style.configure("Treeview", rowheight=32, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        style.map("Treeview", background=[("selected", self.COLORS["accent"])])


        style.configure("Accent.TButton",
                        background=self.COLORS["accent"],
                        foreground="white",
                        font=("Arial", 11, "bold"),
                        borderwidth=1,
                        focuscolor="none")

        # Состояния кнопки: активная (нажатие) и заблокированная
        style.map("Accent.TButton",
                  background=[("active", "#4a77b8"), ("disabled", "#a5c9f0")])


        style.configure("BlueGray.TButton", background="#8c9ebc", foreground="black", font=("Arial", 11), borderwidth=1,
                        focuscolor="none")
        style.map("BlueGray.TButton", background=[("active", "#7a8fb0"), ("disabled", "#dcdcdc")])

    #  Меню
    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Меню", menu=file_menu)
        file_menu.add_separator()
        file_menu.add_command(label="О программе", command=self.show_about)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.on_exit)

    #  Валидация ввода
    def _validate_number(self, value):
        if value == "" or value is None:
            return True
        raw = value.replace(",", ".")
        if raw.count(".") > 1:
            return False
        stripped = raw.replace(".", "", 1)
        return stripped.isdigit() or stripped == ""

    #  Верхняя строка: два блока рядом
    def _create_top_row(self):
        top_frame = tk.Frame(self.root, bg=self.COLORS["bg_main"])
        top_frame.pack(fill="x", padx=12, pady=12)

        crypto_frame = self._make_section_block(top_frame, "<<< Крипто-Монеты >>>")
        crypto_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self._create_crypto_inputs(crypto_frame)

        currency_frame = self._make_section_block(top_frame, "<<< Валюты-Стандартные >>>")
        currency_frame.pack(side="right", fill="both", expand=True, padx=(8, 0))
        self._create_currency_inputs(currency_frame)

    def _make_section_block(self, parent, title):
        frame = tk.Frame(parent, bg=self.COLORS["bg_panel"], highlightbackground=self.COLORS["border"],
                         highlightthickness=1)
        lbl_title = tk.Label(frame, text=title, font=("Arial", 12, "bold"), bg=self.COLORS["bg_panel"],
                             fg=self.COLORS["text"])
        lbl_title.pack(pady=(10, 5))
        return frame

    #  Ввод: Криптовалюта
    def _create_crypto_inputs(self, frame):
        tk.Label(frame, text="Выберите монету", font=("Arial", 10), bg=self.COLORS["bg_panel"],
                 fg=self.COLORS["text"]).pack(anchor="w", pady=(8, 0))

        self.crypto_combo = ttk.Combobox(frame, values=list(self.CRYPTOS.keys()), state="readonly")
        self.crypto_combo.pack(fill="x", pady=2)
        self.crypto_combo.current(0)

        tk.Label(frame, text="Сколько посчитать (шт.)", font=("Arial", 10), bg=self.COLORS["bg_panel"],
                 fg=self.COLORS["text"]).pack(anchor="w", pady=(8, 0))

        vcmd = (self.root.register(self._validate_number), "%P")
        self.crypto_qty_entry = ttk.Entry(frame, validate="key", validatecommand=vcmd)
        self.crypto_qty_entry.pack(fill="x", pady=2)

        tk.Label(frame, text="Конвертировать в", font=("Arial", 10), bg=self.COLORS["bg_panel"],
                 fg=self.COLORS["text"]).pack(anchor="w", pady=(8, 0))

        self.crypto_convert_combo = ttk.Combobox(frame, values=list(self.CRYPTO_CONVERT_TO.keys()), state="readonly")
        self.crypto_convert_combo.pack(fill="x", pady=2)
        self.crypto_convert_combo.current(list(self.CRYPTO_CONVERT_TO.keys()).index("RUB"))

    #  Ввод: Валюты
    def _create_currency_inputs(self, frame):
        tk.Label(frame, text="Базовая валюта", font=("Arial", 10), bg=self.COLORS["bg_panel"],
                 fg=self.COLORS["text"]).pack(anchor="w", pady=(8, 0))

        self.base_curr_combo = ttk.Combobox(frame, values=list(self.FIAT_CURRENCIES.keys()), state="readonly")
        self.base_curr_combo.pack(fill="x", pady=2)
        self.base_curr_combo.current(list(self.FIAT_CURRENCIES.keys()).index("USD"))

        tk.Label(frame, text="Целевая валюта", font=("Arial", 10), bg=self.COLORS["bg_panel"],
                 fg=self.COLORS["text"]).pack(anchor="w", pady=(8, 0))

        self.target_curr_combo = ttk.Combobox(frame, values=list(self.FIAT_CURRENCIES.keys()), state="readonly")
        self.target_curr_combo.pack(fill="x", pady=2)
        self.target_curr_combo.current(list(self.FIAT_CURRENCIES.keys()).index("RUB"))

        tk.Label(frame, text="Сколько посчитать", font=("Arial", 10), bg=self.COLORS["bg_panel"],
                 fg=self.COLORS["text"]).pack(anchor="w", pady=(8, 0))

        vcmd = (self.root.register(self._validate_number), "%P")
        self.curr_qty_entry = ttk.Entry(frame, validate="key", validatecommand=vcmd)
        self.curr_qty_entry.pack(fill="x", pady=2)

    #  Кнопки и статус
    def _create_controls(self):
        btn_frame = tk.Frame(self.root, bg=self.COLORS["bg_main"])
        btn_frame.pack(pady=12)

        # Все кнопки теперь используют единый стиль
        self.refresh_btn = ttk.Button(btn_frame, text="Показать", command=self.on_refresh, style="Accent.TButton")
        self.refresh_btn.pack(side="left", padx=(0, 14))

        self.status_label = tk.Label(btn_frame, text="Нажмите «Показать»", background=self.COLORS["bg_panel"],
                                     foreground=self.COLORS["text"], font=("Arial", 10), relief="flat", anchor="center",
                                     padx=10, pady=6)
        self.status_label.pack(side="left", fill="x", expand=True)

        self.clear_btn = ttk.Button(btn_frame, text="Очистить", command=self.clear_all, style="Accent.TButton")
        self.clear_btn.pack(side="right", padx=(7, 0))

        self.save_btn = ttk.Button(btn_frame, text="Сохранить", command=self.save_results, style="Accent.TButton")
        self.save_btn.pack(side="right", padx=(0, 7))

    #  Таблица
    def _create_table(self):
        self.tree = ttk.Treeview(self.root, columns=("type", "name", "value"), show="headings", height=8)
        self.tree.heading("type", text="Тип")
        self.tree.heading("name", text="Показатель / Пара")
        self.tree.heading("value", text="Значение")

        self.tree.column("type", width=20, anchor="center")
        self.tree.column("name", width=260, anchor="w")
        self.tree.column("value", width=170, anchor="e")

        self.tree.tag_configure("green_row", background="#e8f5e9")
        self.tree.tag_configure("blue_row", background="#b3e5fc")

        self.tree.pack(padx=12, pady=8, fill="both", expand=True)

    #  О программе
    def show_about(self):
        messagebox.showinfo("О программе",
                            "Курсы: Крипта и Валюта\nВерсия: 1.0\n\nИспользуемые API:\n- open.er-api.com — курсы валют\n- coingecko.com — крипто-монеты")

    #  Выход
    def on_exit(self):
        if messagebox.askyesno("Выход", "Вы действительно хотите закрыть программу?"):
            self.root.quit()
            self.root.destroy()

    #  Очистить все поля
    def clear_all(self):
        self.crypto_qty_entry.delete(0, tk.END)
        self.curr_qty_entry.delete(0, tk.END)
        self.crypto_combo.current(0)
        self.crypto_convert_combo.current(list(self.CRYPTO_CONVERT_TO.keys()).index("RUB"))
        self.base_curr_combo.current(list(self.FIAT_CURRENCIES.keys()).index("USD"))
        self.target_curr_combo.current(list(self.FIAT_CURRENCIES.keys()).index("RUB"))
        self.tree.delete(*self.tree.get_children())
        self._last_results = []
        self.set_status("Поля очищены", self.COLORS["bg_panel"])

    #  Сохранение результатов в CSV
    def save_results(self):
        if not self._last_results:
            messagebox.showwarning("Сохранение", "Нет данных для сохранения. Нажмите «Показать».")
            return

        default_name = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                                initialfile=default_name)
        if not filepath:
            return

        try:
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Тип", "Показатель / Пара", "Значение"])
                for row in self._last_results:
                    writer.writerow(row)
            self.set_status("Результаты сохранены", self.COLORS["status_ok"])
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    #  Статус-бар
    def set_status(self, text, color):
        self.status_label.config(text=text, background=color, foreground="white")

    #  Запрос данных
    def fetch_all(self):
        crypto_id = self.crypto_combo.get().strip().lower()
        crypto_qty_str = self.crypto_qty_entry.get().strip().replace(",", ".")
        crypto_convert_to = self.crypto_convert_combo.get().strip().upper()

        base_curr = self.base_curr_combo.get().strip().upper()
        target_curr = self.target_curr_combo.get().strip().upper()
        curr_qty_str = self.curr_qty_entry.get().strip().replace(",", ".")

        results = []

        #  Крипта
        if crypto_id:
            try:
                # Получаю цену выбранной монеты в долларах
                params = {"ids": crypto_id, "vs_currencies": "usd"}
                resp = requests.get(self.API_CRYPTO_PRICE, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                coin_data = data.get(crypto_id)

                if coin_data:
                    price_usd = coin_data.get("usd", None)
                    name_display = self.CRYPTOS.get(crypto_id, crypto_id.capitalize())

                    converted_value = None
                    display_currency = self.CRYPTO_CONVERT_TO.get(crypto_convert_to, crypto_convert_to)

                    if price_usd is not None:
                        qty = None
                        if crypto_qty_str:
                            try:
                                qty = float(crypto_qty_str)
                            except ValueError:
                                pass

                        # Конвертация в зависимости от выбранной целевой монеты
                        if crypto_convert_to in ["RUB", "USD", "EUR"]:
                            resp_rates = requests.get(self.API_FIAT + "USD", timeout=10)
                            resp_rates.raise_for_status()
                            rates_data = resp_rates.json()
                            rates = rates_data.get("rates", {})
                            rate_to_target = rates.get(crypto_convert_to, None)
                            if rate_to_target is not None:
                                converted_value = price_usd * rate_to_target
                        elif crypto_convert_to == "USDT":
                            # Tether привязан к доллару 1:1
                            converted_value = price_usd
                        elif crypto_convert_to in ["BNB", "DOGE"]:
                            # Конвертация в другую крипту: цена целевой крипты в USD
                            params_target = {"ids": crypto_convert_to.lower(), "vs_currencies": "usd"}
                            resp_target = requests.get(self.API_CRYPTO_PRICE, params=params_target, timeout=10)
                            resp_target.raise_for_status()
                            target_data = resp_target.json()
                            target_price_usd = target_data.get(crypto_convert_to.lower(), {}).get("usd", None)
                            if target_price_usd is not None and target_price_usd > 0:
                                # Подсчет, сколько единиц целевой крипты идет за 1 единицу исходной
                                converted_value = price_usd / target_price_usd

                    # Строки для таблицы
                    if converted_value is not None:
                        if qty is not None:
                            total = converted_value * qty
                            if crypto_convert_to in ["USDT", "BNB", "DOGE"]:
                                name_display_full = f"{name_display} ({qty:.4f} шт.) -> {display_currency}"
                            else:
                                name_display_full = f"{name_display} ({qty:.4f} шт.)"
                            results.append(("Крипта", name_display_full, self.format_currency(total, display_currency)))
                        else:
                            if crypto_convert_to in ["USDT", "BNB", "DOGE"]:
                                results.append(
                                    ("Крипта", f"1 {name_display} = {converted_value:.8f} {display_currency}", ""))
                            else:
                                results.append(
                                    ("Крипта", name_display, self.format_currency(converted_value, display_currency)))
                    else:
                        results.append(("Крипта", "Ошибка конвертации (валюта не найдена)", ""))
                else:
                    results.append(("Крипта", "Данные не найдены", ""))
            except Exception as e:
                results.append(("Крипта", "Ошибка", str(e)))
        else:
            results.append(("Крипта", "Не выбрана", ""))

        #  Валюта
        if base_curr and target_curr:
            try:
                resp = requests.get(self.API_FIAT + base_curr, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                rates = data.get("rates", {})
                if target_curr in rates:
                    rate = rates[target_curr]
                    base_name = self.FIAT_CURRENCIES.get(base_curr, base_curr)
                    target_name = self.FIAT_CURRENCIES.get(target_curr, target_curr)

                    pair_display = f"{base_name}  /  {target_name}"

                    if curr_qty_str:
                        try:
                            qty = float(curr_qty_str)
                            total = rate * qty
                            pair_display = f"{pair_display}  ×  {qty:g}"
                            value_str = f"{total:,.2f} {target_curr}   (курс: {rate:.2f} за 1)"
                        except ValueError:
                            value_str = f"{rate:.2f} {target_curr}"
                    else:
                        value_str = f"{rate:.2f} {target_curr}"

                    results.append(("Валюта", pair_display, value_str))
                else:
                    results.append(("Валюта", "Курс не найден", ""))
            except Exception as e:
                results.append(("Валюта", "Ошибка", str(e)))
        elif base_curr or target_curr:
            results.append(("Валюта", "Выберите обе валюты", ""))

        return results

    #  Форматирование валюты
    @staticmethod
    def format_currency(value, currency_name):
        try:
            return f"{value:,.2f} {currency_name}"
        except (ValueError, TypeError):
            return str(value)

    #  Обновление таблицы
    def update_table(self, rows):
        self.tree.delete(*self.tree.get_children())
        for i, row in enumerate(rows):
            tag = "green_row" if i % 2 == 0 else "blue_row"
            self.tree.insert("", "end", values=row, tags=(tag,))

    #  Обработка кнопки показать
    def on_refresh(self):
        self.set_status("Загрузка данных...", self.COLORS["status_load"])
        self.refresh_btn.config(state="disabled")

        def worker():
            try:
                results = self.fetch_all()
                self._last_results = results
                self.root.after(0, lambda: self.update_table(results))
                self.root.after(0, lambda: self.set_status("Данные обновлены", self.COLORS["status_ok"]))
            except Exception as e:
                self.root.after(0, lambda: self.set_status(f"Ошибка: {e}", "#f44336"))
            finally:
                self.root.after(0, lambda: self.refresh_btn.config(state="normal"))

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyApp(root)
    root.mainloop()