""" 
You can run this as: 

pytest -s test
"""

import multiprocessing as mp 
import m_logger as log
import time
import os 

def test_logger(): 
    log.initLogger()

    log.debug("Debug message")
    log.info("Info message")
    log.warning("Warning message")
    log.error("Error message")
    log.critical("Critical message")

def test_logger_prepend(): 
    log.initLogger(name="test_logger_prepend", prepend="PREPEND")

    log.debug("Debug message")
    log.info("Info message")
    log.warning("Warning message")
    log.error("Error message")
    log.critical("Critical message")    


def test_logger_multiprocessing(): 
    log.initLogger(name="_logger_test_multi")
    mpQueue = log.initLogListener()

    workers = []
    for i in range(5):
        p = mp.Process(
            target=_multiprocessing_log_worker, 
            args=(i, mpQueue)
        )
        p.start()
        workers.append(
            p
        )

    for w in workers: 
        w.join()

    logger = log.initLogger("kill_listeners", mpQueue=mpQueue)
    logger.info(log.LISTENER_KILL_MSG)


def _multiprocessing_log_worker(workerId, mpQueue): 
    log.initLogger(
        mpQueue=mpQueue, 
        prepend="Worker {} PID: {}".format(workerId, os.getpid())
    )

    log.debug("Multiprocessing - Debug message")
    log.info("Multiprocessing - Info message")
    log.warning("Multiprocessing - Warning message")
    log.error("Multiprocessing - Error message")
    log.critical("Multiprocessing - Critical message")

    time.sleep(3)

if __name__ == "__main__": 
    test_logger()