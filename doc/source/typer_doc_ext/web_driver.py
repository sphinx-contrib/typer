from contextlib import contextmanager
from sphinxcontrib import typer as sphinxcontrib_typer


@contextmanager
def typer_get_web_driver(directive):
    from pathlib import Path
    import os

    if not Path('~/.rtd.build').expanduser().is_file():
        with sphinxcontrib_typer.typer_get_web_driver(directive) as driver:
            yield driver
        return
    
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    # Set up headless browser options
    options=Options()
    os.environ['PATH'] += os.pathsep + os.path.expanduser("~/chrome/opt/google/chrome")
    options.binary_location = os.path.expanduser("~/chrome/opt/google/chrome/google-chrome")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    yield driver
    driver.quit()
