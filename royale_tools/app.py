import json
import sys

import PySimpleGUI as sg
from loguru import logger
from utils import CustomWindows as cw
from utils import RoyaleApi as api


class App:
    """Clash Royale tools application."""

    def __init__(self):
        # General settings
        self.token = None
        self.player_tag = None
        self.clan_tag = None
        # Appeareance settings
        self.theme = "DarkBlue3"
        # Load and apply configuration
        self.load_config()
        api.token = self.token
        sg.theme(self.theme)
        # Start main app
        self.main()

    def main(self):
        """Main application behaviour."""
        window = cw.main_window()
        while True:
            event, values = window.read()
            # Exit app
            if event in (sg.WIN_CLOSED, "Exit"):
                window.close()
                sys.exit()
            # Event handler
            if event == "Settings":
                window.hide()
                self.settings(mandatory=False)
                window.un_hide()
            if event == "About":
                window.hide()
                self.about()
                window.un_hide()
            if event == "Player":
                window.hide()
                self.player()
                window.un_hide()

    def settings(self, mandatory: bool):
        """Settings behaviour.

        Args:
            mandatory (bool): Whether if previous settings were invalid or not.
        """
        config = dict(
            token=self.token,
            player_tag=self.player_tag,
            clan_tag=self.clan_tag,
            theme=self.theme,
        )
        window = cw.settings_window(mandatory, config)  # pass values
        while True:
            event, values = window.read()
            # Exit settings
            if mandatory and event in ("Exit", sg.WIN_CLOSED):
                sys.exit()
            # Close window
            if not mandatory and event in ("Cancel", sg.WIN_CLOSED):
                break
            if event == "Save":
                if not values["in.token"]:
                    sg.popup_error("Enter your API token!", title="Token required")
                    continue
                for key, value in values.items():
                    if not value:
                        value = None
                    setattr(self, key.split(".")[1], value)
                sg.theme(self.theme)
                self.save_config()
                sg.popup(
                    "Settings saved succesfully!",
                    "Restart the app to reload theme in every window.",
                )
                break
            if event == "Preview theme":
                sg.theme(values["cmb.theme"])
                _, _ = cw.theme_sample_window().read(close=True)
                sg.theme(self.theme)
        window.close()

    def about(self):
        """About behaviour."""
        window = cw.about_window()
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                break
            if event == "GitHub":
                open_url("github.com/igonro/royale-tools")
            if event == "Buy":
                item = values["cmb.item"]
                if item == "coffee":
                    price = 2.5
                if item == "meal":
                    price = 10
                if item == "book":
                    price = 40
                open_url(f"paypal.me/igonro/{price}")
        window.close()

    def player(self):
        """Player behaviour."""
        # Select player tag
        event, values = cw.select_player_window(self.player_tag).read(close=True)
        tag = values["in.player_tag"]
        # Show player window
        player_info = api.get_player_info(tag)
        window = cw.player_info_window(player_info)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                break
            if event == "Royale API":
                open_url(f"royaleapi.com/player/{tag}")
        window.close()

    def load_config(self):
        """Load the saved configuration if it exists."""
        try:
            with open(".royale-tools-config", "r") as f:
                config = json.load(f)
            if "token" not in config:
                raise ValueError("Token field missing in configuration")
            for attr in self.__dict__:
                if attr in config:
                    setattr(self, attr, config[attr])
        except (FileNotFoundError, ValueError):
            logger.warning("Wrong or non-existent configuration")
            self.settings(mandatory=True)

    def save_config(self):
        """Save the current parameters."""
        config = {}
        for attr, val in self.__dict__.items():
            if val is not None:
                config[attr] = val
        with open(".royale-tools-config", "w") as f:
            json.dump(config, f, indent=2)


def open_url(url: str):
    """Open url in browser.

    Args:
        url (str): Url to open.
    """
    import webbrowser

    webbrowser.open_new_tab(url)


if __name__ == "__main__":
    app = App()