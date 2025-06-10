import requests
import pandas as pd
from io import StringIO
from logger.Logger import Logger


class Orima:
    """Responsável por descarregar o CSV da Orima e convertê‑lo em lista de dicts."""

    ENDPOINT = (
        "https://orima.pt/api/get/products/id/33098/username/suporte@kontrolsat.com/password/509043267/filetype/csv"
    )

    local_logger = Logger.setup(name="Orima")

    # ─────────────────────────────────────────────────────────────
    # Download
    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def download_file() -> str | bool:
        """Faz download do CSV da Orima. Devolve str (ISO‑8859‑1) ou False se falhar."""
        print("Iniciar download ficheiro Orima…")
        Orima.local_logger.info("Iniciando download do ficheiro Orima")

        try:
            resp = requests.get(Orima.ENDPOINT, timeout=60)
            resp.raise_for_status()
        except requests.exceptions.RequestException as exc:
            print(f"Erro ao efetuar download: {exc}")
            Orima.local_logger.error("Falha no download: %s", exc, exc_info=True)
            return False

        Orima.local_logger.info(
            "Download OK | status=%s | bytes=%d", resp.status_code, len(resp.content)
        )
        print(f"Download bem‑sucedido! Código de resposta: {resp.status_code}")

        return resp.content.decode("iso-8859-1")  # Orima CSV é ISO‑8859‑1

    # ─────────────────────────────────────────────────────────────
    # Normalize
    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def normalize_file(raw_content: str):
        """Converte o CSV em lista de produtos normalizados."""
        Orima.local_logger.info("Normalizando ficheiro (len=%d)", len(raw_content))

        buf = StringIO(raw_content)
        df = pd.read_csv(buf, sep=";", encoding="iso-8859-1", index_col=False, skipinitialspace=True)

        formatted_data = []
        for idx, row in df.iterrows():
            name = row["description"]
            stock_val = str(row["stock"]).strip()
            if stock_val in {"F", "E", "0"}:
                stock_val = 0
            else:
                try:
                    stock_val = int(float(stock_val))  # alguns vêm como "3.0"
                except (TypeError, ValueError):
                    stock_val = 0

            product = {
                "stock": stock_val,
                "price": row["wholesale_price"],
                "name": name,
                "ean13": row["ean13"].zfill(13),
            }

            print(f"[*] Orima formatar: {name}")
            Orima.local_logger.debug("Produto normalizado: %r", product)
            formatted_data.append(product)

        Orima.local_logger.info("Total de produtos normalizados: %d", len(formatted_data))
        return formatted_data
