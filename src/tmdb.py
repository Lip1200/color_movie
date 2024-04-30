import requests


class TMDB:
    base_url = "https://api.themoviedb.org/3"

    def __init__(self, api_key):
        self.api_key = api_key

        self.__validate_api_key()

    ### Movies

    def list_popular_movies(self, language="en-US", page=1, region=""):
        return self.__base_request(
            "/movie/popular", {"language": language, "page": page, "region": region}
        )

    def list_top_rated_movies(self, language="en-US", page=1, region=""):
        return self.__base_request(
            "/movie/top_rated", {"language": language, "page": page, "region": region}
        )

    def get_movie(self, movie_id, append_to_response="", language="en-US"):
        return self.__base_request(
            f"/movie/{movie_id}",
            {"append_to_response": append_to_response, "language": language},
        )

    def get_movies_credits(self, movie_id, language="en-US"):
        return self.__base_request(f"/movie/{movie_id}/credits", {"language": language})

    ### TV

    def list_popular_tv(self, language="en-US", page=1):
        return self.__base_request("/tv/popular", {"language": language, "page": page})

    def list_top_rated_tv(self, language="en-US", page=1):
        return self.__base_request("/tv/top_rated", {"language": language, "page": page})

    def get_tv(self, series_id, append_to_response="", language="en-US"):
        return self.__base_request(
            f"/tv/{series_id}",
            {"append_to_response": append_to_response, "language": language},
        )

    def get_tv_credits(self, series_id, language="en-US"):
        return self.__base_request(
            f"/tv/{series_id}/credits", {"language": language}
        )

    def get_person(self, person_id, append_to_response="", language="en-US"):
        return self.__base_request(
            f"/person/{person_id}",
            {"append_to_response": append_to_response, "language": language},
        )

    def __validate_api_key(self):
        res = self.__base_request("/authentication")
        if not res.get("success"):
            raise requests.exceptions.HTTPError("Invalid API key")

    def __base_request(self, path: str, params: dict[str, str] = {}):
        url = self.base_url + path
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        response = requests.get(url, params=params, headers=headers)

        if not response.ok:
            response.raise_for_status()

        return response.json()
