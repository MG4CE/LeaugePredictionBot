import sqlite3
from loguru import logger
from data.data_models import UserStats, create_user_stats_obj
from typing import List

class StatsDataInterface:
    """
    A class to interface with stats database table
    """
    
    def __init__(self, conn : sqlite3.Connection):
        self.conn = conn
        
        self.conn.execute('''CREATE TABLE IF NOT EXISTS user_stats
                             (id                    INTEGER  PRIMARY KEY AUTOINCREMENT,
                              discord_user_id       INTEGER  NOT NULL,
                              discord_server_id     INTEGER  NOT NULL,
                              score                 INTEGER  NOT NULL,
                              correct_predictions   INTEGER  NOT NULL,
                              wrong_predictions     INTEGER  NOT NULL);
                          ''')

    def create_user(self, user: UserStats) -> int:
        logger.debug("create_user for server_id: " + str(user.discord_server_id) + " user_id: " + str(user.discord_user_id) + " from db")
        cursor = self.conn.execute("INSERT INTO user_stats " +
                                   "(discord_user_id, discord_server_id, score, correct_predictions, wrong_predictions) " +
                                   "VALUES (?, ?, ?, ?, ?)",
                                   (user.discord_user_id, user.discord_server_id, user.score, user.correct_predictions, user.wrong_predictions))
        self.conn.commit()
        return cursor.lastrowid
    

    def delete_user_by_id(self, id: int) -> int:
        logger.debug("delete_user_by_id id: " + str(id) + " from db")
        count = self.conn.execute("DELETE FROM user_stats WHERE id = ?", (id, )).rowcount
        self.conn.commit()
        return count

    def delete_user_by_discord_ids(self, user_id: int, server_id: int) -> int:
        logger.debug("delete_user_by_discord_ids user_id: " + str(user_id) + " server_id: " + str(server_id) + " from db")
        count = self.conn.execute("DELETE FROM user_stats WHERE discord_user_id = ? AND discord_server_id = ?", 
                                 (user_id, server_id)).rowcount
        self.conn.commit()
        return count

    def get_user_by_id(self, id: int) -> UserStats:
        logger.debug("get_user_by_id id: " + str(id) + " from db")
        cursor = self.conn.execute("SELECT * FROM user_stats WHERE id = ?", (id,))
        row = cursor.fetchone()

        if row == None:
            return None

        return create_user_stats_obj(row[0],
                                     row[1],
                                     row[2],
                                     row[3],
                                     row[4],
                                     row[5])

    def get_user_by_discord_id(self, user_id: int, server_id: int) -> UserStats:
        logger.debug("get_user_by_discord_id user_id: " + str(user_id) + " server_id: " + str(server_id) + " from db")
        cursor = self.conn.execute("SELECT * FROM user_stats WHERE discord_user_id = ? AND discord_server_id = ?", (user_id, server_id))
        row = cursor.fetchone()

        if row == None:
            return None

        return create_user_stats_obj(row[0],
                                     row[1],
                                     row[2],
                                     row[3],
                                     row[4],
                                     row[5])

    def update_user_stats(self, id :int, correct_predictions: int, wrong_predictions: int, score: int) -> int:
        logger.debug("update_user_stats id: " + str(id) + " correct_predictions: " + str(correct_predictions) + " wrong_predictions: " + str(wrong_predictions) + " score: " + str(score) + " from db")
        count = self.conn.execute("UPDATE user_stats SET score = ?, correct_predictions = ?, wrong_predictions = ? WHERE id = ?", 
                                 (score, correct_predictions, wrong_predictions, id)).rowcount
        self.conn.commit()
        return count
    
    def get_top_user_score_list(self, num_entries: int) -> List[UserStats]:
        logger.debug("get_top_user_score_list from db")
        cursor = self.conn.execute("SELECT * FROM user_stats ORDER BY score DESC LIMIT ?", (num_entries, ))
        rows = cursor.fetchall()
        
        top_score_users = []

        for row in rows:
            top_score_users.append(create_user_stats_obj(row[0],
                                                         row[1],
                                                         row[2],
                                                         row[3],
                                                         row[4],
                                                         row[5]))
            
        return top_score_users
