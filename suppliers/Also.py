from pathlib import Path
import zipfile
import paramiko
import pandas as pd
from io import StringIO
from logger.Logger import Logger

class Also:
    FTP_HOSTNAME = "paco.also.com"
    FTP_FILEPATH = "./pricelist-1.csv.zip"   # caminho NO servidor
    FTP_USERNAME = "nesofuwexawada"
    FTP_PASSWORD = "todi9taci6"

    LOCAL_DIR   = Path("./downloads")
    LOCAL_ZIP   = LOCAL_DIR / "also_pricelist.zip"
    
    local_logger = Logger.setup(name="ALSO")

    # ─────────────────────────────────────────────────────────────
    # Download
    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def download_zip() -> bool:
        print("Conectar por SFTP Also...")
        Also.local_logger.info("Contectar STFP %s", Also.FTP_HOSTNAME)
        
        Also.LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        transport = paramiko.Transport((Also.FTP_HOSTNAME, 22))

        try:
            transport.connect(None, Also.FTP_USERNAME, Also.FTP_PASSWORD)
            sftp = paramiko.SFTPClient.from_transport(transport)
            Also.local_logger.info("Conectado SFTP %s", Also.FTP_HOSTNAME)
            Also.local_logger.info("Download %s → %s", Also.FTP_FILEPATH, Also.LOCAL_ZIP)
            sftp.get(Also.FTP_FILEPATH, str(Also.LOCAL_ZIP))
        except Exception as e:
            print(f"Falha a conectar por SFTP: {e}")
            Also.local_logger.error("Falha no SFTP: %s", e, exc_info=True)
            return False
        finally:
            transport.close()

        Also.local_logger.info("ZIP guardado (%d bytes)", Also.LOCAL_ZIP.stat().st_size)
        print("Download ZIP concluído.")
        return True

    # ─────────────────────────────────────────────────────────────
    # Extração
    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def extract_csv() -> Path | None:
        if not Also.LOCAL_ZIP.exists():
            Also.local_logger.error("ZIP não encontrado para extrair")
            return None

        with zipfile.ZipFile(str(Also.LOCAL_ZIP)) as zf:
            csv_name = next((n for n in zf.namelist() if n.endswith(".csv")), None)
            if csv_name is None:
                Also.local_logger.error("Nenhum CSV dentro do ZIP")
                return None

            dest = Also.LOCAL_DIR / csv_name
            zf.extract(csv_name, Also.LOCAL_DIR)
            Also.local_logger.info("CSV extraído para %s", dest)
            return dest


    # ─────────────────────────────────────────────────────────────
    # Normalização
    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def normalize_file(csv_path: Path):
        """Lê o CSV da Also e devolve lista de dicts."""
        Also.local_logger.info("Lendo CSV %s", csv_path)
        df = pd.read_csv(
            csv_path,
            sep=";",
            encoding="latin-1",
            skipinitialspace=True,
            index_col=False,
        )

        formatted = []
        for _, row in df.iterrows():
            stock_val = str(row["AvailableQuantity"]).strip().replace(".0", "")
            ean13 = str(row["EuropeanArticleNumber"]).replace(".0", "").strip()

            if not stock_val:
                Also.local_logger.error(f"Erro ao encontrar stock para produto: {ean13}")
                stock_val = 0


            product = {
                "stock": stock_val,
                "price": row["NetPrice"],
                "name":  row["Description"],
                "ean13": ean13,
            }
            Also.local_logger.debug("Produto normalizado: %r", product)
            formatted.append(product)

        Also.local_logger.info("Total produtos normalizados: %d", len(formatted))
        return formatted

















