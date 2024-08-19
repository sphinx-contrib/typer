from sphinxcontrib import typer
from pathlib import Path
import json
import os

TEST_CALLBACKS = Path(__file__).parent / "callback_record.json"

test_callbacks = {}


def record_callback(callback):
    """crude but it works"""
    if TEST_CALLBACKS.is_file():
        os.remove(TEST_CALLBACKS)
    test_callbacks[callback] = True
    TEST_CALLBACKS.write_text(json.dumps(test_callbacks))


def typer_get_web_driver(*args, **kwargs):
    record_callback("typer_get_web_driver")
    return typer.typer_get_web_driver(*args, **kwargs)


def typer_render_html(*args, **kwargs):
    record_callback("typer_render_html")
    return typer.typer_render_html(*args, **kwargs)


def typer_get_iframe_height(*args, **kwargs):
    record_callback("typer_get_iframe_height")
    return typer.typer_get_iframe_height(*args, **kwargs)


def typer_svg2pdf(*args, **kwargs):
    record_callback("typer_svg2pdf")
    return typer.typer_svg2pdf(*args, **kwargs)


def typer_convert_png(*args, **kwargs):
    record_callback("typer_convert_png")
    return typer.typer_convert_png(*args, **kwargs)
