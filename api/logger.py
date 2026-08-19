#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import logging
import sys

logger = logging.getLogger("documind")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)


if __name__ == "__main__":

    logger.debug("Debug message")

    logger.info("Info message")

    logger.warning("Warning message")

    logger.error("Error message")

