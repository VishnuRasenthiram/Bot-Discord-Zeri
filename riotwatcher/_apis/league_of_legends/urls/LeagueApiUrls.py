from .LeagueEndpoint import LeagueEndpoint


class LeagueV4Endpoint(LeagueEndpoint):
    def __init__(self, url, **kwargs):
        nurl = f"/league/v4{url}"
        super().__init__(nurl, **kwargs)


class LeagueApiV4Urls:
    challenger_by_queue = LeagueV4Endpoint("/challengerleagues/by-queue/{queue}")
    grandmaster_by_queue = LeagueV4Endpoint("/grandmasterleagues/by-queue/{queue}")
    by_id = LeagueV4Endpoint("/leagues/{league_id}")
    master_by_queue = LeagueV4Endpoint("/masterleagues/by-queue/{queue}")
    by_puuid = LeagueV4Endpoint("/entries/by-puuid/{encrypted_puuid}")
    entries = LeagueV4Endpoint("/entries/{queue}/{tier}/{division}", page=int)
