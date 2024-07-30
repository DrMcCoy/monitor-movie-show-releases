"""! Program configuration.
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

import json
from pathlib import Path
from typing import Any

from xdg import xdg_config_home

from util import PACKAGE_NAME


class Config:
    """! Program configuration.
    """

    def __init__(self) -> None:
        self._config_path = xdg_config_home() / PACKAGE_NAME
        self._config_file = self._config_path / "config.json"

        self._movies_path = self._config_path / "movies"

    def get_program_config(self) -> dict[Any, Any]:
        """! Return the global program configuration.

        @return A dict containing the global program configuration.
        """

        config = {}

        if self._config_file.exists():
            with open(self._config_file, 'rb') as f:
                config = json.load(f)

        if "tmdb" not in config or config["tmdb"] is None or config["tmdb"].strip() == "":
            config["tmdb"] = None
        if "email_from" not in config or not config["email_from"] or config["email_from"].strip() == "":
            config["email_from"] = "monitor_movie_show_releases"
        if "email_to" not in config or not config["email_to"] or config["email_to"].strip() == "":
            config["email_to"] = []
        if isinstance(config["email_to"], str):
            config["email_to"] = [config["email_to"]]
        if "sendmail" not in config or not config["sendmail"] or config["sendmail"].strip() == "":
            config["sendmail"] = "sendmail"
        if "movies" not in config or not config["movies"]:
            config["movies"] = []

        return config

    def get_program_config_path(self) -> Path:
        """! Return the global program configuration path.

        @return A Path where to find the global program configuration.
        """

        return self._config_file

    def _get_movie_file(self, movie_id: int) -> Path:
        return self._movies_path / (str(movie_id) + ".json")

    def _create_movie_path(self) -> None:
        self._movies_path.mkdir(parents=True, exist_ok=True)

    def get_cached_movie(self, movie_id: int) -> dict[Any, Any]:
        """! Return the cached information for a single movie.

        @param movie_id  ID of the movie.

        @return A dict with the cached movie details.
        """

        movie_file = self._get_movie_file(movie_id)
        if not movie_file.exists():
            return {}

        with open(movie_file, 'rb') as f:
            return json.load(f)

    def put_cached_movie(self, movie_id: int, movie: dict[Any, Any]) -> None:
        """! Save the given movie information into the cache.

        @param movie_id  ID of the movie.
        @param movie     Movie information to cache.
        """

        self._create_movie_path()

        movie_file = self._get_movie_file(movie_id)
        with open(movie_file, "w", encoding="utf-8") as f:
            json.dump(movie, f, ensure_ascii=False)
