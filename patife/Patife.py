import requests
from typing import Dict, Any, List
from logger.Logger import Logger

# Inicializa logger global (pode ser reconfigurado por supplier_name ao chamar setup)
logger = Logger.setup()

class Patife:
    PATIFE_KEY = "SRNEJZFZ7HK5P2E1UQ7DLPKBFVAXCWP2"
    GET_SUPPLIER_STOCKS_EDP = "http://patife.kontrolsat.com/api/products-supplier/"
    UPD_SUPPLIER_STOCK_EDP = "http://patife.kontrolsat.com/api/update-product-supplier/"

    @staticmethod
    def get_current_stocks(supplier_id: int, supplier_name: str) -> Dict[str, Dict[str, Any]]:
        """
        Faz GET /api/products-supplier/{supplier_id}?key={PATIFE_KEY} e
        retorna um dicionário { ean13: {'stock': int, 'price': float}, … }.
        """
        local_logger = Logger.setup(name=supplier_name)
        local_logger.info("Procurar stocks do supplier %s", supplier_id)
        print(f"Procurar stocks do supplier {supplier_id}...")

        final_endpoint = f"{Patife.GET_SUPPLIER_STOCKS_EDP}{supplier_id}"
        params = {"key": Patife.PATIFE_KEY}
        headers = {"User-Agent": "Servidor-Local-Stock-Updater"}

        local_logger.debug("GET %s params=%r headers=%r", final_endpoint, params, headers)
        response = requests.get(final_endpoint, params=params, headers=headers, timeout=120)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            local_logger.error("Erro HTTP ao procurar stocks: %s", exc, exc_info=True)
            raise

        payload: List[Dict[str, Any]] = response.json()
        result: Dict[str, Dict[str, Any]] = {}

        for item in payload:
            ean = item.get("ean13")
            if not ean:
                local_logger.warning("Item sem EAN ignorado: %r", item)
                continue

            try:
                stock = int(item.get("stock", 0))
            except (TypeError, ValueError):
                stock = 0
                local_logger.warning("Stock inválido para EAN %s: %r", ean, item.get("stock"))
                continue

            try:
                price = float(item.get("price", 0.0))
            except (TypeError, ValueError):
                price = 0.0
                local_logger.warning("Price inválido para EAN %s: %r", ean, item.get("price"))
                continue

            result[ean] = {"stock": stock, "price": price}

        local_logger.info("Recuperados %d produtos do supplier %s", len(result), supplier_id)
        return result

    @staticmethod
    def update_stock(supplier_id: int, supplier_name: str, product_data: List[Dict[str, Any]]):
        """
        Para cada produto em product_data (lista de dicts com 'ean13', 'stock', 'old_stock', 'price', 'old_price'),
        faz POST no endpoint de atualização de stock/preço e registra mudanças.
        """
        local_logger = Logger.setup(name=supplier_name)
        total = len(product_data)
        local_logger.info("Iniciando atualização de %d produtos para %s (ID %s)", total, supplier_name, supplier_id)
        print(f"Iniciando atualização de stock para {supplier_name} ({total} produtos)")

        for p in product_data:
            ean = p.get("ean13")
            new_stock = p.get("stock")
            old_stock = p.get("old_stock")
            new_price = p.get("price")
            old_price = p.get("old_price")

            if not ean:
                local_logger.warning("Pulando item sem EAN: %r", p)
                continue

            print(f"Atualizar {ean}: stock {old_stock} -> {new_stock}, price {old_price} -> {new_price}")
            endpoint = f"{Patife.UPD_SUPPLIER_STOCK_EDP}{supplier_id}/{ean}"
            params = {"key": Patife.PATIFE_KEY}
            headers = {"User-Agent": "Servidor-Local-Stock-Updater"}
            payload = {"stock": new_stock, "price": new_price}

            local_logger.debug(
                "POST %s params=%r headers=%r payload=%r", endpoint, params, headers, payload
            )

            try:
                response = requests.post(
                    endpoint,
                    params=params,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
            except requests.exceptions.RequestException as exc:
                local_logger.error(
                    "Falha ao atualizar EAN=%s: %s", ean, exc, exc_info=True
                )
                print(f"Falha ao atualizar {ean}: {exc}")
            else:
                local_logger.info(
                    "Sucesso %s: stock %s -> %s, price %.2f -> %.2f, status=%s",
                    ean, old_stock, new_stock, old_price, new_price, response.status_code
                )
                print(
                    f"Sucesso atualização de {ean}: "
                    f"stock {old_stock}->{new_stock}, price {old_price}->{new_price}, "
                    f"status {response.status_code}"
                )
