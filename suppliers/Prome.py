import json
import re
from html import unescape
from pathlib import Path
from typing import Any, Dict

import requests
from logger.Logger import Logger


class Prome:
    ENDPOINT = "http://patife.kontrolsat.com/api/proxy-download/prome?key=SRNEJZFZ7HK5P2E1UQ7DLPKBFVAXCWP2"

    local_logger = Logger.setup("Prome")

    # ------------------------------------------------------------------
    @staticmethod
    def download(save_path: str | None = None) -> Dict[str, Any] | None:
        try:
            response = requests.get(Prome.ENDPOINT, timeout=200)
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            print(f"Erro ao efetuar download: {exc}")
            Prome.local_logger.error("Falha no download: %s", exc, exc_info=True)
            return False

        Prome.local_logger.info(
            "Download bem‑sucedido | status=%s | bytes=%d",
            response.status_code,
            len(response.content),
        )
        print(f"Download bem‑sucedido! Código de resposta: {response.status_code}")
        return response.json()


    @staticmethod
    def normalize_data(raw_response):
        data = []
        products = raw_response.get("Produtos")

        for p in products:
            ean = str(p.get("EAN")).replace(".0", "")
            stock = p.get("Stock")
            name = p.get('Nome')
            raw_price = p.get("Preco")  # pode vir str, float ou None

            try:
                price = round(float(raw_price), 2)  # 2 casas decimais – 12.345 → 12.35
            except (TypeError, ValueError):
                price = p.get("Preco")

            data.append({
                "stock": stock,
                "price": price,
                "name": name,
                "ean13": ean
            })

        return data