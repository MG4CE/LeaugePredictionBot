import sqlite3
from data.listeners_data import ListenersDataInterface
from data.servers_data import ServersDataInterface
from data.stats_data import StatsDataInterface

# TODO: the way DB access and management is done is here autistic, make it better

class DatabaseController:
    """
    A class to manage SQLite database tables
    """
    
    def __init__(self, conn : sqlite3.Connection) -> None:
        self.conn = conn
        self.listeners = ListenersDataInterface(self.conn)
        self.servers = ServersDataInterface(self.conn)
        self.user_stats = StatsDataInterface(self.conn)
