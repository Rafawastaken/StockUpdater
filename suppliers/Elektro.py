import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

import requests
from logger.Logger import Logger


class Elektro:
    AUTH_ENDPOINT = "https://api.elektro3.com/oauth/token"
    PRODUCTS_ENDPOINT = "https://api.elektro3.com/api/get-productos/"
    AUTH_PAYLOAD = {
        "grant_type": "password",
        "client_id": "243",
        "client_secret": "BOT10OuYiTGA6S4ibT0b7suICSDZORZvKaKxqCQn",
        "username": "suporte@kontrolsat.com",
        "password": "7FACNIIrKO7zbHY5HDW3",
    }

    logger = Logger.setup("Elektro")

    # ------------------------------------------------------------------
    @staticmethod
    def authenticate() -> str | None:
        print("Autenticar em Elektro…")
        Elektro.logger.info("Autenticar em Elektro3")

        try:
            r = requests.post(Elektro.AUTH_ENDPOINT, data=Elektro.AUTH_PAYLOAD, timeout=20)
            r.raise_for_status()
            token = r.json().get("access_token")
            if not token:
                Elektro.logger.error("access_token ausente: %r", r.text)
            return token
        except Exception as exc:
            Elektro.logger.error("Falha no login: %s", exc, exc_info=True)
            return None

    # ------------------------------------------------------------------
    @staticmethod
    def get_normalize_products(
        token: str,
        items_per_page: int = 50,  # maior página → menos requisições
        max_workers: int = 10,  # 20 threads ≈ muito mais rápido que serial
    ) -> List[Dict[str, Any]] | None:

        if not token:
            return None

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "StockUpdater/1.0",
        }
        params = {"iso_code": "pt", "items_per_page": items_per_page, "page": 1}

        session = requests.Session()
        session.headers.update(headers)

        try:
            # 1️⃣ primeira página – descobrir total_pages
            print("⇢ Ler página 1 …")
            r = session.post(Elektro.PRODUCTS_ENDPOINT, data=params, timeout=30)
            r.raise_for_status()
            first_json = r.json()
            total_pages = int(first_json.get("total_pages", 1))
            Elektro.logger.info("total_pages=%d | items_per_page=%d", total_pages, items_per_page)
            print(f"Total pages: {total_pages} (items_per_page={items_per_page})")

            def fetch(page: int) -> List[Dict[str, Any]]:
                """Baixa e converte uma página."""
                local_params = params | {"page": page}
                try:
                    resp = session.post(Elektro.PRODUCTS_ENDPOINT, data=local_params, timeout=30)
                    resp.raise_for_status()
                    data = resp.json()
                    prods = [
                        {
                            "ean13": str(p.get("ean13")).replace(".0", ""),
                            "name": p.get("nombre"),
                            "stock": p.get("stock") or p.get("quantity"),
                            "price": p.get("precio") or p.get("price"),
                        }
                        for p in data.get("productos", [])
                    ]
                    print(f"Página {page} ✓ ({len(prods)} produtos)")
                    return prods
                except Exception as exc:
                    print(f"Página {page} ✗ {exc}")
                    Elektro.logger.warning("Página %d falhou: %s", page, exc)
                    return []

            # 3️⃣ baixar em paralelo
            t0 = time.perf_counter()
            product_data: List[Dict[str, Any]] = []

            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                futures = {pool.submit(fetch, p): p for p in range(1, total_pages + 1)}
                for fut in as_completed(futures):
                    product_data.extend(fut.result())

            dt = time.perf_counter() - t0
            print(f"Concluído: {len(product_data)} produtos em {dt:.1f}s")
            Elektro.logger.info("✓ %d produtos em %.1fs", len(product_data), dt)
            return product_data

        except Exception as exc:
            Elektro.logger.error("Erro global em get_normalize_products: %s", exc, exc_info=True)
            return None
