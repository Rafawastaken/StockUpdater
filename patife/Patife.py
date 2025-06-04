import requests
from typing import Dict, Any, List

class Patife:
    PATIFE_KEY = "COLOQUE_A_SUA_CHAVE_AQUI"
    BASE_URL = "http://localhost/patife/public"
    GET_SUPPLIER_STOCKS_EDP = f"{BASE_URL}/api/products-supplier"

    @staticmethod
    def get_current_stocks(supplier_id: int) -> Dict[str, Dict[str, Any]]:
        """
        Faz GET /api/products-supplier/{supplier_id}?key={PATIFE_KEY} e
        retorna um dicionário { ean13: {'stock': int, 'price': float}, … }.
        """
        final_endpoint = f"{Patife.GET_SUPPLIER_STOCKS_EDP}/{supplier_id}"
        params  = {"key": Patife.PATIFE_KEY}
        headers = {"User-Agent": "Servidor-Local-Stock-Updater"}

        resp = requests.get(final_endpoint, params=params, headers=headers, timeout=10)
        resp.raise_for_status()  # dispara HTTPError se status != 200

        payload: List[Dict[str, Any]] = resp.json()

        result: Dict[str, Dict[str, Any]] = {}
        for item in payload:
            ean = item.get("ean13")
            if not ean:
                continue

            # Convertendo 'stock' e 'price' de string para os tipos corretos
            try:
                stock = int(item.get("stock", 0))
            except (TypeError, ValueError):
                stock = 0

            try:
                price = float(item.get("price", 0.0))
            except (TypeError, ValueError):
                price = 0.0

            result[ean] = {"stock": stock, "price": price}

        return result
