"""! The actual Monitor Movie and Show Releases logic.
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

from enum import IntEnum
from typing import Any

import dictdiffer

from tmdb import TMDB


class ReleaseType(IntEnum):
    """! Different types of releases.
    """
    # pylint: disable=invalid-name
    Premiere = 1
    LimitedTheatrical = 2
    Theatrical = 3
    Digital = 4
    Physical = 5
    TV = 6


class MonitorMovieShowReleases:  # pylint: disable=too-few-public-methods
    """! Monitor Movie and Show Releases logic.
    """

    def __init__(self) -> None:
        self._tmdb: TMDB | None = None

    @staticmethod
    def _format_movie_change(movie_old: dict[Any, Any], movie_new: dict[Any, Any]) -> tuple[bool, str, str]:
        movie_diff = list(dictdiffer.diff(movie_old, movie_new))
        if not movie_diff:
            return False, "", ""

        subject = f'Change in movie "{movie_new["title"]}" ({movie_new["id"]})'

        body = ''
        body += f'Title: {movie_new["title"]}\n'
        body += f'Status: {movie_new["status"]}\n\n'
        for release in movie_new["release_dates"]:
            body += f'Release({release["type"]}, {release["iso_639_1"]}): {release["release_date"]}\n'

        body += '\n'
        body += '------\n'
        body += '\n'
        for diff in movie_diff:
            body += str(diff)

        return True, subject, body

    @staticmethod
    def _describe_release_type(type_id: int) -> str:
        if type_id not in ReleaseType:
            return "Unknown"

        return ReleaseType(type_id).name

    @staticmethod
    def _filter_release_dates_by_country(movie: dict[Any, Any], country: str) -> list[dict[Any, Any]]:
        if "release_dates" not in movie or "results" not in movie["release_dates"]:
            return []

        country_releases = list(filter(lambda r: r["iso_3166_1"] == country, movie["release_dates"]["results"]))
        if not country_releases:
            return []

        releases = country_releases[0]["release_dates"]
        for release in releases:
            release["type"] = MonitorMovieShowReleases._describe_release_type(release["type"])
            release["iso_639_1"] = country

        return releases

    def _get_movie_info(self, movie_id: int) -> dict[Any, Any]:
        assert self._tmdb is not None
        movie = self._tmdb.get_movie(movie_id)

        movie_info: dict[Any, Any] = {}

        movie_info["id"] = movie_id
        movie_info["title"] = movie.get("title", "")
        movie_info["status"] = movie.get("status", "")
        movie_info["release_dates"] = []

        if not movie_info["release_dates"]:
            movie_info["release_dates"] = self._filter_release_dates_by_country(movie, "US")
        if not movie_info["release_dates"]:
            movie_info["release_dates"] = self._filter_release_dates_by_country(movie, "GB")
        if not movie_info["release_dates"]:
            movie_info["release_dates"] = self._filter_release_dates_by_country(movie, "DE")

        return movie_info

    def run(self) -> int:
        """! Run the main logic.
        """

        return 0
