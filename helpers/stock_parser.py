from logger.Logger import Logger
from typing import Dict, Any, List


def safe_int(val, fallback=0):
    try:
        return int(val)
    except (TypeError, ValueError):
        return fallback


def safe_float(val, fallback=0.0):
    """Converte val para float lidando com vírgula decimal e None."""
    if val is None or val == "":
        return fallback
    if isinstance(val, (int, float)):
        return float(val)
    try:
        cleaned = str(val).strip().replace(".", "").replace(",", ".")
        return float(cleaned)
    except (TypeError, ValueError):
        return fallback


def file_parser(patife_data: Dict[str, Dict[str, Any]],
                supplier_data: List[Dict[str, Any]],
                supplier_name: str) -> List[Dict[str, Any]]:
    """
    Compara estoques/preços do Patife com o CSV do fornecedor.
    Retorna lista de atualizações necessárias.
    """
    logger = Logger.setup(name=supplier_name)

    print("Comparar dados descarregados com Patife…")
    logger.info("Iniciando comparação Patife × %s", supplier_name)

    products_update: List[Dict[str, Any]] = []

    for ean, patife_info in patife_data.items():
        patife_stock = safe_int(patife_info.get("stock"), 0)
        patife_price = safe_float(patife_info.get("price"), 0.0)

        sup = next((s for s in supplier_data if str(s.get("ean13")) == str(ean)), None)

        if sup is None:
            sup_stock = 0
            sup_price = patife_price
            sup_name = "N/A"
        else:
            sup_stock = safe_int(sup.get("stock"), 0)
            sup_price = safe_float(sup.get("price"), patife_price)
            sup_name = sup.get("name", "<sem nome>")

        # Verifica diferenças
        if sup_stock != patife_stock or sup_price != patife_price:
            print(f"Atualizar {ean}: stock {patife_stock} → {sup_stock}, price {patife_price} → {sup_price}")
            logger.info(
                "Atualizar: %s | %s | stock %s → %s | price %.2f → %.2f",
                sup_name, ean, patife_stock, sup_stock, patife_price, sup_price
            )

            products_update.append({
                "ean13": ean,
                "stock": sup_stock,
                "old_stock": patife_stock,
                "price": sup_price,
                "old_price": patife_price
            })

    logger.info("Total de produtos a atualizar: %d", len(products_update))
    return products_update
