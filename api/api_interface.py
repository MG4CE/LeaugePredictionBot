from abc import ABC, abstractmethod

class GameInterface(ABC):

    @abstractmethod
    def get_account_data(self, username: str) -> dict:
        pass

    @abstractmethod
    def is_user_in_game(self, account_id: str) -> bool:
        pass

    @abstractmethod
    def get_user_current_match(self, account_id: str) -> dict:
        pass

    @abstractmethod
    def is_match_done(self, account_id: str) -> bool:
        pass

    @abstractmethod
    def get_user_rank(self, account_id: str) -> str:
        pass
