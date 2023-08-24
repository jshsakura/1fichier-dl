#!/usr/bin/env python3
import os
import sys
import logging
from core.gui import gui

if __name__ == '__main__':
    try:
        logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), 'logs'),
                            level=logging.DEBUG, filemode='w')
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
        logger = logging.getLogger(__name__)
        gui.Gui()
    except Exception as e:
        logger.exception(e)
