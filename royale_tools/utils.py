import locale
import statistics as st
import sys
from copy import deepcopy as dc
from typing import Any, Dict, Iterable, Optional

import pkg_resources
import PySimpleGUI as sg
import requests

VERSION = pkg_resources.require("royale-tools")[0].version
locale.setlocale(locale.LC_ALL, "")

TITLE = "Royale Tools"
MIN_SIZE = (320, 180)
THEMES = (
    "BlueMono|Dark|DarkAmber|DarkTeal2|GreenMono|LightYellow|Reddit|"
    "Reds|SandyBeach|SystemDefault|TealMono|Topanga"
)


class CustomWindows:
    @staticmethod
    def F(*args: Any, **kwargs: Any) -> sg.Frame:
        """Custom sg.Frame implementation."""
        return sg.Frame(*args, **kwargs, font="Any 14 bold")

    @staticmethod
    def main_window() -> sg.Window:
        """Main window."""
        b_size = (10, 1)
        layout = [
            [sg.B("Player", size=b_size), sg.B("Clan", size=b_size)],
            [sg.B("Settings", size=b_size), sg.B("About", size=b_size)],
        ]
        return sg.Window(TITLE, layout, element_justification="c", font="Any 15")

    @staticmethod
    def settings_window(mandatory: bool, config: Dict[str, str]) -> sg.Window:
        """Settings configuration window.

        Args:
            mandatory: Whether if previous settings were invalid or not.
                If True, Exit button is showed instead of Cancel.
            config: Default input text fields.
        """
        layout = [
            [sg.T("Token*", tooltip="Clash Royale API token (mandatory)")],
            [sg.In(config["token"] or "", key="in.token")],
            [sg.T("Player tag", tooltip="Your personal player tag (optional)")],
            [sg.In(config["player_tag"] or "", key="in.player_tag")],
            [sg.T("Clan tag", tooltip="Your clan tag (optional)")],
            [sg.In(config["clan_tag"] or "", key="in.clan_tag")],
            [sg.T("Theme")],
            [
                sg.Combo(
                    THEMES.split("|"),
                    default_value=config["theme"],
                    key="cmb.theme",
                    enable_events=True,
                )
            ],
            [
                sg.Save(),
                sg.Exit() if mandatory else sg.Cancel(),
                sg.HorizontalSeparator(),
                sg.B("Preview theme"),
            ],
        ]
        return sg.Window(TITLE, layout)

    @staticmethod
    def theme_sample_window() -> sg.Window:
        """Theme sample window."""
        layout = [
            [sg.T("Text element"), sg.In("Input data here", size=(10, 1))],
            [sg.B("Ok"), sg.B("Cancel"), sg.Slider(orientation="h", size=(15, 15))],
        ]
        return sg.Window(sg.theme(), layout)

    @staticmethod
    def about_window() -> sg.Window:
        """About window."""
        items = ["coffee", "meal", "book"]
        selector = sg.Combo(items, "coffee", key="cmb.item")
        desc = (
            "Royale Tools is a clan management python application."
            "If you have any problem, open a new issue in GitHub!"
        )
        info = [
            [sg.T("Name: Royale Tools")],
            [sg.T("Author: Iago GR")],
            [sg.T(f"Version: {VERSION}")],
        ]
        layout = [
            [cw.F("Description", [[sg.T(desc, size=(30, 3), justification="c")]])],
            [cw.F("Project information", info), sg.B("GitHub")],
            [cw.F("Donations", [[sg.T("Buy me a..."), selector, sg.B("Buy")]])],
            [sg.B("\u2190")],
        ]
        return sg.Window(TITLE, layout)

    @staticmethod
    def player_tag_window(default_tag: str) -> sg.Window:
        """Player tag selection window.

        Args:
            default_tag (str): Default player tag.
        """
        layout = [
            [sg.T("Enter a player tag")],
            [sg.In(default_tag, key="in.player_tag", size=(20, 1)), sg.B("OK")],
        ]
        return sg.Window(TITLE, layout)

    @staticmethod
    def player_main_window(data: Dict) -> sg.Window:
        """Player main window.

        Args:
            data (Dict): Dictionary with player information.
        """

        def get_winrate(n_losses: int, n_wins: int):
            try:
                return f"{100.0 * n_wins / (n_wins + n_losses):.2f}%"
            except Exception:
                return "Not available"

        generic = [
            [sg.T(f"Name: {data['name']}")],
            [sg.T(f"Tag: {data['tag']}")],
            [sg.T(f"Arena: {data['arena']['name']}")],
            [sg.T(f"Winrate: {get_winrate(data['losses'], data['wins'])}")],
            [sg.T(f"War day wins: {data['warDayWins']}")],
            [sg.T(f"Challenge max wins: {data['challengeMaxWins']}")],
            [sg.T(f"{data['role'].capitalize()} in {data['clan']['name']}")],
            [sg.T(f"Donations sent: {data['donations']}")],
            [sg.T(f"Donations received: {data['donationsReceived']}")],
        ]

        stats = data["leagueStatistics"]

        if "previousSeason" not in stats:
            stats["previousSeason"]["trophies"] = "Not found"
            stats["previousSeason"]["bestTrophies"] = "Not found"
        if "bestSeason" not in stats:
            stats["bestSeason"]["trophies"] = "Not found"

        trophies = [
            [sg.T("Current season:")],
            [sg.T(f" + Trophies: {stats['currentSeason']['trophies']}")],
            [sg.T(f" + Best: {stats['currentSeason']['bestTrophies']}")],
            [sg.T("Previous season:")],
            [sg.T(f" + Trophies: {stats['previousSeason']['trophies']}")],
            [sg.T(f" + Best: {stats['previousSeason']['bestTrophies']}")],
            [sg.T("Best season:")],
            [sg.T(f" + Best: {stats['bestSeason']['trophies']}")],
        ]
        layout = [
            [
                cw.F("Generic", generic),
                cw.F("Trophies", trophies),
            ],
            [sg.B("Chests"), sg.B("Cards"), sg.B("War"), sg.B("Royale API")],
            [sg.B("\u2190")],
        ]
        return sg.Window(TITLE, layout)

    @staticmethod
    def player_chests_window(data: Dict) -> sg.Window:
        """Player chests window.

        Args:
            data (Dict): Dictionary with chests information.
        """
        upcoming = []
        for chest in data["items"]:
            upcoming.append([sg.T(f"+{chest['index']+1}:\t{chest['name']}")])
        layout = [
            [cw.F("Upcoming chests", upcoming)],
            [sg.B("\u2190")],
        ]
        return sg.Window(TITLE, layout)

    @staticmethod
    def player_cards_window(data: Dict) -> sg.Window:
        """Player cards window.

        Args:
            data (Dict): Dictionary with player information.
        """
        fav_card = data["currentFavouriteCard"]["name"]
        stats = RoyaleApi.get_cards_stats(data["cards"])
        n_collected, n_all = stats.pop("collected")
        layout = [
            [sg.T(f"Obtained cards: {n_collected}/{n_all}")],
            [sg.T(f"Favorite card: {fav_card}")],
        ]
        max_level_names = {13: "Common", 11: "Rare", 8: "Epic", 5: "Legendary"}
        frames = []
        for max_lvl, name in max_level_names.items():
            lvl_stats = stats[max_lvl]
            frame = [
                [sg.T(f"Remaining cards: {lvl_stats['rem_cards']:n}")],
                [sg.T(f"Remaining gold: {lvl_stats['rem_gold']:n}")],
                [sg.T(f"Progress: {lvl_stats['progress']:n}%")],
                [sg.T(f"Average level: {lvl_stats['avg_level']:n}")],
            ]
            frames.append(cw.F(name, frame))

        layout.append([frames[0], frames[1]])
        layout.append([frames[2], frames[3]])
        layout.append([sg.B("\u2190")])

        return sg.Window(TITLE, layout)


