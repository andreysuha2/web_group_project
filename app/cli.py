import secrets
import dotenv
import typer
import shutil
from pathlib import Path
from users.seed import main as users_seed
from photos.seed import main as photos_seed
from comments.seed import main as comments_seed
try:
    from app.settings import settings
except TypeError:
    settings = None

app = typer.Typer()

@app.command()
def seed():
    users_seed()
    photos_seed()
    comments_seed()

@app.command()
def initenv(env: str = 'development'):
    ROOT_PATH = Path(__file__).parent.parent
    ENV_PATH = f"{ROOT_PATH}/.env"
    ENV_EXAMPLE_PATH = f"{ROOT_PATH}/.env.example"
    if Path(ENV_EXAMPLE_PATH).exists():
        if not Path(ENV_PATH).exists():
            shutil.copy(ENV_EXAMPLE_PATH, ENV_PATH)
            dotenv_file = dotenv.find_dotenv()
            dotenv.load_dotenv(dotenv_file)
            dotenv.set_key(dotenv_file, "APP_SECRET", secrets.token_urlsafe(25))
            dotenv.set_key(dotenv_file, "APP_ENV", env)
            print("Env file sccessfuly inited")
        else:
            print("Env file already exists!")
    else:
        print('File .env.example does not existig at root folder')

@app.command()
def version():
    print(settings.app.NAME, settings.app.VERSION)
    

if __name__ == "__main__":
    app()