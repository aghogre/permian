# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 14:15:37 2018

@author: ADMIN
"""
from govtjobssite_sourcecode import execution_govt
from rigzone_data_sourcing import execution_rigzone
from texas_data_sourcing import execution_texas
from mrt_Monster_data_sourcing import execution_monster
import logging.handlers
import logging
import time
import datetime
from config import argument_config

def get_logger(LOG_FORMAT     = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        LOG_NAME       = '',
        LOG_FILE_INFO  = 'file.log',
        LOG_FILE_ERROR = 'file.err',
        LEVEL=logging.INFO,
        ):
    
    log           = logging.getLogger(__name__)
    if not len(log.handlers):
        log_formatter = logging.Formatter(LOG_FORMAT)
    
        file_handler_error = logging.FileHandler('file.log', mode='w')
        file_handler_error.setFormatter(log_formatter)
        file_handler_error.setLevel(logging.INFO)
        log.addHandler(file_handler_error)
        
    #email sending
    smtp_handler = logging.handlers.SMTPHandler(mailhost=(argument_config.get('mailhost'), 25),
                                            fromaddr=argument_config.get('fromaddr'), 
                                            toaddrs=argument_config.get('toaddrs'),
                                            subject=argument_config.get('subject'),

                                            credentials=(argument_config.get('emailid'), argument_config.get('password')),
                                            secure=())
    smtp_handler.setLevel(logging.ERROR)
    log.addHandler(smtp_handler)

    return log

def main():
    try:
            # Calling govtjobssite_sourcing
            logger.info("Starting Sourcing for Government Jobs")
            execution_govt()

    except Exception as e:
        logger.error(str(datetime.today())+" Code need to be taken care for government Jobs. Code stopped from schedular "+str(e.message))
        pass
    try:
            # Calling Rigzone
            logger.info("Starting Sourcing for Rigzone Jobs")
            execution_rigzone()

    except Exception as e:
        logger.error(str(datetime.today())+" Code need to taken care be for Rigzone Jobs. Code stopped from schedular "+str(e.message))
        pass
    
    try:
            # Calling TexasBack To work
            logger.info("Starting Sourcing for Texasbacktowork Jobs")
            execution_texas()

    except Exception as e:
        logger.error(str(datetime.today())+" Code need to taken care for be Texas Back To work Jobs. Code stopped from schedular "+str(e.message))
        pass
    try:
            # Calling mrt_monster_sourcing
            logger.info("Starting Sourcing for Monster Jobs")
            execution_monster()

    except Exception as e:
        logger.error(str(datetime.today())+" Code need to be taken care for Monster Jobs. Code stopped from schedular "+str(e.message))
        
    logger.info("Going for 24 hrs of sleep")
    time.sleep(86400)

if __name__ == '__main__':
    logger = get_logger()
    main()
