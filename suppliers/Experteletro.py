import requests
import pandas as pd
from io import StringIO
from logger.Logger import Logger

class Experteletro:
    ENDPOINT = "https://experteletro.pt/webservice.php?key=f8615627-4ea1-11eb-b020-a4bf011b03ee&pass=NTA5MDQzMjY3"
    local_logger = Logger.setup(name = "Experteletro")

    # ─────────────────────────────────────────────────────────────
    # Download
    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def download_file() -> str | bool:
        print("Iniciar download ficheiro Experteletro")
        Experteletro.local_logger.info("Iniciando download do ficheiro Experteletro")

        try:
            resp = requests.get(Experteletro.ENDPOINT, timeout=60)
            resp.raise_for_status()
        except requests.exceptions.RequestException as exc:
            print(f"Erro ao efetuar download: {exc}")
            Experteletro.local_logger.error("Falha no download: %s", exc, exc_info=True)
            return False

        Experteletro.local_logger.info(
            "Download OK | status=%s | bytes=%d", resp.status_code, len(resp.content)
        )
        print(f"Download bem‑sucedido! Código de resposta: {resp.status_code}")

        return resp.content.decode("iso-8859-1")  # Experteletro CSV é ISO‑8859‑1

        # ────────────────────────────────────────────────────────────────
        # Normalize
        # ────────────────────────────────────────────────────────────────

    @staticmethod
    def normalize_file(raw_content):
        """Converte CSV Experteletro em lista de dicts padronizados para comparação."""
        Experteletro.local_logger.info("Normalizando conteúdo CSV (%d caracteres)", len(raw_content))

        csv_buffer = StringIO(raw_content)
        df = pd.read_csv(csv_buffer, sep=';', skipinitialspace=True, index_col=False)

        formatted_data = []
        total_rows = len(df)

        for idx, row in df.iterrows():
            name = row["nome"]
            print(f"[*] Formatar ({idx + 1}/{total_rows}): {name}")
            Experteletro.local_logger.debug("Formatar idx=%d | %s", idx, name)

            stock = str(row['disponibilidade'])

            if stock == "Limitado":
                stock = 1
            elif stock == "Disponivel":
                stock = 2
            elif stock == "Indisponivel":
                stock = 0
            else:
                stock = 0


            product = {
                "stock": stock,
                "price": row['preco'],
                "name": name,
                "ean13": str(row['ean']).replace(".0", "").zfill(13)
            }

            Experteletro.local_logger.debug("\tProduto normalizado: %r", product)
            formatted_data.append(product)

        Experteletro.local_logger.info("Total de linhas normalizadas: %d", total_rows)
        return formatted_data