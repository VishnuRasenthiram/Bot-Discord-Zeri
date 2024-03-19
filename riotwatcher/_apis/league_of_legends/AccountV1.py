from .. import BaseApi, NamedEndpoint
from .urls import AccountV1Urls


class AccountV1(NamedEndpoint):
    """
    This class wraps the Summoner-v4 endpoint calls provided by the Riot API.

    See https://developer.riotgames.com/api-methods/#summoner-v4 for more detailed
    information
    """

    def __init__(self, base_api: BaseApi):
        """
        Initialize a new SummonerApiV4 which uses the provided base_api

        :param BaseApi base_api: the root API object to use for making all requests.
        """
        super().__init__(base_api, self.__class__.__name__)


    def by_riotid(self, region: str, summoner_name: str,tagline:str):
        """
        Get a summoner by summoner name

        :param string region:           The region to execute this request on
        :param string summoner_name:    Summoner Name

        :returns: SummonerDTO: represents a summoner
        """
        return self._request_endpoint(
            self.by_riotid.__name__,
            region,
            AccountV1Urls.by_RiotId,
            name=summoner_name,
            tagline=tagline,
        )

    def by_puuid(self, region: str, encrypted_puuid: str):
        """
        Get a summoner by PUUID.

        :param string region:           The region to execute this request on
        :param string encrypted_puuid:  PUUID

        :returns: SummonerDTO: represents a summoner
        """
        return self._request_endpoint(
            self.by_puuid.__name__,
            region,
            AccountV1Urls.by_puuid,
            encrypted_puuid=encrypted_puuid,
        )

