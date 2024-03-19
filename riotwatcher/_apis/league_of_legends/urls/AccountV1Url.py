#https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/zRjDt32ZFw-wWT-8-g4o6XW24plv8zPqnyVu35z08dcioqxNMI047LShzsoIIKxzWqnkuJd_A7Rowg?api_key=RGAPI-640b86d9-f433-4649-9168-54cbb2af604d
#https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/aladdin/rakan?api_key=RGAPI-640b86d9-f433-4649-9168-54cbb2af604d
from .LeagueEndpoint2 import LeagueEndpoint2

class AccountV1Endpoint(LeagueEndpoint2):
    def __init__(self, url, **kwargs):
        nurl = f"/account/v1/accounts{url}"
        super().__init__(nurl, **kwargs)    


class AccountV1Urls:
    by_RiotId = AccountV1Endpoint("/by-riot-id/{name}/{tagline}")
    by_puuid = AccountV1Endpoint("/by-puuid/{encrypted_puuid}")
