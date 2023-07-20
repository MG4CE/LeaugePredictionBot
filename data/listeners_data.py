import sqlite3
from data.data_models import Listener, create_listener_obj
from typing import List

NULL_LISTENER_ID = -1

class ListenersDataInterface:
    """
    A class to interface with listeners database table
    """
    
    def __init__(self, conn : sqlite3.Connection) -> None:
        self.conn = conn
        
        self.conn.execute('''CREATE TABLE IF NOT EXISTS listeners
                             (id                    INTEGER PRIMARY KEY AUTOINCREMENT,
                              game_name             TEXT NOT NULL,
                              discord_server_id     INTEGER  NOT NULL,
                              discord_user_id       INTEGER  NOT NULL,
                              game_account_username TEXT NOT NULL,
                              game_account_id       TEXT,
                              game_puuid            TEXT);
                          ''')

    def create_listener(self, listener: Listener) -> int:
        cursor = self.conn.execute("INSERT INTO listeners " +
                                   "(game_name, discord_server_id, discord_user_id, game_account_username, game_account_id, game_puuid) " +
                                   "VALUES (?, ?, ?, ?, ?)",
                                   (listener.game_name, listener.discord_server_id, listener.discord_user_id, listener.game_account_username, listener.game_account_id, listener.game_puuid))
        self.conn.commit()
        return cursor.lastrowid

    def delete_listener(self, id: int) -> int:
        count =  self.conn.execute("DELETE FROM listeners WHERE id = ?", (id,)).rowcount
        self.conn.commit()
        return count

    def get_listener(self, id: int) -> Listener:
        cursor = self.conn.execute("SELECT * FROM listeners WHERE id = ?", (id,))
        row = cursor.fetchone()

        if row == None:
            return None

        return create_listener_obj(row[0],
                                   row[1],
                                   row[2],
                                   row[3],
                                   row[4],
                                   row[5],
                                   row[6])

    def get_all_listeners(self) -> List[Listener]:
        cursor = self.conn.execute("SELECT * FROM listeners")
        rows = cursor.fetchall()
        
        listener_list = []

        for row in rows:
            listener_list.append(create_listener_obj(row[0],
                                                     row[1],
                                                     row[2],
                                                     row[3],
                                                     row[4],
                                                     row[5],
                                                     row[6]))
        
        return listener_list

    def get_all_game_listeners(self, game_name: str) -> List[Listener]:
        cursor = self.conn.execute("SELECT * FROM listeners WHERE game_name = ?", (game_name,))
        rows = cursor.fetchall()
        
        listener_list = []

        for row in rows:
            listener_list.append(create_listener_obj(row[0],
                                                     row[1],
                                                     row[2],
                                                     row[3],
                                                     row[4],
                                                     row[5],
                                                     row[6]))
    
        return listener_list

    def get_all_server_listeners(self, discord_server_id: int) -> List[Listener]:
        cursor = self.conn.execute("SELECT * FROM listeners WHERE discord_server_id = ?", (discord_server_id,))
        rows = cursor.fetchall()
        
        listener_list = []

        for row in rows:
            listener_list.append(create_listener_obj(row[0],
                                                     row[1],
                                                     row[2],
                                                     row[3],
                                                     row[4],
                                                     row[5],
                                                     row[6]))
    
        return listener_list

    def get_all_user_listener(self, discord_user_id: int) -> List[Listener]:
        cursor = self.conn.execute("SELECT * FROM listeners WHERE discord_user_id = ?", (discord_user_id,))
        rows = cursor.fetchall()
        
        listener_list = []

        for row in rows:
            listener_list.append(create_listener_obj(row[0],
                                                     row[1],
                                                     row[2],
                                                     row[3],
                                                     row[4],
                                                     row[5],
                                                     row[6]))
    
        return listener_list
    
    def get_user_listener(self, discord_user_id: int, discord_server_id: int, username: str, game_name: str) -> Listener:
        cursor = self.conn.execute("SELECT * FROM listeners WHERE discord_user_id = ? AND discord_server_id = ? AND game_name = ? AND game_account_username = ?", (discord_user_id, discord_server_id, game_name, username))    
        row = cursor.fetchone()

        if row == None:
            return None
        
        return create_listener_obj(row[0],
                                   row[1],
                                   row[2],
                                   row[3],
                                   row[4],
                                   row[5],
                                   row[6])

    