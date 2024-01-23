import logging
import sys

format_1 = '{levelname:8} [{asctime}] {filtername}:'\
            '{lineno} - {name} - {message}'

format_2 = '[{asctime}] #{levelname:8} {filename}:'\
            '{lineno} - {name} - {message}'

formatter_1 = logging.Formatter(fmt = format_1, style='{')
formatter_2 = logging.Formatter(fmt = format_2, style='{')

logger = logging.getLogger(__name__)

stderr_handler = logging.StreamHandler()
stdout_handler = logging.StreamHandler(sys.stdout)

stdout_handler.setFormatter(formatter_1)
stderr_handler.setFormatter(formatter_2)

logger.addHandler(stdout_handler)
logger.addHandler(stderr_handler)

#print(logger.handlers)
#logger.level = logging.DEBUG
#logger.warning('Warning!')
logger.warning('Warning information!')



