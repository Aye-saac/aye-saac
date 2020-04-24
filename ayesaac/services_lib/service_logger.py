import logging
from pathlib import Path


def open_log(service_name: str):
    root_logger = logging.getLogger('ayesaac')
    root_logger.setLevel(logging.DEBUG)

    logfile = Path(__file__).parent.parent.parent/'ayesaac'/'services_log'/f'{service_name}.log'
    file_handler = logging.FileHandler(logfile, mode='w')
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s   [%(filename)s:%(lineno)d] - %(message)s')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
