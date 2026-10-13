import requests
import tkinter as tk
from tkinter import ttk, messagebox

CRYPTO_IDS = [
    "bitcoin",
    "ethereum",
    "solana",
    "ripple",
    "cardano",
    "dogecoin",
    "polkadot",
    "chainlink",
]

CRYPTO_NAMES = {
    "bitcoin": "Bitcoin (BTC)",
    "ethereum": "Ethereum (ETH)",
    "solana": "Solana (SOL)",
    "ripple": "Ripple (XRP)",
    "cardano": "Cardano (ADA)",
    "dogecoin": "Dogecoin (DOGE)",
    "polkadot": "Polkadot (DOT)",
    "chainlink": "Chainlink (LINK)",
}

API_URL = "https://api.coingecko.com/api/v3/simple/price"


def fetch_prices():
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
    btn_refresh.config(state="disabled")
    status_label.config(text="Загрузка курсов...", fg="#4a90e2")

    def worker():
        try:
            rows = fetch_prices()
            tree.delete(*tree.get_children())
            for name, price in rows:
                tree.insert("", "end", values=(name, price))
            status_label.config(text="Курсы обновлены", fg="#2e7d32")
        except RuntimeError as e:
            messagebox.showerror("Ошибка", str(e))
            status_label.config(text="Ошибка загрузки", fg="#d32f2f")
        finally:
            btn_refresh.config(state="normal")

    import threading
    threading.Thread(target=worker, daemon=True).start()


root = tk.Tk()
root.title("Курсы криптовалют к USD (от CoinGecko)")
root.geometry("500x350")

lbl_title = tk.Label(root, text="Курсы криптовалют к USD", font=("Arial", 14, "bold"))
lbl_title.pack(pady=10)

btn_refresh = ttk.Button(root, text="Обновить курсы", command=update_table)
btn_refresh.pack(pady=5)

status_label = tk.Label(root, text="Нажмите «Обновить курсы»", fg="#555555", font=("Arial", 10))
status_label.pack(pady=5)

columns = ("name", "price")
tree = ttk.Treeview(root, columns=columns, show="headings", height=12)

tree.heading("name", text="Криптовалюта")
tree.heading("price", text="Курс к USD")

tree.column("name", width=300, anchor="w")
tree.column("price", width=150, anchor="e")

tree.pack(fill="both", expand=True, padx=10, pady=5)

update_table()

root.mainloop()









