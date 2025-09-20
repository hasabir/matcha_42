from ..dbmanager import DBManager
import logging
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)



class Search(DBManager):
    def __init__(self, connection_pool):
        super().__init__(connection_pool)