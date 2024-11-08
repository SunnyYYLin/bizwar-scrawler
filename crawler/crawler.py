import re
import requests
from bs4 import BeautifulSoup
from .user import User
from .const import PARTS, SUBMIT_VALUES
from dataclasses import dataclass

base_url = "http://bizwar.cn/"

@dataclass
class InfoPage:
    team_id: int
    game_id: int
    period_id: int
    render: str|None
    
    @property
    def url(self):
        suffix = f"games/public_report?gameid={self.game_id}&periodid={self.period_id}&teamid={self.team_id}"
        suffix += f"&render={self.render}" if self.render is not None else ""
        return base_url + suffix
    
    def abbr(self, base_period: int = None) -> str:
        render = self.render if self.render else "orders"
        if base_period is None or self.period_id < base_period:
            abbr = f"{self.team_id}_{self.game_id}_{self.period_id}_{render}"
        else:
            abbr = f"{self.team_id}_{self.game_id}_{self.period_id - base_period}_{render}"
        return abbr
            

class Crawler:
    def __init__(self, user: User|None = None) -> None:
        self.user = User() if user is None else user
        self.session = requests.Session()
        self.is_login = False
        self.game_id = None
    
    def _get_form(self, form_url):
        try:
            response = self.session.get(base_url + form_url)
        except Exception as e:
            print("An error occurred when getting:", str(e))
            
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            form = soup.find('form', {'method': 'post'})
            return form
        else:
            print("Failed to get the form page with status code:", response.status_code)
            
    def _get_hidden(self, form):
        hidden_fields = form.find_all('input', {'type': 'hidden'})
        hidden_data = {}
        for field in hidden_fields:
            hidden_data[field['name']] = field['value']
        return hidden_data
    
    def register(self):
        reg_url = "/users/new"
        f = self._get_form(reg_url)
        action_url = base_url + f['action']
        data = self._get_hidden(f)
        data.update(self.reg_data)
        response = self.session.post(action_url, data=data)
        self.is_login = True
        return response
    
    def create_team(self):
        new_team_url = "/teams/new"
        f = self._get_form(new_team_url)
        action_url = base_url + f['action']
        data = self._get_hidden(f)
        data.update(self.team_data)
        response = self.session.post(action_url, data=data)
        return response
    
    def login(self):
        login_url = "/main/login"
        f = self._get_form(login_url)
        action_url = base_url + f['action']
        data = self._get_hidden(f)
        data.update(self.user.login_data)
        response = self.session.post(action_url, data=data)
        self.user.user_id = response.url.split('/')[-1]
        self.is_login = True
        self.user.save_config()
        return response
    
    def create_game(self):
        assert self.is_login, "User is not logged in"
        game_url = "/games/new_machine"
        f = self._get_form(game_url)
        action_url = base_url + f['action']
        data = {
            'utf8': '✓',
            'game[template_id]': '1',
            'commit': '创建'
        }
        data.update(self._get_hidden(f))
        response = self.session.post(action_url, data=data)
        response.raise_for_status()
        match = re.search(r'gameid=(\d+)&.*teamid=(\d+)', response.url)
        if match:
            self.user.games.update({match.group(1): self.get_period(match.group(1))})
            self.user.team_id = match.group(2) if self.user.team_id is None \
                else self.user.team_id
            self.user.save_config()
            return response
        else:
            print("No match found.")
    
    def get_period(self, game_id):
        response = self.get_game(game_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        period = soup.find('input', {'name': 'decision[period_id]'})['value']
        return int(period)
    
    def get_game(self, game_id):
        game_url = base_url + f"/games/decision?gameid={game_id}&type=raw&teamid={self.user.team_id}&mode=old"
        response = self.session.get(game_url)
        return response
    
    def get_infopage(self, info_page: InfoPage) -> requests.Response:
        response = self.session.get(info_page.url)
        return response
    
    def submit(self, part, inputs, auth):
        submit_url = self.submit_url()
        data = {
            'commit': SUBMIT_VALUES[part],
            'utf8': '✓',
            'authenticity_token': auth,
            }
        for dic_name, dic in inputs.items():
            for key in dic.keys():
                data[f'{dic_name}[{key}]'] = inputs[dic_name][key]
        response = self.session.post(submit_url, data=data)
        return response
            
    def submit_url(self):
        return base_url + f"/games/make_decision?&mode=old&teamid={self.user.team_id}"