class RoyaleApi:

    token = None

    @staticmethod
    def get_request(url: str, params: Optional[Any] = None) -> Dict:
        """Get request.

        Args:
            url: URL of the request.
            params: Optional parameters of the request.

        Returns:
            Dict: JSON response.
        """
        headers = {
            "Accept": "application/json",
            "authorization": f"Bearer {RoyaleApi.token}",
        }
        req = None
        try:
            req = requests.get(url, headers=headers, params=params)

            if req.status_code != 200:
                raise ConnectionError

        except Exception:
            code_info = "" if not req else f"(code: {req.status_code})"
            sg.popup_error(
                f"Couldn't get API data! {code_info}",
                "This application can't work without API data.",
                "Common errors:",
                " - Internet connection error",
                " - Invalid API token",
                " - Invalid player/clan tag",
                "Please, check these issues and try again.",
                title="API error",
            )
            sys.exit()

        return req.json()

    @staticmethod
    def get_player_data(tag: str, query: str = "") -> Dict:
        """Get player data.

        Args:
            tag (str): Player tag.
            query (str): Query type. Defaults to "".

        Returns:
            Dict: Player data in JSON format.
        """
        if not tag.startswith("#"):
            tag = "#" + tag
        tag = tag.replace("#", "%23")
        url = f"https://api.clashroyale.com/v1/players/{tag}/{query}"
        return RoyaleApi.get_request(url)

    @staticmethod
    def get_cards_stats(player_cards: Dict) -> Dict:
        """Get cards stats.

        Args:
            player_cards (Dict): Player cards in JSON format.

        Returns:
            Dict: Cards stats.
        """

        def get_remaining_cards(level: int, max_level: int, count: int):
            # Return 0 if maxed
            if level == max_level:
                return 0
            n_cards = [1, 2, 4, 10, 20, 50, 100, 200, 400, 800, 1000, 2000, 5000]
            return sum(n_cards[level:max_level]) - count

        def get_remaining_gold(level: int, max_level: int):
            # Return 0 if maxed
            if level == max_level:
                return 0
            n_gold = [100000, 50000, 20000, 8000, 4000, 2000, 1000, 400, 150, 50, 20, 5]
            if max_level == 5:
                n_gold.append(0)
                n_gold[3] = 5000
            if max_level == 8:
                n_gold[6] = 400
            return sum(n_gold[: max_level - level])

        empty = {"rem_cards": 0, "rem_gold": 0, "levels": []}
        stats = {13: dc(empty), 11: dc(empty), 8: dc(empty), 5: dc(empty)}
        collected = set()

        for card in player_cards:
            collected.add(card["name"])
            lvl, max_lvl, cnt = card["level"], card["maxLevel"], card["count"]
            stats[max_lvl]["rem_cards"] += get_remaining_cards(lvl, max_lvl, cnt)
            stats[max_lvl]["rem_gold"] += get_remaining_gold(lvl, max_lvl)
            stats[max_lvl]["levels"].append(lvl)  # type: ignore

        all_cards = RoyaleApi.get_request("https://api.clashroyale.com/v1/cards")
        for card in all_cards["items"]:
            if card["name"] not in collected:
                lvl, max_lvl, cnt = 0, card["maxLevel"], 0
                stats[max_lvl]["rem_cards"] += get_remaining_cards(lvl, max_lvl, cnt)
                stats[max_lvl]["rem_gold"] += get_remaining_gold(lvl, max_lvl)
                stats[max_lvl]["levels"].append(lvl)  # type: ignore

        stats["collected"] = (len(collected), len(all_cards["items"]))  # type: ignore
        for max_lvl in (13, 11, 8, 5):
            levels: Iterable[float] = stats[max_lvl]["levels"]  # type: ignore
            stats[max_lvl]["progress"] = st.mean(levels) * (100.0 / max_lvl)
            stats[max_lvl]["avg_level"] = st.mean(levels) + (13 - max_lvl)

        return stats


cw = CustomWindows
