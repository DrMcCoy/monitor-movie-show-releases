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

        response = requests.get(url, timeout=5, headers=headers)
        response.raise_for_status()

        return response.json()

    def _try_auth(self) -> None:
        print("Trying to authenticate with TMDB...")

        try:
            response = self._query("authentication")
            if "success" not in response:
                raise RuntimeError("Response has no success value")
            if not response["success"]:
                raise RuntimeError("Response yielded no success")
        except (requests.exceptions.HTTPError, RuntimeError) as error:
            raise RuntimeError(f"Failed to authenticate with TMDB: {error}") from error
