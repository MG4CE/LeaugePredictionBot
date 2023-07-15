import sqlite3
from data.data_models import RegisteredServer, create_registered_server_obj

class ServersDataInterface:
    """
    A class to interface with server database table
    """
    
    def __init__(self, conn : sqlite3.Connection):
        self.conn = conn
        
        self.conn.execute('''CREATE TABLE IF NOT EXISTS servers
                             (discord_server_id INTEGER PRIMARY KEY NOT NULL,
                              channel_id        INTEGER,
                              admin_role_id     INTEGER,
                              command_modifier  TEXT);
                          ''')

    def create_server(self, server: RegisteredServer) -> int:
        cursor = self.conn.execute("INSERT INTO servers " +
                                   "(discord_server_id, channel_id, admin_role_id, command_modifier) " +
                                   "VALUES (?, ?, ?, ?)",
                                   (server.discord_server_id, server.channel_id, server.admin_role_id, server.command_modifier))
        self.conn.commit()
        return cursor.lastrowid

    def delete_server(self, discord_server_id: int) -> int:
        count = self.conn.execute("DELETE FROM servers WHERE discord_server_id = ?", (discord_server_id, )).rowcount
        self.conn.commit()
        return count

    def get_server(self, discord_server_id: int) -> RegisteredServer:
        cursor = self.conn.execute("SELECT * FROM servers WHERE discord_server_id = ?", (discord_server_id, ))
        row = cursor.fetchone()

        if row == None:
            return None

        return create_registered_server_obj(row[0],
                                            row[1],
                                            row[2],
                                            row[3])

    def update_channel_id(self, discord_server_id: int, channel_id: int) -> int:
        count = self.conn.execute("UPDATE servers SET channel_id = ? WHERE discord_server_id = ?", 
                                  (channel_id, discord_server_id)).rowcount
        self.conn.commit()
        return count

    def update_admin_role_id(self, discord_server_id: int, admin_role_id: int) -> int:
        count = self.conn.execute("UPDATE servers SET admin_role_id = ? WHERE discord_server_id = ?", 
                                  (admin_role_id, discord_server_id)).rowcount
        self.conn.commit()
        return count

    def update_command_modifier(self, discord_server_id: int, command_modifier: int) -> int:
        count = self.conn.execute("UPDATE servers SET command_modifier = ? WHERE discord_server_id = ?", 
                                  (command_modifier, discord_server_id)).rowcount
        self.conn.commit()
        return count
