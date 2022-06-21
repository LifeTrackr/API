import os

from dotenv import load_dotenv

from definitions import ROOT_DIR


class Env:
    def __init__(self):
        load_dotenv(dotenv_path=f"{ROOT_DIR}/.env")
        runtime = os.environ["runtime"]
        prefix = f"{os.environ['DB_BASE_PREFIX']}-"
        if runtime == "prod":
            prefix += os.environ['DB_PROD_PREFIX']
        elif runtime == "dev":
            prefix += os.environ['DB_DEV_PREFIX']
        elif runtime == "test":
            prefix += os.environ['DB_TEST_PREFIX']
        else:
            raise RuntimeWarning("Missing runtime environment variable")
        self.db_host = f"{prefix}.{os.environ['DB_URL']}"
        print("[info] Running in development")
        try:
            self.db_pass = os.environ["DB_PASS"]
            self.db_user = os.environ["DB_USER"]
            self.db_name = os.environ["DB_NAME"]
            self.db_port = os.environ["DB_PORT"]
            self.production = True if runtime is "prod" else False
        except KeyError as key_error:
            raise KeyError(f"Error: Missing environment variable {key_error}")
