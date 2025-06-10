from io import StringIO
import pandas as pd
import requests.exceptions
from logger.Logger import Logger


class Depau:
    ENDPOINT = "https://www.depau.es/webservices/prestashop/76ed9838-776a-40e7-c00f-97644fc0355a/csv"
    local_logger = Logger.setup(name = "Depau")

    # ────────────────────────────────────────────────────────────────
    # Download
    # ────────────────────────────────────────────────────────────────
    @staticmethod
    def download_file() -> str | bool:
        """Faz download do CSV da Depau e devolve-o como *str* (latin‑1)."""
        print("Iniciar download ficheiro Depau…")
        Depau.local_logger.info("Iniciando download do ficheiro Depau")

        try:
            response = requests.get(Depau.ENDPOINT, timeout=60)
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            print(f"Erro ao efetuar download: {exc}")
            Depau.local_logger.error("Falha no download: %s", exc, exc_info=True)
            return False

        Depau.local_logger.info(
            "Download bem‑sucedido | status=%s | bytes=%d",
            response.status_code,
            len(response.content),
        )
        print(f"Download bem‑sucedido! Código de resposta: {response.status_code}")

        # Decodifica inteiro como latin‑1 (arquivo da Depau costuma vir em ISO‑8859‑1)
        return response.content.decode("latin-1")

    # ────────────────────────────────────────────────────────────────
    # Normalize
    # ────────────────────────────────────────────────────────────────
    @staticmethod
    def normalize_file(raw_content):
        """Converte CSV Depau em lista de dicts padronizados para comparação."""
        Depau.local_logger.info("Normalizando conteúdo CSV (%d caracteres)", len(raw_content))

        csv_buffer = StringIO(raw_content)
        df = pd.read_csv(csv_buffer, sep=';', skipinitialspace=True, index_col=False)

        formatted_data = []
        total_rows = len(df)

        for idx, row in df.iterrows():
            name = row["Nombre"]
            print(f"[*] Formatar ({idx+1}/{total_rows}): {name}")
            Depau.local_logger.debug("Formatar idx=%d | %s", idx, name)

            stock = str(row['Cantidad'])
            product = {
                "stock": stock,
                "price": row['PVD (Sin IVA) con Canon'],
                "name": row['Nombre'],
                "ean13": row['EAN13']
            }
            Depau.local_logger.debug("\tProduto normalizado: %r", product)
            formatted_data.append(product)

        Depau.local_logger.info("Total de linhas normalizadas: %d", total_rows)
        return formatted_data
