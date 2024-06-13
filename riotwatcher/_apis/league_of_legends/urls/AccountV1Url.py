from .LeagueEndpoint2 import LeagueEndpoint2

class AccountV1Endpoint(LeagueEndpoint2):
    def __init__(self, url, **kwargs):
        nurl = f"/account/v1/accounts{url}"
        super().__init__(nurl, **kwargs)    


class AccountV1Urls:
    by_RiotId = AccountV1Endpoint("/by-riot-id/{name}/{tagline}")
    by_puuid = AccountV1Endpoint("/by-puuid/{encrypted_puuid}")
