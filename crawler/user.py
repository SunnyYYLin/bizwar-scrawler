import os
import json
from faker import Faker

class User:
    def __init__(self, nickname=None):
        if nickname:
            config = self.read_config(nickname)
            self.email = config['email']
            self.password = config['password']
            self.nickname = config['nickname']
            self.school_name = config['school_name']
            self.class_name = config['class_name']
            self.number = config['number']
            self.phone = config['phone']
            self.team_name = config['team_name']
            self.games: list[str] = config['games'] if 'games' in config else []
            self.team_id: str = config['team_id'] if 'team_id' in config else None
        else:
            reg_data = self.generate_register_data()
            self.email = reg_data['user[login]']
            self.password = reg_data['password1']
            self.nickname = reg_data['user[nickname]']
            self.school_name = reg_data['user[school_name]']
            self.class_name = reg_data['user[class_name]']
            self.number = reg_data['user[number]']
            self.phone = reg_data['user[phone]']
            self.team_name = self.generate_team_name()
            self.games = {}
        
    def __str__(self):
        return self.nickname
    
    def read_config(self, nickname):
        with open(os.path.join("configs", f"{nickname}.json"), "r") as f:
            config = json.load(f)
        return config
    
    def save_config(self):
        assert self.email is not None, "Email is not set"
        assert self.password is not None, "Password is not set"
        with open(os.path.join("configs", f"{self.nickname}.json"), 'w') as f:
            json.dump(self.config, f, indent=4)
    
    @staticmethod
    def generate_register_data():
        fake = Faker()
        password = fake.password()
        nickname = fake.user_name()
        email = nickname + "@gmail.com"
        school_name = fake.company()
        class_name = fake.word()
        number = str(fake.random_int(min=10000000, max=99999999))
        phone = fake.random_int(min=13000000000, max=19999999999)

        form_data = {
            'user[login]': email,
            'password1': password,
            'password2': password,
            'user[nickname]': nickname,
            'user[school_name]': school_name,
            'user[class_name]': class_name,
            'user[number]': number,
            'user[phone]': phone,
        }
        return form_data
    
    @staticmethod
    def generate_team_name():
        fake = Faker()
        team_name = fake.company()
        team_name = ''.join(filter(str.isalnum, team_name))  # Remove special characters
        if len(team_name) > 15:
            team_name = team_name[:15]
        return team_name
    
    @property
    def config(self) -> dict:
        return self.__dict__
        
    @property
    def reg_data(self) -> dict:
        return {
            'user[login]': self.email,
            'password1': self.password,
            'password2': self.password,
            'user[nickname]': self.nickname,
            'user[school_name]': self.school_name,
            'user[class_name]': self.class_name,
            'user[number]': self.number,
            'user[phone]': self.phone,
        }
        
    @property
    def team_data(self) -> dict:
        return {
            'utf8': '✓',
            'team[name]': self.team_name,
            'commit': '创建'
        }
        
    @property
    def login_data(self) -> dict:
        return {
            'name': self.email,
            'password': self.password
        }
    
    @property
    def decision_url(self):
        return f"http://bizwar.cn/games/decision?gameid={self.game_id}\
            &type=raw&teamid={self.team_id}&mode=old"