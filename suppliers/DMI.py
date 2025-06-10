import requests
import pandas as pd
from io import StringIO
from logger.Logger import Logger

class DMI:
    """Responsável por descarregar o CSV da Prome aka DMI e convertê‑lo em lista de dicts."""

    ENDPOINT = "https://www.dmi.es/catalogo.aspx?u=CT074858&p=yhnadcjj"
    local_logger = Logger.setup(name="DMI")

    # ─────────────────────────────────────────────────────────────
    # Download
    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def download_file() -> bool | str:
        """Faz download do CSV da DMI. Devolve str (ISO‑8859‑1) ou False se falhar."""
        print("Iniciar download ficheiro DMI…")
        DMI.local_logger.info("Iniciando download do ficheiro Prome")

        try:
            resp = requests.get(DMI.ENDPOINT, timeout=120)
            resp.raise_for_status()
        except requests.exceptions.RequestException as exc:
            print(f"Erro ao efetuar download: {exc}")
            DMI.local_logger.error("Falha no download: %s", exc, exc_info=True)
            return False

        DMI.local_logger.info(
            "Download OK | status=%s | bytes=%d", resp.status_code, len(resp.content)
        )
        print(f"Download bem‑sucedido! Código de resposta: {resp.status_code}")

        return resp.content.decode("iso-8859-1")  # Prome CSV é ISO‑8859‑1


    # ────────────────────────────────────────────────────────────────
    # Normalize
    # ────────────────────────────────────────────────────────────────
    @staticmethod
    def normalize_file(raw_content):
        """Converte CSV DMI em lista de dicts padronizados para comparação."""
        DMI.local_logger.info("Normalizando conteúdo CSV (%d caracteres)", len(raw_content))

        csv_buffer = StringIO(raw_content)
        df = pd.read_csv(csv_buffer, sep=';', skipinitialspace=True, index_col=False)

        formatted_data = []
        total_rows = len(df)

        for idx, row in df.iterrows():
            name = row["DENOMINA"]
            print(f"[*] Formatar ({idx + 1}/{total_rows}): {name}")
            DMI.local_logger.debug("Formatar idx=%d | %s", idx, name)

            stock = str(row['STOCK'])
            product = {
                "stock": stock,
                "price": row['COMPRA'],
                "name": name,
                "ean13": str(row['EAN']).replace(".0", "").zfill(13)
            }
            DMI.local_logger.debug("\tProduto normalizado: %r", product)
            formatted_data.append(product)

        DMI.local_logger.info("Total de linhas normalizadas: %d", total_rows)
        return formatted_data