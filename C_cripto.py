import requests
import tkinter as tk
from tkinter import ttk, messagebox

# Список популярных монет (id для CoinGecko)
CRYPTO_IDS = [
    "bitcoin",
    "ethereum",
    "solana",
    "ripple",
    "cardano",
    "dogecoin",
    "polkadot",
    "avalanche",
    "chainlink",
    "ton"
]

# Читаемые названия
CRYPTO_NAMES = {
    "bitcoin": "Bitcoin (BTC)",
    "ethereum": "Ethereum (ETH)",
    "solana": "Solana (SOL)",
    "ripple": "Ripple (XRP)",
    "cardano": "Cardano (ADA)",
    "dogecoin": "Dogecoin (DOGE)",
    "polkadot": "Polkadot (DOT)",
    "avalanche": "Avalanche (AVAX)",
    "chainlink": "Chainlink (LINK)",
    "ton": "TON (TON)"
}

API_URL = "https://api.coingecko.com/api/v3/simple/price"


def fetch_prices():
    """Получает курсы к USD и возвращает список строк для таблицы."""
    try:
        params = {
            "ids": ",".join(CRYPTO_IDS),
            "vs_currencies": "usd"
        }
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        rows = []
        for coin_id in CRYPTO_IDS:
            price_usd = data.get(coin_id, {}).get("usd")
            name = CRYPTO_NAMES.get(coin_id, coin_id.capitalize())
            if price_usd is not None:
                rows.append((name, f"{price_usd:,.2f} USD"))
            else:
                rows.append((name, "Нет данных"))
        return rows

    except requests.exceptions.Timeout:
        raise RuntimeError("Превышено время ожидания ответа от сервера.")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Ошибка соединения: {e}")
    except Exception as e:
        raise RuntimeError(f"Произошла ошибка: {e}")


def update_table():
    """Обновляет таблицу с курсами."""
    # блокировка кнопки
    btn_refresh.config(state="disabled")
    status_label.config(text="Загрузка курсов...", fg="#4a90e2")

    def worker():
        try:
            rows = fetch_prices()
            # очистка таблицы и заполняем новыми данными
            tree.delete(*tree.get_children())
            for name, price in rows:
                tree.insert("", "end", values=(name, price))
            status_label.config(text="Курсы обновлены", fg="#2e7d32")
        except RuntimeError as e:
            messagebox.showerror("Ошибка", str(e))
            status_label.config(text="Ошибка загрузки", fg="#d32f2f")
        finally:
            btn_refresh.config(state="normal")

    # отдельный поток, чтобы интерфейс не зависал
    import threading
    threading.Thread(target=worker, daemon=True).start()


# Интерфейс
root = tk.Tk()
root.title("Курсы криптовалют к USD (CoinGecko)")
root.geometry("500x450")

# Заголовок
lbl_title = tk.Label(root, text="Актуальные курсы криптовалют к USD", font=("Arial", 14, "bold"))
lbl_title.pack(pady=10)

# Кнопка обновления
btn_refresh = ttk.Button(root, text="Обновить курсы", command=update_table)
btn_refresh.pack(pady=5)

# Статус
status_label = tk.Label(root, text="Нажмите «Обновить курсы»", fg="#555555", font=("Arial", 10))
status_label.pack(pady=5)

# Таблица
columns = ("name", "price")
tree = ttk.Treeview(root, columns=columns, show="headings", height=12)

tree.heading("name", text="Криптовалюта")
tree.heading("price", text="Курс к USD")

tree.column("name", width=300, anchor="w")
tree.column("price", width=150, anchor="e")

tree.pack(fill="both", expand=True, padx=10, pady=5)

# Первая загрузка при старте
update_table()

root.mainloop()









