from crawler.user import User
from crawler.crawler import Crawler, InfoPage
from crawler.info import InfoParser
from bs4 import BeautifulSoup
import os

first_period = 3206314

if __name__ == "__main__":
    user = User("刘宇")
    game_id = user.games[0]
    crawler = Crawler(user)
    crawler.login()
    crawler.get_game(game_id)
    period_ids = [0] + [first_period + i for i in range(10)]
    RENDERS = [None, 'public_report_finance', 'public_report_finance', 'public_report_rank']
    if not os.path.exists("data"):
        os.mkdir("data")
    
    for period_id in period_ids:
        for render in RENDERS:
            info_page = InfoPage(
                game_id=game_id,
                period_id=period_id,
                team_id=user.team_id,
                render=render
            )
            print(info_page)
            info_response = crawler.get_infopage(info_page)
            parser = InfoParser(BeautifulSoup(info_response.text, 'lxml'))
            dataframe = parser.parse()
            dataframe.to_csv(f"data/{info_page.abbr(first_period-1)}.csv", index=False)
            