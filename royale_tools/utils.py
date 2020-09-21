from typing import Any, Dict, Optional

import pkg_resources
import PySimpleGUI as sg
import requests

VERSION = pkg_resources.require("royale-tools")[0].version


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
    def player_info_window(info: Dict) -> sg.Window:
        """Player info window.

        Args:
            info (Dict): Dictionary with player information.
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
    def get_player_info(tag: str) -> Dict:
        """Get player info.

        Args:
            tag (str): Player tag.

        Returns:
            Dict: Player info in JSON format.
        """
        if not tag.startswith("#"):
            tag = "#" + tag
        tag = tag.replace("#", "%23")
        url = f"https://api.clashroyale.com/v1/players/{tag}"
        return RoyaleApi.get_request(url)
