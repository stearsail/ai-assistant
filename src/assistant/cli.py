import asyncio
import getpass
import sys

from assistant import config
from assistant.agent import run_agent


def setup_oauth() -> None:
    try:
        config.load_credentials()
        print("Loaded credentials.")
    except config.MissingCredentials as e:
        print("Credentials not found.")
        print(
            f"{e}\nPlease enter your google OAuth credentials (Cloud Console → APIs & Services → Credentials)"
        )
        google_oauth_client_id = input("Client ID: ").strip()
        google_oauth_client_secret = getpass.getpass("Client secret: ").strip()
        if google_oauth_client_id and google_oauth_client_secret:
            print("Saving credentials to configuration file...")
            config.save_credentials(google_oauth_client_id, google_oauth_client_secret)
            print("Credentials saved.")


def setup_api() -> None:
    try:
        config.load_anthropic_api_key()
        print("Loaded API Key.")
    except config.MissingAPIKey as e:
        print(e)
        api_key = getpass.getpass("Please enter your Anthropic API key: ").strip()
        if api_key:
            print("Saving API key to configuration file...")
            config.save_anthropic_api_key(api_key)


def main() -> None:
    # load_dotenv()
    setup_oauth()
    setup_api()
    try:
        api_key = config.load_anthropic_api_key()["anthropic_api_key"]
        asyncio.run(run_agent(api_key))
    except config.MissingAPIKey as e:
        print(e, file=sys.stderr)
        return 1
    return 0
