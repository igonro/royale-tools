import locale
from typing import Any, Dict, List, Optional, Tuple

import pkg_resources
import PySimpleGUI as sg
import requests

VERSION = pkg_resources.require("royale-tools")[0].version
locale.setlocale(locale.LC_ALL, "")


class CustomWindows:
    @staticmethod
    def main_window() -> sg.Window:
        """Main window."""
        layout = [
            [sg.B("Player"), sg.B("Clan")],
            [sg.B("Settings"), sg.B("About"), sg.Exit()],
        ]
        return sg.Window(title="Royale Tools", layout=layout)

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
                    sg.theme_list(),
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
        return sg.Window(title="Settings", layout=layout)

    @staticmethod
    def theme_sample_window() -> sg.Window:
        """Theme sample window."""
        layout = [
            [sg.T("Text element"), sg.In("Input data here", size=(10, 1))],
            [sg.B("Ok"), sg.B("Cancel"), sg.Slider(orientation="h", size=(15, 15))],
        ]
        return sg.Window(title=sg.theme(), layout=layout)

    @staticmethod
    def about_window() -> sg.Window:
        """About window."""
        items = ["coffee", "meal", "book"]
        selector = sg.Combo(items, "coffee", key="cmb.item")
        layout = [
            [
                sg.Frame(
                    "Description",
                    [
                        [sg.T("Royale Tools is a clan management")],
                        [sg.T("python application. If you have any")],
                        [sg.T("problem, open a new issue in GitHub!")],
                    ],
                )
            ],
            [
                sg.Frame(
                    "Project information",
                    [
                        [sg.T("Name: Royale Tools")],
                        [sg.T("Author: Iago GR")],
                        [sg.T(f"Version: {VERSION}")],
                    ],
                ),
                sg.B("GitHub"),
            ],
            [sg.Frame("Donations", [[sg.T("Buy me a..."), selector, sg.B("Buy")]])],
        ]
        return sg.Window(title="About", layout=layout)

    @staticmethod
    def select_player_window(default_tag: str) -> sg.Window:
        """Select player window.

        Args:
            default_tag (str): Default player tag.
        """
        layout = [
            [sg.T("Enter a player tag")],
            [sg.In(default_tag, key="in.player_tag"), sg.B("Ok!")],
        ]
        return sg.Window(title="Player selection", layout=layout)

    @staticmethod
    def player_main_window(info: Dict) -> sg.Window:
        """Player info window.

        Args:
            info (Dict): Dictionary with information.
        """
        try:
            winrate = f"{100.0 * info['wins'] / (info['wins'] + info['losses']):.2f}%"
        except Exception:
            winrate = "Error!"
        generic = [
            [sg.T(f"Name: {info['name']}")],
            [sg.T(f"Arena: {info['arena']['name']}")],
            [sg.T(f"Winrate: {winrate}")],
            [sg.T(f"War day wins: {info['warDayWins']}")],
            [sg.T(f"Challenge max wins: {info['challengeMaxWins']}")],
            [sg.T(f"{info['role'].capitalize()} in {info['clan']['name']}")],
            [sg.T(f"Donations given: {info['donations']}")],
            [sg.T(f"Donations received: {info['donationsReceived']}")],
        ]
        stats = info["leagueStatistics"]
        trophies = [
            [sg.T("Current season:")],
            [sg.T(f"  Trophies: {stats['currentSeason']['trophies']}")],
            [sg.T(f"  Best: {stats['currentSeason']['bestTrophies']}")],
            [sg.T("Previous season:")],
            [sg.T(f"  Trophies: {stats['previousSeason']['trophies']}")],
            [sg.T(f"  Best: {stats['previousSeason']['bestTrophies']}")],
            [sg.T("Best season:")],
            [sg.T(f"  Best: {stats['bestSeason']['trophies']}")],
        ]
        layout = [
            [
                sg.Frame("Generic", generic, font="Any 15"),
                sg.Frame("Trophies", trophies, font="Any 15"),
            ],
            [sg.B("Chests"), sg.B("Cards"), sg.B("War"), sg.B("Royale API")],
        ]
        return sg.Window(title=f"{info['tag']} info", layout=layout)

    @staticmethod
    def player_chests_window(info: Dict) -> sg.Window:
        """Player chests window.

        Args:
            info (Dict): Dictionary with information.
        """
        upcoming = []
        for chest in info["items"]:
            upcoming.append([sg.T(f"+{chest['index']+1} to get {chest['name']}")])
        layout = [[sg.Frame("Upcoming chests", upcoming, font="Any 15")]]
        return sg.Window("Player chests", layout=layout)

    @staticmethod
    def player_cards_window(info: Dict) -> sg.Window:
        """Player cards window.

        Args:
            info (Dict): Dictionary with information.
        """
        number, gold, obtained, progress, levels, avg = RoyaleApi.get_cards_stats(info)
        layout = [
            [sg.T(f"Obtained cards: {obtained[0]}/{obtained[1]}")],
            [sg.T(f"Favorite card: {info['currentFavouriteCard']['name']}")],
            [sg.T(f"Average level: {avg:.2f}")],
        ]
        max_level_names = {13: "Common", 11: "Rare", 8: "Epic", 5: "Legendary"}
        for max_level in (13, 11, 8, 5):
            frame_layout = [
                [sg.T(f"Remaining cards: {number[max_level]:n}")],
                [sg.T(f"Remaining gold: {gold[max_level]:n}")],
                [sg.T(f"Progress: {progress[max_level]:.2f}%")],
                [sg.T(f"Average level: {levels[max_level]:.2f}")],
            ]
            layout.append(
                [sg.Frame(max_level_names[max_level], frame_layout, font="Any 15")]
            )

        return sg.Window("Player cards", layout=layout)


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
        req = requests.get(url, headers=headers, params=params)

        return req.json()

    @staticmethod
    def get_player_info(tag: str, query: str = "") -> Dict:
        """Get player info.

        Args:
            tag (str): Player tag.
            query (str): Query type. Defaults to "".

        Returns:
            Dict: Player info in JSON format.
        """
        if not tag.startswith("#"):
            tag = "#" + tag
        tag = tag.replace("#", "%23")
        url = f"https://api.clashroyale.com/v1/players/{tag}/{query}"
        return RoyaleApi.get_request(url)

    @staticmethod
    def get_cards_data() -> Dict:
        """Get cards data.

        Returns:
            Dict: Cards data.
        """
        return RoyaleApi.get_request("https://api.clashroyale.com/v1/cards")

    @staticmethod
    def get_cards_stats(
        player_info: Dict,
    ) -> Tuple[
        Dict[int, int],
        Dict[int, int],
        Tuple[int, int],
        Dict[Any, Any],
        Dict[Any, Any],
        float,
    ]:
        """Get cards stats.

        Args:
            player_info (Dict): Player info in JSON format.

        Returns:
            Cards stats.
        """

        def get_remaining_gold(level: int, max_level: int):
            # Return 0 if maxed
            if level == max_level:
                return 0
            gold_tiers = [
                100000,
                50000,
                20000,
                8000,
                4000,
                2000,
                1000,
                400,
                150,
                50,
                20,
                5,
                0,
            ]
            if max_level == 5:
                gold_tiers[3] = 5000
            if max_level == 8:
                gold_tiers[6] = 400
            return sum(gold_tiers[: max_level - level])

        def get_remaining_cards(level: int, max_level: int, count: int):
            # Return 0 if maxed
            if level == max_level:
                return 0
            card_tiers = [1, 2, 4, 10, 20, 50, 100, 200, 400, 800, 1000, 2000, 5000]
            return sum(card_tiers[level:max_level]) - count

        def normalize_level(level: float, max_level: int):
            return 13 - (max_level - level)

        cards_data = RoyaleApi.get_cards_data()
        cards_number = {13: 0, 11: 0, 8: 0, 5: 0}
        gold_amount = {13: 0, 11: 0, 8: 0, 5: 0}
        card_levels: Dict[int, List[int]] = {13: [], 11: [], 8: [], 5: []}
        sum_level = 0
        obtained_cards = set()

        for card in player_info["cards"]:
            obtained_cards.add(card["name"])
            level, max_level, count = card["level"], card["maxLevel"], card["count"]
            cards_number[max_level] += get_remaining_cards(level, max_level, count)
            gold_amount[max_level] += get_remaining_gold(level, max_level)
            card_levels[max_level].append(level)
            sum_level += normalize_level(level, max_level)

        total = 0
        for card in cards_data["items"]:
            total += 1
            if not card["name"] in obtained_cards:
                max_level = card["maxLevel"]
                cards_number[max_level] += get_remaining_cards(0, max_level, 0)
                gold_amount[max_level] += get_remaining_gold(0, max_level)
                card_levels[max_level].append(0)

        avg_level = float(sum_level) / total
        obtained = (len(obtained_cards), total)
        card_progress, avg_levels = {}, {}
        for max_level, levels in card_levels.items():
            card_progress[max_level] = 100.0 * sum(levels) / (max_level * len(levels))
            avg_levels[max_level] = normalize_level(
                float(sum(levels)) / len(levels), max_level
            )

        return cards_number, gold_amount, obtained, card_progress, avg_levels, avg_level
