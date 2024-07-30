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

from tmdb import TMDB


class MonitorMovieShowReleases:  # pylint: disable=too-few-public-methods
    """! Monitor Movie and Show Releases logic.
    """

    def __init__(self) -> None:
        self._tmdb: TMDB | None = None

    def run(self) -> int:
        """! Run the main logic.
        """

        return 0
