# -*- coding: utf-8 -*-
"""
Created on Tue Aug 21 09:27:17 2018

@author: Anshul
"""

import os

argument_config = {
    'azure_account_name': os.getenv('AZURE_ACCOUNT_NAME', 'randomtrees'),
    'azure_account_key': os.getenv('AZURE_ACCOUNT_KEY', 'wvNLlB2cSHhB0OFPRhIQDv+1QBJ1CnwFt+AGfQnL8rTyKTCG90t1Z+aCepe25aol6CKneJYgvHJl5gMtHON7TQ=='),
    'azure_container': os.getenv('CONTAINER', 'tsnv'),
    'neo4j_host': os.getenv('NEO4J_HOST', 'http://Graph:test@localhost:7474'),
    
}

       