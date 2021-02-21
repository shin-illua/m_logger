import time
import logging 
import argparse
import threading
import multiprocessing
import logging.handlers

# Static 
_logger = logging.getLogger()

LISTENER_KILL_MSG = "$____KILL_SERVER____$"

debug = logging.debug 
info = logging.info 
warning = logging.warning 
error = logging.error 
critical = logging.critical 

class LoggerAdapter(logging.LoggerAdapter):
    def __init__(self, logger, prefix):
        super(LoggerAdapter, self).__init__(logger, {})
        self.prefix = prefix

    def process(self, msg, kwargs):
        return '%s %s' % (self.prefix, msg), kwargs


def initLogger(
    name=__name__,              
    level=logging.DEBUG,          
    logFile=None, 
    logFileMode='a+', 
    logFileLevel=logging.WARNING,
    mpQueue=None, 
    prepend=None
): 
    """ Initialize logger object 
    
    Args (All argument is Optional): 
        name: 
            The name of the logger object to initialize 
        level: 
            Log level for console handler. 
        logFile: 
            Log file location in disl.  
        logFileMode: 
            The log file `open` mode.
        logFileLevel: 
            Log level for file handler. 
        mpQueue: 
            Multiprocessing queue object for multiprocessing logging 
            events. 
        prepend: 
            A string to prepend to every log event messages. 

    Returns: 
        The initialized logger object. 
    """ 
    global _logger, debug, info, warning, error, critical 

    # Get logger 
    logger = logging.getLogger(name)
    
    # Build formatter 
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s", 
        "%d-%b-%y %H:%M:%S"
    )

    # Build and add file log handler    
    if logFile != None: 
        fileHandler = logging.FileHandler(logFile, logFileMode)
        fileHandler.setFormatter(formatter)
        # Only WARNING events and higher will be written to log file.  
        fileHandler.setLevel(logFileLevel)

    # Build console log handler 
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    consoleHandler.setLevel(level)
    logger.addHandler(consoleHandler)

    # Build and add queue handler (for multiprocessing)
    if mpQueue != None:
        queueHandler = logging.handlers.QueueHandler(mpQueue)
        logger.addHandler(queueHandler)

    # Set log level for logger 
    logger.setLevel(level)

    if prepend: 
        logger = LoggerAdapter(
            logger, 
            prepend
        )

    debug = logger.debug 
    info = logger.info 
    warning = logger.warning
    error = logger.error 
    critical = logger.critical

    _logger = logger 

    return logger 

def listen(mpQueue, logger): 
    """ Worker function to listen and emit log events
    
    Args: 
        mpQueue: 
            multiprocessing queue object to listen log events from. 
        logger: 
            The logger object that will handle received log events. 

    """
    stop = False
    while not stop:
        time.sleep(0.001)   # I've known this to lessen cpu usage :)
        while not mpQueue.empty():
            time.sleep(0.001)
            try:
                record = mpQueue.get()
                if ( record.levelno == logging.INFO 
                    and LISTENER_KILL_MSG == record.getMessage()
                ):
                    # Stop signal 
                    stop = True
                    break 
                logger.handle(record)
            except:
                import traceback 
                print("Logger logistener exception!")
                print(traceback.format_exc())  
                  
def initLogListener(logger=None):
    """ Initialize log events listener

    Args: 
        logger (Optional): 
            The logger that will handle the log events. 

    Returns: 
        The multiprocessing queue object that child processes can use 
        to send log events to the listener. 
    """
    global _logger 
    if logger == None: 
        logger = _logger
    mpQueue = multiprocessing.Queue()
    threading.Thread(target=listen, args=(mpQueue, logger)).start()
    return mpQueue

def killListener(mpQueue): 
    """ Kill listener thread 

    Args: 
        mpQueue: 
            The queue in which the listener thread to kill is listening 
            from. 
    
    """
    _logger = initLogger("__listener_killer__", mpQueue=mpQueue)
    _logger.info(LISTENER_KILL_MSG)

    