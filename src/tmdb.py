"""! Interacting with The Movie Database (TMDB).
"""

# Monitor Movie and Show Releases - Monitor future movie and TV show releases
#
# Monitor Movie and Show Releases is the legal property of its developers,
# whose names can be found in the AUTHORS file distributed with this source
# distribution.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Any

import requests
from requests.adapters import HTTPAdapter, Retry


class TMDB:  # pylint: disable=too-few-public-methods
    """! Interacting with The Movie Database (TMDB).
    """

    def __init__(self, bearer: str) -> None:
        self._bearer: str = bearer
        self._try_auth()

    def _query(self, endpoint: str, path_params: list[str] | None = None,
               query_params: dict[Any, Any] | None = None) -> dict[Any, Any]:

        path_params_str = ""
        if path_params:
            path_params_str = "/" + "/".join(path_params)

        query_params_str = ""
        if query_params:
            query_params_str = "?" + "&".join([f"{key}={value}" for key, value in query_params.items()])

        url = f"https://api.themoviedb.org/3/{endpoint}{path_params_str}{query_params_str}"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self._bearer}"
        }

        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))

        response = session.get(url, timeout=5, headers=headers)
        response.raise_for_status()

        if response.text == "":
            return {}

        return response.json()

    def _try_auth(self) -> None:
        print("Trying to authenticate with TMDB...")

        try:
            response = self._query("authentication")
            if "success" in response and not response["success"]:
                raise RuntimeError("Response yielded no success")
        except (requests.exceptions.HTTPError, RuntimeError) as error:
            raise RuntimeError(f"Failed to authenticate with TMDB: {error}") from error

    def get_movie(self, movie_id: int, with_releases: bool = True, language: str | None = None) -> dict[Any, Any]:
        """! Query TMDB for details about a movie.

        @param movie_id       ID of the movie on TMDB.
        @param with_releases  Add information about releases of the movie.
        @param language       For which language to query.

        @return A dict with details about the movie.
        """

        try:
            query_params: dict[Any, Any] | None = {}

            assert query_params is not None
            if language is not None:
                query_params["language"] = language
            if with_releases:
                query_params["append_to_response"] = "release_dates"

            if not query_params:
                query_params = None

            response = self._query("movie", path_params=[str(movie_id)], query_params=query_params)
            return response

        except requests.exceptions.HTTPError as error:
            raise RuntimeError(f"Failed to get movie: {error}") from error

    def get_show(self, show_id: int, language: str | None = None) -> dict[Any, Any]:
        """! Query TMDB for details about a show.

        @param show_id   ID of the show on TMDB.
        @param language  For which language to query.

        @return A dict with details about the show.
        """

        try:
            query_params: dict[Any, Any] | None = {}

            assert query_params is not None
            if language is not None:
                query_params["language"] = language

            if not query_params:
                query_params = None

            response = self._query("tv", path_params=[str(show_id)], query_params=query_params)
            return response

        except requests.exceptions.HTTPError as error:
            raise RuntimeError(f"Failed to get show: {error}") from error
