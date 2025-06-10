from patife import Patife
from helpers.stock_parser import file_parser

from suppliers.Orima import Orima
from suppliers.Depau import Depau
from suppliers.DMI import DMI
from suppliers.Experteletro import Experteletro
from suppliers.Also import Also
from suppliers.Elektro import Elektro
from suppliers.Prome import Prome

def ElektroRoutine(logger) -> bool:
    try:
        SUPPLIER_ID = 11
        SUPPLIER_NAME = "Elektro"

        elektro_patife_products = Patife.get_current_stocks(supplier_id=SUPPLIER_ID, supplier_name=SUPPLIER_NAME)
        access_token = Elektro.authenticate()
        elektro_formatted_products = Elektro.get_normalize_products(access_token)
        elektro_corrected_stock_data = file_parser(patife_data=elektro_patife_products, supplier_data=elektro_formatted_products, supplier_name=SUPPLIER_NAME)
        Patife.update_stock(SUPPLIER_ID, SUPPLIER_NAME, elektro_corrected_stock_data)
    except Exception as e:
        logger.error(f"Error rotina da Elektro: {e}")
        return False

def AlsoRoutine(logger) -> bool:
    try:
        SUPPLIER_ID = 6
        SUPPLIER_NAME = "ALSO"

        also_download_zip = Also.download_zip()
        if not also_download_zip:
            return False
        also_csv_file = Also.extract_csv()
        if not also_csv_file:
            return False

        also_patife_products = Patife.get_current_stocks(supplier_id = SUPPLIER_ID, supplier_name = SUPPLIER_NAME)
        also_formatted_data = Also.normalize_file(also_csv_file)
        also_corrected_stock_data = file_parser(patife_data=also_patife_products, supplier_data=also_formatted_data, supplier_name=SUPPLIER_NAME)
        Patife.update_stock(SUPPLIER_ID, SUPPLIER_NAME, also_corrected_stock_data)
        logger.info("ALSO atualizada com sucesso")
        return True
    except Exception as e:
        logger.error(f"Error rotina da ALSO: {e}")
        return False

def OrimaRoutine(logger) -> bool:
    try:
        SUPPLIER_ID = 1
        SUPPLIER_NAME = "Orima"
        orima_patife_products = Patife.get_current_stocks(supplier_id = SUPPLIER_ID, supplier_name = SUPPLIER_NAME)
        orima_raw_response = Orima.download_file()
        orima_formatted_data = Orima.normalize_file(raw_content = orima_raw_response)
        orima_corrected_stock_data = file_parser(patife_data = orima_patife_products, supplier_data=orima_formatted_data, supplier_name=SUPPLIER_NAME)
        Patife.update_stock(SUPPLIER_ID, SUPPLIER_NAME, orima_corrected_stock_data)
        logger.info("Orima atualizada com sucesso")
        return True
    except Exception as e:
        logger.error(f"Error rotina da Orima: {e}")
        return False

def DepauRoutine(logger) -> bool:
    try:
        SUPPLIER_ID = 9
        SUPPLIER_NAME = "Depau"
        depau_patife_products = Patife.get_current_stocks(supplier_id=SUPPLIER_ID, supplier_name=SUPPLIER_NAME)
        depau_raw_response = Depau.download_file()
        depau_formatted_data = Depau.normalize_file(raw_content = depau_raw_response)
        depau_corrected_stock_data = file_parser(patife_data=depau_patife_products, supplier_data=depau_formatted_data, supplier_name=SUPPLIER_NAME)
        Patife.update_stock(SUPPLIER_ID, SUPPLIER_NAME, depau_corrected_stock_data)
        logger.info("Depau atualizada com sucesso")
        return True
    except Exception as e:
        logger.error(f"Error rotina da Depau: {e}")
        return False

def ExperteletroRoutine(logger) -> bool:
    try:
        SUPPLIER_ID = 4
        SUPPLIER_NAME = "Experteletro"
        experteletro_patife_products = Patife.get_current_stocks(supplier_id=SUPPLIER_ID, supplier_name=SUPPLIER_NAME)
        experteletro_raw_response = Experteletro.download_file()
        experteletro_formatted_data = Experteletro.normalize_file(raw_content = experteletro_raw_response)
        prome_corrected_stock_data = file_parser(patife_data=experteletro_patife_products, supplier_data=experteletro_formatted_data, supplier_name=SUPPLIER_NAME)
        Patife.update_stock(SUPPLIER_ID, SUPPLIER_NAME, prome_corrected_stock_data)
        logger.info("Experteletro atualizada com sucesso")
        return True
    except Exception as e:
        logger.error(f"Error rotina da Experteletro: {e}")
        return False

def DMIRoutine(logger) -> bool:
    try:
        SUPPLIER_ID = 10
        SUPPLIER_NAME = "DMI"
        dmi_patife_products = Patife.get_current_stocks(supplier_id=SUPPLIER_ID, supplier_name=SUPPLIER_NAME)
        dmi_raw_response = DMI.download_file()
        dmi_formatted_data = DMI.normalize_file(raw_content=dmi_raw_response)
        dmi_corrected_stock_data = file_parser(patife_data=dmi_patife_products, supplier_data=dmi_formatted_data, supplier_name=SUPPLIER_NAME)
        Patife.update_stock(SUPPLIER_ID, SUPPLIER_NAME, dmi_corrected_stock_data)
        logger.info("DMI atualizada com sucesso")
        return True
    except Exception as e:
        logger.error(f"Error rotina da DMI: {e}")
        return False

def PromeRoutine(logger) -> bool:
    try:
        SUPPLIER_ID = 2
        SUPPLIER_NAME = "Prome"
        prome_patife_products = Patife.get_current_stocks(supplier_id=SUPPLIER_ID, supplier_name=SUPPLIER_NAME)
        prome_raw_response = Prome.download()
        prome_formatted_data = Prome.normalize_data(prome_raw_response)
        prome_corrected_stock_data = file_parser(patife_data=prome_patife_products, supplier_data=prome_formatted_data, supplier_name=SUPPLIER_NAME)
        Patife.update_stock(SUPPLIER_ID, SUPPLIER_NAME, prome_corrected_stock_data)
        logger.info("Prome atualizada com sucesso")
        return True
    except Exception as e:
        logger.error(f"Error rotina da Prome: {e}")
        return False