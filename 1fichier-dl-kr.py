import os
import sys
import logging
import atexit
from core.gui import gui

log_level = logging.DEBUG

if getattr(sys, 'frozen', False):
    log_dir = os.path.join(os.path.dirname(sys.executable), 'app')
    log_level = logging.INFO
else:
    log_dir = os.path.join(os.path.dirname(__file__), 'app')

def global_exception_handler(exctype, value, traceback):
    logger = logging.getLogger(__name__)
    logger.error(f"Uncaught exception: {value}")
    if app and app.actions:
        app.actions.handle_exit()
    sys.__excepthook__(exctype, value, traceback)

if __name__ == '__main__':
    app = None
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = os.path.join(log_dir, 'logs.txt')

        logging.basicConfig(filename=log_file, level=log_level, filemode='w')
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
        logger = logging.getLogger(__name__)

        sys.excepthook = global_exception_handler

        app = gui.Gui()

        # 종료 시 캐시 저장 강화
        def save_cache_on_exit():
            try:
                if app and app.actions:
                    app.actions.handle_exit()
            except Exception as e:
                logger.error(f"Error saving cache on exit: {e}")

        atexit.register(save_cache_on_exit)
        
    except Exception as e:
        if app and app.actions:
            app.actions.handle_exit()
        logger = logging.getLogger(__name__)
        logger.debug(__name__+' Exception')
        logger.exception(e)
