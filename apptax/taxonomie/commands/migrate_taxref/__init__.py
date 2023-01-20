import logging

logger = logging.getLogger("taxref_migration")
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
# # create formatter
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)
