import logging

WEB_LOGGER = logging.getLogger(__name__)
WEB_LOGGER.setLevel(logging.DEBUG)

FORMATTER = logging.Formatter("%(asctime)s %(levelname)-8s %(name)-10s: %(message)s")

HANDLER = logging.StreamHandler()
HANDLER.setLevel(logging.DEBUG)
HANDLER.setFormatter(FORMATTER)
WEB_LOGGER.addHandler(HANDLER)
