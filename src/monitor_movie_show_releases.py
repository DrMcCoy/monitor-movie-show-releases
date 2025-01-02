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

import argparse
import difflib
import json
import time
from enum import IntEnum
from typing import Any

import dictdiffer

from config import Config
from sendmail import SendMail
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

    def __init__(self, args: argparse.Namespace) -> None:
        self._args = args

        self._tmdb: TMDB | None = None
        self._sendmail: SendMail | None = None

    @staticmethod
    def _format_unified_dict_diff(old: dict[Any, Any], new: dict[Any, Any], tmdb_id: int) -> str:
        str_old = json.dumps(old, indent=4)
        str_new = json.dumps(new, indent=4)

        return '\n'.join(difflib.unified_diff(str_old.splitlines(), str_new.splitlines(),
                                              fromfile=f'{tmdb_id}.json.old', tofile=f'{tmdb_id}.json.new',
                                              lineterm='')) + '\n'

    @staticmethod
    def _format_dict_diff(diff: list[Any]) -> str:
        formatted = ''
        for change in diff:
            formatted += str(change) + '\n'

        return formatted

    @staticmethod
    def _format_movie_change(movie_old: dict[Any, Any], movie_new: dict[Any, Any]) -> tuple[bool, str, str]:
        movie_diff = list(dictdiffer.diff(movie_old, movie_new))
        if not movie_diff:
            return False, "", ""

        subject = f'Change in movie "{movie_new["title"]}" ({movie_new["id"]})'

        body = ''
        body = f'https://www.themoviedb.org/movie/{movie_new["id"]}\n\n'
        body += f'Title: {movie_new["title"]}\n'
        body += f'Original Title: {movie_new["original_title"]}\n'
        body += f'Status: {movie_new["status"]}\n\n'
        for release in movie_new["release_dates"]:
            body += f'Release({release["type"]}, {release["iso_639_1"]}): {release["release_date"]}\n'

        body += '\n------\n\n'
        body += MonitorMovieShowReleases._format_unified_dict_diff(movie_old, movie_new, movie_new["id"])
        body += '\n------\n\n'
        body += MonitorMovieShowReleases._format_dict_diff(movie_diff)

        return True, subject, body

    @staticmethod
    def _format_show_change(show_old: dict[Any, Any], show_new: dict[Any, Any]) -> tuple[bool, str, str]:
        show_diff = list(dictdiffer.diff(show_old, show_new))
        if not show_diff:
            return False, "", ""

        subject = f'Change in show "{show_new["title"]}" ({show_new["id"]})'

        body = ''
        body = f'https://www.themoviedb.org/tv/{show_new["id"]}\n\n'
        body += f'Title: {show_new["title"]}\n'
        body += f'Original Title: {show_new["original_title"]}\n'
        body += f'Status: {show_new["status"]}\n\n'

        next_episode = show_new["next_episode_to_air"]
        if next_episode is not None:
            episode = next_episode.get("episode_number", 0)
            season = next_episode.get("season_number", 0)
            name = next_episode.get("name", "")
            episode_id = next_episode.get("id", 0)
            date = next_episode.get("air_date", "")

            body += f'Next to air: {season}x{episode:02} - {name} ({episode_id})  --  {date}\n'

        body += '\n------\n\n'
        body += MonitorMovieShowReleases._format_unified_dict_diff(show_old, show_new, show_new["id"])
        body += '\n------\n\n'
        body += MonitorMovieShowReleases._format_dict_diff(show_diff)

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
        movie_info["original_title"] = movie.get("original_title", movie_info["title"])
        movie_info["status"] = movie.get("status", "")
        movie_info["release_dates"] = []

        if not movie_info["release_dates"]:
            movie_info["release_dates"] = self._filter_release_dates_by_country(movie, "US")
        if not movie_info["release_dates"]:
            movie_info["release_dates"] = self._filter_release_dates_by_country(movie, "GB")
        if not movie_info["release_dates"]:
            movie_info["release_dates"] = self._filter_release_dates_by_country(movie, "DE")

        return movie_info

    def _get_show_info(self, show_id: int) -> dict[Any, Any]:
        assert self._tmdb is not None
        show = self._tmdb.get_show(show_id)

        show_info: dict[Any, Any] = {}

        show_info["id"] = show_id
        show_info["title"] = show.get("name", "")
        show_info["original_title"] = show.get("original_name", show_info["title"])
        show_info["status"] = show.get("status", "")
        show_info["next_episode_to_air"] = show.get("next_episode_to_air", None)
        return show_info

    def _check_movie(self, movie_id: int, config: Config, email_to: list[str]) -> None:
        print(f"Checking movie {movie_id}... ", end='', flush=True)

        movie_info_cached = config.get_cached_movie(movie_id)
        movie_info = self._get_movie_info(movie_id)

        print(f'"{movie_info["title"]}"... ', end='', flush=True)

        changed, subject, body = self._format_movie_change(movie_info_cached, movie_info)

        if changed:
            print("change")
            if not self._args.skip_mails:
                assert self._sendmail is not None
                for address in email_to:
                    self._sendmail.send(address, subject, body)

            if not self._args.skip_cache:
                config.put_cached_movie(movie_id, movie_info)
        else:
            print("no change")

    def _check_show(self, show_id: int, config: Config, email_to: list[str]) -> None:
        print(f"Checking show {show_id}... ", end='', flush=True)

        show_info_cached = config.get_cached_show(show_id)
        show_info = self._get_show_info(show_id)

        print(f'"{show_info["title"]}"... ', end='', flush=True)

        changed, subject, body = self._format_show_change(show_info_cached, show_info)

        if changed:
            print("change")
            if not self._args.skip_mails:
                assert self._sendmail is not None
                for address in email_to:
                    self._sendmail.send(address, subject, body)

            if not self._args.skip_cache:
                config.put_cached_show(show_id, show_info)
        else:
            print("no change")

    def run(self) -> int:
        """! Run the main logic.
        """

        config = Config()

        program_config = config.get_program_config()

        if not program_config["tmdb"]:
            print(f"No TMDB API key in config file \"{config.get_program_config_path()}\"")
            return 1

        if not program_config["movies"] and not program_config["shows"]:
            print("Nothing to do.")

        self._sendmail = SendMail(program_config["email"]["host"],
                                  program_config["email"]["port"],
                                  program_config["email"]["from"])
        self._tmdb = TMDB(program_config["tmdb"])

        if not self._args.skip_movies:
            for n, movie in enumerate(program_config["movies"]):
                if n % 10 == 0:
                    print("Waiting for a bit... ", end='', flush=True)
                    time.sleep(2)
                    print("done")

                print(f'{n + 1}/{len(program_config["movies"])}: ', end='', flush=True)
                self._check_movie(movie, config, program_config["email"]["to"])

        if not self._args.skip_shows:
            for n, show in enumerate(program_config["shows"]):
                if n % 10 == 0:
                    print("Waiting for a bit... ", end='', flush=True)
                    time.sleep(2)
                    print("done")

                print(f'{n + 1}/{len(program_config["shows"])}: ', end='', flush=True)
                self._check_show(show, config, program_config["email"]["to"])

        return 0
