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
        self._shows_path = self._config_path / "shows"

    @staticmethod
    def _get_config_key(config: dict[Any, Any], key: str, default: Any):
        if key not in config:
            return default

        value = config[key]
        if value is None or not value:
            return default

        if isinstance(value, str):
            if value.strip() == "":
                return default

        return value

    def get_program_config(self) -> dict[Any, Any]:
        """! Return the global program configuration.

        @return A dict containing the global program configuration.
        """

        config: dict[Any, Any] = {
            "tmdb": None,
            "email": {
                "host": "localhost",
                "port": 25,
                "from": "monitor_movie_show_releases <monitor_movie_show_releases@localhost>",
                "to": []
            },
            "movies": [],
            "shows": []
        }

        if not self._config_file.exists():
            return config

        with open(self._config_file, 'rb') as f:
            saved_config = json.load(f)

        config["tmdb"] = self._get_config_key(saved_config, "tmdb", config["tmdb"])
        config["movies"] = self._get_config_key(saved_config, "movies", config["movies"])
        config["shows"] = self._get_config_key(saved_config, "shows", config["shows"])

        if "email" in saved_config:
            config["email"]["host"] = self._get_config_key(saved_config["email"], "host", config["email"]["host"])
            config["email"]["port"] = self._get_config_key(saved_config["email"], "port", config["email"]["port"])
            config["email"]["from"] = self._get_config_key(saved_config["email"], "from", config["email"]["from"])
            config["email"]["to"] = self._get_config_key(saved_config["email"], "to", config["email"]["to"])

        if isinstance(config["email"]["to"], str):
            config["email"]["to"] = [config["email"]["to"]]

        return config

    def get_program_config_path(self) -> Path:
        """! Return the global program configuration path.

        @return A Path where to find the global program configuration.
        """

        return self._config_file

    def _get_movie_file(self, movie_id: int) -> Path:
        return self._movies_path / (str(movie_id) + ".json")

    def _get_show_file(self, show_id: int) -> Path:
        return self._shows_path / (str(show_id) + ".json")

    def _create_movie_path(self) -> None:
        self._movies_path.mkdir(parents=True, exist_ok=True)

    def _create_show_path(self) -> None:
        self._shows_path.mkdir(parents=True, exist_ok=True)

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

    def get_cached_show(self, show_id: int) -> dict[Any, Any]:
        """! Return the cached information for a single show.

        @param show_id  ID of the show.

        @return A dict with the cached show details.
        """

        show_file = self._get_show_file(show_id)
        if not show_file.exists():
            return {}

        with open(show_file, 'rb') as f:
            return json.load(f)

    def put_cached_show(self, show_id: int, show: dict[Any, Any]) -> None:
        """! Save the given show information into the cache.

        @param show_id  ID of the show.
        @param show     Movie information to cache.
        """

        self._create_show_path()

        show_file = self._get_show_file(show_id)
        with open(show_file, "w", encoding="utf-8") as f:
            json.dump(show, f, ensure_ascii=False)
