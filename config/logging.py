import logging
import os

def setup_logger(log_file_name):
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, f"{log_file_name}.log")
    
    logger = logging.getLogger(log_file_name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

def log_exception(logger, exception, message):
    exception_level_map = {
        ValueError: logging.WARNING,
        TypeError: logging.WARNING,
        FileNotFoundError: logging.ERROR,
        ZeroDivisionError: logging.CRITICAL,
        Exception: logging.ERROR
    }
    log_level = exception_level_map.get(type(exception), logging.ERROR)
    logger.log(log_level, f"{message}: {str(exception)}")

if __name__ == "__main__":
    logger = setup_logger("auto_level_app")
    
    try:
        raise ValueError("Invalid value provided")
    except Exception as e:
        log_exception(logger, e, "Caught ValueError")
    
    try:
        result = 10 / 0
    except Exception as e:
        log_exception(logger, e, "Caught ZeroDivisionError")
    
    try:
        with open("nonexistent.txt") as f:
            content = f.read()
    except Exception as e:
        log_exception(logger, e, "Caught FileNotFoundError")
    
    try:
        x = int("not_a_number")
    except Exception as e:
        log_exception(logger, e, "Caught TypeError")
