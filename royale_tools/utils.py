import locale
import statistics as st
import sys
from copy import deepcopy as dc
from typing import Any, Dict, Iterable, List, Optional

import pkg_resources
import PySimpleGUI as sg
import requests

VERSION = pkg_resources.require("royale-tools")[0].version
locale.setlocale(locale.LC_ALL, "")

TITLE = "Royale Tools"
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
            [cw.F("Donations", [[sg.T("Buy me a..."), selector, sg.B("PayPal")]])],
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
    def progress_window(max_prog: Optional[int] = 100) -> sg.Window:
        """Progress window.

        Args:
            max_prog (int): Maximum progress. Defaults to 100.
        """
        layout = [[sg.ProgressBar(max_prog, orientation="h", size=(20, 20), k="pbar")]]
        return sg.Window(TITLE, layout, no_titlebar=True)

    @staticmethod
    def player_main_window(data: Dict) -> sg.Window:
        """Player main window.

        Args:
            data (Dict): Dictionary with player information.
        """
        winrate = RoyaleApi.get_winrate(data["losses"], data["wins"])
        winrate_text = f"{winrate:.2f}%" if winrate > 0 else "Not available"
        generic = [
            [sg.T(f"Name: {data['name']}")],
            [sg.T(f"Tag: {data['tag']}")],
            [sg.T(f"Arena: {data['arena']['name']}")],
            [sg.T(f"Winrate: {winrate_text}")],
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
    def player_cards_window(data: Dict, stats: Dict) -> sg.Window:
        """Player cards window.

        Args:
            data (Dict): Dictionary with player information.
            stats (Dict): Dictionary with cards stats.
        """
        fav_card = data["currentFavouriteCard"]["name"]
        n_collected, n_all = stats["collected"]
        layout = [
            [sg.T(f"Obtained cards: {n_collected}/{n_all}")],
            [sg.T(f"Favorite card: {fav_card}")],
        ]
        max_level_names = {13: "Common", 11: "Rare", 8: "Epic", 5: "Legendary"}
        frames = []
        for max_lvl, name in max_level_names.items():
            lvl_stats = stats[max_lvl]
            frame = [
                [sg.T(f"Remaining cards: {lvl_stats['rem_cards']}")],
                [sg.T(f"Remaining gold: {lvl_stats['rem_gold']}")],
                [sg.T(f"Progress: {lvl_stats['progress']:.2f}%")],
                [sg.T(f"Average level: {lvl_stats['avg_level']:.2f}")],
            ]
            frames.append(cw.F(name, frame))

        layout.append([frames[0], frames[1]])
        layout.append([frames[2], frames[3]])
        layout.append([sg.B("\u2190")])

        return sg.Window(TITLE, layout)

    @staticmethod
    def player_war_window(data: Dict, best_32: List[int], stats: Dict) -> sg.Window:
        """Player war window.

        Args:
            data (Dict): Dictionary with player information.
            best_32 (List): List with best 32 stats levels.
            stats (Dict): Dictionary with war stats.
        """
        winrate = RoyaleApi.get_winrate(data["losses"], data["wins"]) / 100.0
        base_fp = sum(best_32)
        est_fp = int(winrate * (2 * base_fp) + (1 - winrate) * base_fp)
        decks = [
            [sg.T(f"Average level: {st.mean(best_32):.2f}")],
            [sg.T(f"Minimum daily WP: {base_fp}")],
            [sg.T(f"Maximum daily WP: {2 * base_fp}")],
            [sg.T(f"Estimated daily WP: {est_fp}")],
            [sg.HSep()],
            [sg.T(f"Minimum war WP: {7 * base_fp}")],
            [sg.T(f"Maximum war WP: {14 * base_fp}")],
            [sg.T(f"Estimated war WP: {7 * est_fp}")],
        ]
        war_stats = [
            [sg.T(f"Total WP: {sum(stats['war_points']):.0f}")],
            [sg.T(f" \u21B3 FP: {sum(stats['fame_points']):.0f}")],
            [sg.T(f" \u21B3 RP: {sum(stats['repair_points']):.0f}")],
            [
                sg.T(
                    f"Average WP: {sum(stats['war_points']) / len(stats['war_points'])}"
                )
            ],
        ]
        current_war = [
            [sg.T(f"Current WP: {stats['current_war_points']}")],
            [sg.T(f" \u21B3 FP: {stats['current_fame_points']}")],
            [sg.T(f" \u21B3 RP: {stats['current_repair_points']}")],
        ]
        h = "WP: War Points\nFP: Fame Points\nRP: Repair Points"
        layout = [
            [
                sg.Col(
                    [
                        [
                            cw.F("Best 32 cards", decks),
                            sg.Col(
                                [
                                    [cw.F("War stats", war_stats)],
                                    [cw.F("Current war", current_war)],
                                ]
                            ),
                        ],
                    ]
                )
            ],
            [sg.B("\u2190"), sg.HSep(), sg.T("[?]", tooltip=h)],
        ]

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
    def get_clan_data(tag: str, query: str = "") -> Dict:
        """Get clan data.

        Args:
            tag (str): Clan tag.
            query (str): Query type. Defaults to "".

        Returns:
            Dict: Clan data in JSON format.
        """
        if not tag.startswith("#"):
            tag = "#" + tag
        tag = tag.replace("#", "%23")
        url = f"https://api.clashroyale.com/v1/clans/{tag}/{query}"
        return RoyaleApi.get_request(url)

    @staticmethod
    def get_winrate(n_losses: int, n_wins: int) -> float:
        """Compute winrate.

        Args:
            n_losses (int): Number of losses.
            n_wins (int): Number of wins.

        Returns:
            float: Winrate.
        """
        try:
            return 100.0 * n_wins / (n_wins + n_losses)
        except Exception:
            return -1.0

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

        levels = []
        for card in player_cards:
            collected.add(card["name"])
            lvl, max_lvl, cnt = card["level"], card["maxLevel"], card["count"]
            stats[max_lvl]["rem_cards"] += get_remaining_cards(lvl, max_lvl, cnt)
            stats[max_lvl]["rem_gold"] += get_remaining_gold(lvl, max_lvl)
            stats[max_lvl]["levels"].append(lvl)  # type: ignore
            levels.append(lvl + (13 - max_lvl))

        stats["best_32"] = sorted(levels, reverse=True)[:32]  # type: ignore
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

    @staticmethod
    def get_war_stats(player_tag: str, river_race_log: Dict, curr_river_race) -> Dict:
        """Get war stats.

        Args:
            player_tag (str): Player tag.
            river_race_log (Dict): Clan river race log data in JSON format.
            curr_river_race (Dict): Clan current river race data in JSON format.

        Returns:
            Dict: War stats.
        """
        clan_tag = curr_river_race["clan"]["tag"]
        stats: Dict[str, List] = {
            "fame_points": [],
            "repair_points": [],
            "war_points": [],
        }
        for race in river_race_log["items"]:
            for clan in race["standings"]:
                if clan["clan"]["tag"] != clan_tag:
                    continue
                for player in clan["clan"]["participants"]:
                    if player["tag"] != player_tag:
                        continue
                    stats["fame_points"].append(float(player["fame"]))
                    stats["repair_points"].append(float(player["repairPoints"]))
                    stats["war_points"].append(
                        float(player["fame"]) + float(player["repairPoints"])
                    )

        for player in curr_river_race["clan"]["participants"]:
            if player["tag"] != player_tag:
                continue
            stats["current_fame_points"] = player["fame"]
            stats["current_repair_points"] = player["repairPoints"]
            stats["current_war_points"] = player["fame"] + player["repairPoints"]

        return stats


cw = CustomWindows
