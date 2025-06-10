from routines.supplier_routines import *
from logger.Logger import Logger

if __name__ == "__main__":
    ## LOGGER ===================================================
    logger = Logger.setup()

    ## ALSO =====================================================
    # logger.info("Corrigir stock Also")
    # AlsoRoutine(logger)

    ## DEPAU ====================================================
    logger.info("Corrigir stock Depau")
    DepauRoutine(logger)

    ## DMI ======================================================
    logger.info("Corrigir stock DMI")
    DMIRoutine(logger)

    ## ELEKTRO ==================================================
    logger.info("Corrigir Stock Elektro3")
    ElektroRoutine(logger)

    ## Experteletro =============================================
    logger.info("Corrigir stock Experteletro")
    ExperteletroRoutine(logger)

    ## Globomatik ===============================================
    # IT CANT BE DONE

    # Orima ====================================================
    logger.info("Corrigir stock Orima")
    OrimaRoutine(logger)

    ## Prome ====================================================
    logger.info("Corrigir stock Prome")
    PromeRoutine(logger)








