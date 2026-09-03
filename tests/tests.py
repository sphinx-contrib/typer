import io
import pytest
import re
import sys
from sphinx.application import Sphinx
from sphinx import version_info as sphinx_version
from typer import __version__ as typer_version
import typing as t
import os
from pathlib import Path
import shutil
import subprocess
from bs4 import BeautifulSoup as bs
from PIL import Image
from pypdf import PdfReader
import numpy as np
import json
import math
from collections import Counter

TYPER_VERISON = tuple(int(v) for v in typer_version.split("."))

test_callbacks = {}

DOC_DIR = Path(__file__).parent.parent / "doc"
SRC_DIR = DOC_DIR / "source"
BUILD_DIR = DOC_DIR / "build"

TYPER_EXAMPLES = Path(__file__).parent / "typer"
TEST_CALLBACKS = TYPER_EXAMPLES / "callback_record.json"


def check_callback(callback):
    if not TEST_CALLBACKS.is_file():
        return False
    return json.loads(TEST_CALLBACKS.read_text()).get(callback, False)


def clear_callbacks():
    if TEST_CALLBACKS.is_file():
        os.remove(TEST_CALLBACKS)


_TOKEN = re.compile(r"(?u)\b\w\w+\b")


def similarity(text1, text2):
    """
    Compute the TF-IDF cosine similarity between two texts.
    https://en.wikipedia.org/wiki/Cosine_similarity

    This mirrors the defaults of scikit-learn's TfidfVectorizer (lowercase,
    whole word tokens, smoothed idf, l2 norm) without the dependency.

    We use this to lazily evaluate the output of --help to our
    renderings.
    """
    docs = [Counter(_TOKEN.findall(text.lower())) for text in (text1, text2)]
    n_docs = len(docs)
    idf = {
        word: math.log((1 + n_docs) / (1 + sum(word in doc for doc in docs))) + 1
        for word in set(docs[0]) | set(docs[1])
    }
    vecs = [{word: count * idf[word] for word, count in doc.items()} for doc in docs]
    norms = [math.sqrt(sum(v * v for v in vec.values())) for vec in vecs]
    if not all(norms):
        return 0.0
    dot = sum(vecs[0][word] * vecs[1].get(word, 0.0) for word in vecs[0])
    return dot / (norms[0] * norms[1])


def pdf_text(pdf_path) -> t.List[str]:
    """
    Returns a list of page strings.
    """
    with open(pdf_path, "rb") as file:
        return [page.extract_text() for page in PdfReader(file).pages]


def img_similarity(expected, to_compare):
    """
    Calculate the Mean Squared Error between two images.
    MSE is a non-negative value, where 0 indicates perfect similarity.
    Higher values indicate less similarity.
    """
    img_a, img_b = resize_image_to_match(expected, to_compare)
    Image.fromarray(img_a).save(expected.parent / f"resized_{expected.name}")
    err = np.sum((img_a.astype("float") - img_b.astype("float")) ** 2)
    err /= float(img_a.shape[0] * img_a.shape[1])
    return err


def resize_image_to_match(source_image_path, target_image_path):
    target = np.asarray(Image.open(target_image_path).convert("RGB"))
    source = Image.open(source_image_path).convert("RGB")
    resized = source.resize((target.shape[1], target.shape[0]), Image.LANCZOS)
    return np.asarray(resized), target


def replace_in_file(file_path: str, search_string: str, replacement_string: str):
    with open(file_path, "r") as file:
        file_contents = file.read()

    with open(file_path, "w") as file:
        file.write(file_contents.replace(search_string, replacement_string))


@pytest.mark.skipif(sphinx_version[0] < 6, reason="Sphinx >=6.0 required to build docs")
def test_sphinx_html_build():
    """
    The documentation is extensive and exercises most of the features of the extension so
    we just check to see that our documentation builds!
    """
    shutil.rmtree(BUILD_DIR / "html", ignore_errors=True)

    # Create a Sphinx application instance
    app = Sphinx(
        SRC_DIR, SRC_DIR, BUILD_DIR / "html", BUILD_DIR / "doctrees", buildername="html"
    )

    assert app.config.typer_iframe_height_padding == 30

    # Build the documentation
    app.build()

    # Test passes if no Sphinx errors occurred during build
    assert not app.statuscode, "Sphinx documentation build failed"


def test_sphinx_text_build():
    shutil.rmtree(BUILD_DIR / "text", ignore_errors=True)

    # Create a Sphinx application instance
    app = Sphinx(
        SRC_DIR, SRC_DIR, BUILD_DIR / "text", BUILD_DIR / "doctrees", buildername="text"
    )

    # Build the documentation
    app.build()

    assert not app.statuscode, "Sphinx documentation build failed"


def test_sphinx_latex_build():
    shutil.rmtree(BUILD_DIR / "latex", ignore_errors=True)

    # Create a Sphinx application instance
    app = Sphinx(
        SRC_DIR,
        SRC_DIR,
        BUILD_DIR / "latex",
        BUILD_DIR / "doctrees",
        buildername="latex",
    )

    # Build the documentation
    app.build()

    assert not app.statuscode, "Sphinx documentation build failed"


def build_example(
    name,
    builder,
    example_dir=TYPER_EXAMPLES,
    clean_first=True,
    subprocess=False,
    project=None,
    parallel=0,
):
    cwd = os.getcwd()
    ex_dir = example_dir / name
    bld_dir = ex_dir / "build"
    if clean_first and bld_dir.exists():
        shutil.rmtree(bld_dir)

    os.chdir(example_dir / name)

    if not subprocess:
        app = Sphinx(
            ex_dir,
            example_dir,
            bld_dir / builder,
            bld_dir / "doctrees",
            buildername=builder,
            parallel=parallel,
        )

        assert app.config.typer_iframe_height_padding == 40

        # Build the documentation
        app.build()
    else:
        assert (
            os.system(
                f"uv run sphinx-build {ex_dir} {bld_dir / builder} -c {ex_dir.parent}"
            )
            == 0
        )

    os.chdir(cwd)
    if builder == "html":
        result = (bld_dir / builder / "index.html").read_text()
    elif builder == "text":
        result = (bld_dir / builder / "index.txt").read_text()
    elif builder == "latex":
        if not project:
            from conf import project

        result = (
            bld_dir / builder / f"{project.lower().replace(' ', '')}.tex"
        ).read_text()
    return bld_dir / builder, result


def scrub(output: str) -> str:
    """Scrub control code characters and ansi escape sequences for terminal colors from output"""
    return re.sub(r"\[\d+(?:;\d+)*m", "", output).replace("\t", "")


def get_ex_help(name, *subcommands, example_dir, command_file=None):
    ret = subprocess.run(
        [
            "uv",
            "run",
            "python",
            example_dir / name / f"{command_file or name}.py",
            *subcommands,
            "--help",
        ],
        capture_output=True,
        env={
            **os.environ,
            "PYTHONPATH": f"{os.environ.get('PYTHONPATH', '$PYTHONPATH')}:{example_dir / name}",
            "TERMINAL_WIDTH": str(os.environ.get("TERMINAL_WIDTH", 80)),
        },
    )
    return ret.stdout.decode() or ret.stderr.decode()


def get_typer_ex_help(name, *subcommands, command_file=None):
    return scrub(
        get_ex_help(
            name, *subcommands, example_dir=TYPER_EXAMPLES, command_file=command_file
        )
    )


def check_html(html, help_txt, iframe_number=0, threshold=0.85):
    soup = bs(html, "html.parser")
    iframes = soup.find_all("iframe")
    iframe = iframes[iframe_number]
    assert iframe is not None
    iframe_src = bs(iframe.attrs["srcdoc"], "html.parser")
    assert iframe_src is not None
    code = iframe_src.find("code")
    assert code is not None
    assert similarity(code.text, help_txt) > threshold
    return code.text


def check_svg(html, help_txt, svg_number=0, threshold=0.75):
    soup = bs(html, "html.parser")
    svg = soup.find_all("svg")[svg_number]
    assert svg is not None
    txt = svg.text.strip().replace("\xa0", " ")
    assert similarity(txt, help_txt) > threshold
    return txt


def check_text(html, help_txt, txt_number=0, threshold=0.95):
    soup = bs(html, "html.parser")
    txt = soup.find_all("pre")[txt_number]
    txt = txt.text.strip()
    for element in ["<pre>", "<span>", "</span>", "</pre>"]:
        txt = txt.strip(element)
    assert txt is not None
    sim = similarity(txt, help_txt)
    assert sim > threshold, f"{sim} is below threshold {threshold}"
    return txt


def test_typer_ex_reference():
    clear_callbacks()

    html_dir, index_html = build_example(
        "reference", "html", example_dir=TYPER_EXAMPLES
    )

    doc_help = check_svg(
        (html_dir / "reference.html").read_text(),
        get_typer_ex_help("reference", command_file="cli-ref"),
        0,
        threshold=0.82,
    )
    assert "python -m cli-ref.py" in doc_help

    index = bs(index_html, "html.parser")
    ref1, ref2, ref3 = tuple(
        index.find_all("section")[0].find_all("p")[0].find_all("a")
    )
    for ref in (ref1, ref2):
        assert ref.text == "python -m cli-ref.py"
        assert ref.attrs["href"] == "reference.html#python-m-cli-ref-py"

    assert ref3.text == "command"
    assert ref3.attrs["href"] == "reference.html#python-m-cli-ref-py"


def _reference_links(index_html):
    """Return the anchors in the two reference paragraphs of the reference index."""
    index = bs(index_html, "html.parser")
    paragraphs = index.find_all("section")[0].find_all("p")
    return paragraphs[0].find_all("a"), paragraphs[1].find_all("a")


def test_typer_ex_reference_parallel():
    """
    Cross references must survive a parallel read, where each worker process
    records targets into its own copy of the environment and the domain has
    to merge them back together.
    """
    clear_callbacks()
    _, index_html = build_example(
        "reference", "html", example_dir=TYPER_EXAMPLES, parallel=2
    )
    refs, no_section_refs = _reference_links(index_html)
    assert [ref.attrs["href"] for ref in refs] == [
        "reference.html#python-m-cli-ref-py"
    ] * 3
    assert [ref.attrs["href"] for ref in no_section_refs] == [
        "nosections.html#noref"
    ] * 2


def test_typer_ex_reference_no_sections():
    """
    A command rendered without :make-sections: must still be a valid
    reference target, and the anchor it points at must exist on the page.
    """
    clear_callbacks()
    html_dir, index_html = build_example(
        "reference", "html", example_dir=TYPER_EXAMPLES
    )
    _, refs = _reference_links(index_html)
    assert [ref.attrs["href"] for ref in refs] == ["nosections.html#noref"] * 2
    assert refs[0].text == "noref"
    assert refs[1].text == "no-sections"

    target_page = bs((html_dir / "nosections.html").read_text(), "html.parser")
    assert target_page.find(id="noref") is not None


def test_typer_ex_reference_inventory():
    """
    Commands are exported to objects.inv so intersphinx can link to them.
    """
    from sphinx.util.inventory import InventoryFile

    clear_callbacks()
    html_dir, _ = build_example("reference", "html", example_dir=TYPER_EXAMPLES)
    with open(html_dir / "objects.inv", "rb") as f:
        inv = InventoryFile.load(f, "", os.path.join)
    commands = inv["typer:command"]

    def uri(item):
        # Sphinx < 8.2 uses plain tuples, newer versions use _InventoryItem
        return item.uri if hasattr(item, "uri") else item[2]

    assert uri(commands["python-m-cli-ref-py"]) == "reference.html#python-m-cli-ref-py"
    assert uri(commands["noref"]) == "nosections.html#noref"


def test_typer_reference_stale_targets_cleared(tmp_path):
    """
    When a document is re-read on an incremental build, targets it previously
    contributed must be dropped so a renamed command does not linger.
    """
    src = tmp_path / "src"
    shutil.copytree(
        TYPER_EXAMPLES / "reference", src, ignore=shutil.ignore_patterns("build")
    )
    (src / "conf.py").write_text(
        "import sys, pathlib\n"
        "sys.path.insert(0, str(pathlib.Path(__file__).parent))\n"
        "project = 'stale'\n"
        "extensions = ['sphinxcontrib.typer']\n"
    )

    def build():
        app = Sphinx(
            src, src, tmp_path / "html", tmp_path / "doctrees", buildername="html"
        )
        app.build()
        return app.env.domaindata["typer"]["commands"]

    # conf.py above modifies sys.path, don't let that leak into other tests
    sys_path = list(sys.path)
    try:
        commands = build()
        assert "noref" in commands
        assert commands["noref"][0] == "nosections"

        replace_in_file(src / "nosections.rst", ":prog: noref", ":prog: renamed")
        commands = build()
        assert "renamed" in commands
        assert "noref" not in commands
    finally:
        sys.path[:] = sys_path


def test_typer_ex_themes_do_not_collide():
    """
    Two renderings of the same command at the same width but with different
    themes must not share SVG CSS class names, otherwise the inline styles of
    one restyle the other when both are embedded in the same page.
    https://github.com/sphinx-contrib/typer/issues/32
    """
    clear_callbacks()
    _, index_html = build_example("themes", "html", example_dir=TYPER_EXAMPLES)
    svgs = bs(index_html, "html.parser").find_all("svg")
    assert len(svgs) == 2

    def class_prefixes(svg):
        return set(re.findall(r"\.([\w-]+?)-r\d+ *\{", str(svg)))

    light, dark = (class_prefixes(svg) for svg in svgs)
    assert light and dark
    assert light.isdisjoint(dark), f"shared svg class prefixes: {light & dark}"


def test_typer_ex_nested_prog():
    """
    :prog: must replace the entire invocation path, including for commands
    nested more than one level deep, so the module name of the root app never
    leaks into the usage line.
    https://github.com/sphinx-contrib/typer/issues/23
    """
    clear_callbacks()
    _, index_html = build_example("nested_prog", "html", example_dir=TYPER_EXAMPLES)
    blocks = [pre.get_text() for pre in bs(index_html, "html.parser").find_all("pre")]
    assert len(blocks) == 4
    assert "__main__" not in index_html
    assert "Usage: foo [OPTIONS]" in blocks[0]
    assert "Usage: foo nested [OPTIONS]" in blocks[1]
    assert "Usage: foo nested command [OPTIONS]" in blocks[2]
    assert "Usage: foo nested other [OPTIONS]" in blocks[3]


class _FakeDirective:
    """Minimal stand in for a TyperDirective for hook unit tests."""

    class env:
        class config:
            typer_playwright_install = True

    class _Logger:
        def info(self, *args, **kwargs): ...

        def warning(self, *args, **kwargs): ...

    logger = _Logger()

    def severe(self, message):
        from docutils.parsers.rst import DirectiveError

        return DirectiveError(4, message)


def test_playwright_install_browser(monkeypatch):
    """
    typer_install_browser invokes playwright's cli through subprocess using
    the running interpreter, so the browser lands in the active environment.
    """
    from sphinxcontrib import typer as sct

    calls = []
    monkeypatch.setattr(
        sct.subprocess, "run", lambda *args, **kwargs: calls.append((args, kwargs))
    )
    sct.typer_install_browser(_FakeDirective())
    assert calls == [
        (
            (([sys.executable, "-m", "playwright", "install", "chromium"],)),
            {"check": True},
        )
    ]


def _missing_browser(monkeypatch, fail_times):
    """
    Patch playwright's chromium launch to raise the missing executable error
    the first fail_times calls, then delegate to the real launch.
    """
    from playwright.sync_api import BrowserType, Error

    real_launch = BrowserType.launch
    attempts = []

    def launch(self, *args, **kwargs):
        attempts.append(1)
        if len(attempts) <= fail_times:
            raise Error(
                "BrowserType.launch: Executable doesn't exist at /nowhere/chrome\n"
                "Please run the following command to download new browsers:\n"
                "    playwright install"
            )
        return real_launch(self, *args, **kwargs)

    monkeypatch.setattr(BrowserType, "launch", launch)
    return attempts


def test_playwright_auto_install(monkeypatch):
    """
    When the browser is missing, typer_get_page installs it and retries once.
    """
    from sphinxcontrib import typer as sct

    attempts = _missing_browser(monkeypatch, fail_times=1)
    installs = []
    monkeypatch.setattr(sct, "typer_install_browser", lambda d: installs.append(d))

    with sct.typer_get_page(_FakeDirective()) as page:
        page.set_content("<html><body><p id='x'>hi</p></body></html>")
        assert page.locator("#x").inner_text() == "hi"
    assert len(installs) == 1
    assert len(attempts) == 2


def test_playwright_auto_install_disabled(monkeypatch):
    """
    With typer_playwright_install off the missing browser error is reported
    as a directive error and no install is attempted.
    """
    from docutils.parsers.rst import DirectiveError
    from sphinxcontrib import typer as sct

    _missing_browser(monkeypatch, fail_times=1)
    installs = []
    monkeypatch.setattr(sct, "typer_install_browser", lambda d: installs.append(d))

    directive = _FakeDirective()
    directive.env.config.typer_playwright_install = False
    with pytest.raises(DirectiveError) as exc:
        with sct.typer_get_page(directive):
            pass
    assert "playwright install chromium" in exc.value.msg
    assert installs == []


def _svg_class_prefixes(svg):
    return set(re.findall(r"\.([\w-]+?)-r\d+ *\{", str(svg)))


def test_typer_ex_dark_theme():
    """
    With :dark-theme: the help is rendered twice for html builders and wrapped
    in only-light / only-dark containers so the active theme mode picks one.
    https://github.com/sphinx-contrib/typer/issues/62
    """
    clear_callbacks()
    html_dir, index_html = build_example("dark", "html", example_dir=TYPER_EXAMPLES)
    soup = bs(index_html, "html.parser")

    # svg: root + 2 nested subcommands, each rendered light and dark
    light_svgs = soup.select("div.only-light.typer-only-light svg")
    dark_svgs = soup.select("div.only-dark.typer-only-dark svg")
    assert len(light_svgs) == 3
    assert len(dark_svgs) == 3
    for light, dark in zip(light_svgs, dark_svgs):
        assert _svg_class_prefixes(light).isdisjoint(_svg_class_prefixes(dark))

    # sections and their targets are not duplicated
    ids = [sec.get("id") for sec in soup.find_all("section")]
    for cmd in [
        "composite-subgroup",
        "composite-subgroup-echo",
        "composite-subgroup-multiply",
    ]:
        assert ids.count(cmd) == 1

    # html: one iframe per mode with different page backgrounds
    light_iframes = soup.select("div.only-light iframe")
    dark_iframes = soup.select("div.only-dark iframe")
    assert len(light_iframes) == 1 and len(dark_iframes) == 1
    assert light_iframes[0]["srcdoc"] != dark_iframes[0]["srcdoc"]

    # the stylesheet that hides the inactive mode is installed and linked
    assert (html_dir / "_static" / "sphinxcontrib_typer.css").is_file()
    assert soup.find("link", href=re.compile(r"sphinxcontrib_typer\.css")) is not None


def test_typer_ex_dark_theme_text_builder():
    """
    Non-html builders only render the primary theme.
    """
    clear_callbacks()
    _, index_txt = build_example("dark", "text", example_dir=TYPER_EXAMPLES)
    assert index_txt.count("Usage:") == 4


def _build_dark_project(tmp_path, html_theme, conf_lines=()):
    """
    Build a one page project rendering a command with the given html theme and
    extra conf.py lines, returning the number of light and dark svg renderings.
    """
    src = tmp_path / "src"
    src.mkdir()
    (src / "conf.py").write_text(
        "import sys\n"
        f"sys.path.insert(0, {str(TYPER_EXAMPLES / 'composite')!r})\n"
        "project = 'dark'\n"
        "extensions = ['sphinxcontrib.typer']\n"
        f"html_theme = {html_theme!r}\n" + "".join(f"{line}\n" for line in conf_lines)
    )
    (src / "index.rst").write_text(
        "Dark\n====\n\n"
        ".. typer:: composite.cli.app:repeat\n"
        "    :prog: composite repeat\n"
        "    :preferred: svg\n"
        "    :width: 65\n"
    )
    sys_path = list(sys.path)
    try:
        app = Sphinx(
            src, src, tmp_path / "html", tmp_path / "doctrees", buildername="html"
        )
        app.build()
    finally:
        sys.path[:] = sys_path
    soup = bs((tmp_path / "html" / "index.html").read_text(), "html.parser")
    return (
        len(soup.select("div.typer-only-light svg")),
        len(soup.select("div.typer-only-dark svg")),
        len(soup.select("svg.rich-terminal")),
    )


def test_typer_dark_theme_config_default(tmp_path):
    """
    typer_dark_theme in conf.py applies to directives without :dark-theme:.
    """
    assert _build_dark_project(
        tmp_path, "alabaster", ["typer_dark_theme = 'dark'"]
    ) == (
        1,
        1,
        2,
    )


def test_typer_dark_theme_auto_known_theme(tmp_path):
    """
    When typer_dark_theme is not set and html_theme is known to support light
    and dark modes, the dark theme defaults to "dark".
    """
    assert _build_dark_project(tmp_path, "furo") == (1, 1, 2)


def test_typer_dark_theme_auto_unknown_theme(tmp_path):
    """
    Themes not known to support dark mode render once by default.
    """
    assert _build_dark_project(tmp_path, "alabaster") == (0, 0, 1)


def test_typer_dark_theme_explicit_off(tmp_path):
    """
    typer_dark_theme = None switches the automatic default off.
    """
    assert _build_dark_project(tmp_path, "furo", ["typer_dark_theme = None"]) == (
        0,
        0,
        1,
    )


def _build_project(
    tmp_path, index_rst, conf_lines=(), buildername="html", html_theme="alabaster"
):
    """
    Build a one page project from the given index.rst and extra conf.py lines.
    Returns the rendered index and the captured sphinx warnings.
    """
    src = tmp_path / "src"
    src.mkdir(parents=True, exist_ok=True)
    (src / "conf.py").write_text(
        "\n".join(
            [
                "import sys",
                f"sys.path.insert(0, {str(TYPER_EXAMPLES / 'composite')!r})",
                f"sys.path.insert(0, {str(TYPER_EXAMPLES / 'options')!r})",
                "project = 'proj'",
                "extensions = ['sphinxcontrib.typer']",
                f"html_theme = {html_theme!r}",
                *conf_lines,
            ]
        )
        + "\n"
    )
    (src / "index.rst").write_text(index_rst)
    warnings = io.StringIO()
    sys_path = list(sys.path)
    try:
        app = Sphinx(
            src,
            src,
            tmp_path / "out",
            tmp_path / "doctrees",
            buildername=buildername,
            status=None,
            warning=warnings,
        )
        app.build()
    finally:
        sys.path[:] = sys_path
    ext = {"html": "html", "text": "txt", "xml": "xml"}[buildername]
    # running many Sphinx apps in one process re-registers nodes/directives,
    # those warnings are noise for our purposes
    warnings = "\n".join(
        line
        for line in warnings.getvalue().splitlines()
        if "already registered" not in line
    )
    return (tmp_path / "out" / f"index.{ext}").read_text(), warnings


_REPEAT = """Index
=====

.. typer:: composite.cli.app:repeat
    :prog: composite repeat
    :width: 65
{options}
"""


def test_typer_any_role():
    """
    Commands resolve through the builtin :any: role.
    """
    clear_callbacks()
    _, index_html = build_example("reference", "html", example_dir=TYPER_EXAMPLES)
    paragraphs = bs(index_html, "html.parser").find_all("section")[0].find_all("p")
    (ref,) = paragraphs[2].find_all("a")
    assert ref.attrs["href"] == "reference.html#python-m-cli-ref-py"
    assert ref.text == "python -m cli-ref.py"


def test_typer_builders_option(tmp_path):
    """
    :builders: overrides the render target for the given builder.
    """
    html, warnings = _build_project(
        tmp_path, _REPEAT.format(options="    :builders: html=text")
    )
    assert not warnings
    soup = bs(html, "html.parser")
    assert not soup.select("svg.rich-terminal")
    assert "Usage: composite repeat" in soup.find("pre").get_text()


def test_typer_unknown_builder_falls_back_to_text(tmp_path):
    """
    Builders with no configured render targets fall back to text output.
    """
    xml, warnings = _build_project(
        tmp_path, _REPEAT.format(options=""), buildername="xml"
    )
    assert not warnings
    assert "<literal_block" in xml
    assert "Usage: composite repeat" in xml


def test_typer_markup_mode_option(tmp_path):
    """
    :markup-mode: controls how rich markup in help text is interpreted.
    """
    page = """Index
=====

.. typer:: options_cli.app:hello
    :prog: hello
    :preferred: text
    :width: 65
{options}
"""
    markdown, warnings = _build_project(
        tmp_path / "markdown", page.format(options="    :markup-mode: markdown")
    )
    assert not warnings
    assert (
        "Say [bold]hello[/bold]." in bs(markdown, "html.parser").find("pre").get_text()
    )

    rich, warnings = _build_project(
        tmp_path / "rich", page.format(options="    :markup-mode: rich")
    )
    assert not warnings
    assert "[bold]" not in rich
    assert "Say hello." in bs(rich, "html.parser").find("pre").get_text()


def test_typer_hidden_command(tmp_path):
    """
    A directive pointed at a hidden command renders nothing.
    """
    html, warnings = _build_project(
        tmp_path,
        "Index\n=====\n\n.. typer:: options_cli.app:secret\n    :preferred: text\n",
    )
    assert not warnings
    assert "Usage:" not in html


def test_typer_callable_render_options(tmp_path):
    """
    The *-kwargs options may point at a callable returning the kwargs dict, and
    a callable returning anything else is reported.
    """
    html, warnings = _build_project(
        tmp_path / "good",
        _REPEAT.format(
            options="    :preferred: svg\n    :svg-kwargs: options_cli.svg_kwargs"
        ),
    )
    assert not warnings
    svg = bs(html, "html.parser").select_one("svg.rich-terminal")
    title = svg.find("text").get_text().replace("\xa0", " ")
    assert title == "custom title for composite repeat"

    _, warnings = _build_project(
        tmp_path / "bad",
        _REPEAT.format(
            options="    :preferred: svg\n    :svg-kwargs: options_cli.bad_kwargs"
        ),
    )
    assert "Invalid svg-kwargs, must be a dict or callable" in warnings


def test_typer_callable_config_hook(tmp_path):
    """
    Render hooks may be configured as callables instead of import strings.
    """
    html, _ = _build_project(
        tmp_path,
        _REPEAT.format(options="    :preferred: html"),
        conf_lines=[
            "def typer_render_html(directive, normal_cmd, html_page):",
            "    return f'<div class=\"hooked\">{normal_cmd}</div>'",
        ],
    )
    soup = bs(html, "html.parser")
    assert soup.find("div", class_="hooked").get_text() == "composite repeat"
    assert not soup.find("iframe")


def test_typer_import_errors(tmp_path):
    """
    Import failures are reported with the reason.
    """
    page = """Index
=====

.. typer:: nonexistent.module:app
    :preferred: text

.. typer:: options_raises.app
    :preferred: text

.. typer:: options_exit.app
    :preferred: text

.. typer:: options_cli.not_an_app
    :preferred: text
"""
    _, warnings = _build_project(tmp_path, page)
    assert 'Failed to import "nonexistent.module:app"' in warnings
    assert "boom during import" in warnings
    assert "The module appeared to call sys.exit()" in warnings
    assert "is not a Typer app or command" in warnings


def test_playwright_other_launch_errors_propagate(monkeypatch):
    """
    Launch errors other than a missing browser are not swallowed or retried.
    """
    from playwright.sync_api import BrowserType, Error
    from sphinxcontrib import typer as sct

    def launch(self, *args, **kwargs):
        raise Error("something else went wrong")

    monkeypatch.setattr(BrowserType, "launch", launch)
    installs = []
    monkeypatch.setattr(sct, "typer_install_browser", lambda d: installs.append(d))
    with pytest.raises(Error, match="something else"):
        with sct.typer_get_page(_FakeDirective()):
            pass
    assert installs == []


def test_playwright_not_installed(monkeypatch):
    """
    A missing playwright package is reported as a directive error.
    """
    from docutils.parsers.rst import DirectiveError
    from sphinxcontrib import typer as sct

    monkeypatch.setitem(sys.modules, "playwright.sync_api", None)
    with pytest.raises(DirectiveError) as exc:
        with sct.typer_get_page(_FakeDirective()):
            pass
    assert "requires playwright" in exc.value.msg


def test_cairosvg_not_installed(monkeypatch, tmp_path):
    """
    A missing cairosvg package is reported as a directive error rather than
    silently producing no pdf.
    """
    from docutils.parsers.rst import DirectiveError
    from sphinxcontrib import typer as sct

    monkeypatch.setitem(sys.modules, "cairosvg", None)
    with pytest.raises(DirectiveError) as exc:
        sct.typer_svg2pdf(_FakeDirective(), "<svg/>", tmp_path / "out.pdf")
    assert "cairosvg must be installed" in exc.value.msg
    assert not (tmp_path / "out.pdf").exists()


def test_typer_command_factory(tmp_path):
    """
    The directive accepts a callable returning a click command.
    """
    html, warnings = _build_project(
        tmp_path,
        "Index\n=====\n\n.. typer:: options_cli.command_factory\n    :prog: factory\n"
        "    :preferred: text\n    :width: 65\n",
    )
    assert not warnings
    assert (
        "Usage: factory [OPTIONS] COMMAND [ARGS]..."
        in bs(html, "html.parser").find("pre").get_text()
    )


def test_typer_ex_composite():
    EX_DIR = TYPER_EXAMPLES / "composite/composite"
    cli_py = EX_DIR / "cli.py"
    group_py = EX_DIR / "group.py"
    echo_py = EX_DIR / "echo.py"

    try:
        clear_callbacks()

        def test_build(first=False):
            _, html = build_example(
                "composite",
                "html",
                example_dir=TYPER_EXAMPLES,
                clean_first=first,
                subprocess=True,
            )

            # we test that list_commands order is honored
            subcommands = ["subgroup", "subgroup multiply", "subgroup echo", "repeat"]
            helps = [
                get_typer_ex_help("composite", command_file="composite/cli"),
                *[
                    get_typer_ex_help(
                        "composite", *cmd.split(), command_file="composite/cli"
                    )
                    for cmd in subcommands
                ],
            ]

            doc_helps = []
            for idx, help in enumerate(helps):
                doc_helps.append(check_text(html, help, idx, threshold=0.88))

            return doc_helps

        index_html = TYPER_EXAMPLES / "composite/build/html/index.html"
        composite_html = TYPER_EXAMPLES / "composite/build/html/composite.html"
        echo_html = TYPER_EXAMPLES / "composite/build/html/echo.html"
        multiply_html = TYPER_EXAMPLES / "composite/build/html/multiply.html"
        repeat_html = TYPER_EXAMPLES / "composite/build/html/repeat.html"
        subgroup_html = TYPER_EXAMPLES / "composite/build/html/subgroup.html"
        files = [
            index_html,
            composite_html,
            echo_html,
            multiply_html,
            repeat_html,
            subgroup_html,
        ]

        test_build(first=True)
        times = [pth.stat().st_mtime for pth in files]
        test_build()
        times2 = [pth.stat().st_mtime for pth in files]
        assert times == times2, "Rebuild was not cached!"

        # test that
        replace_in_file(
            cli_py, "Lets do stuff with strings.", "XX Lets do stuff with strings. XX"
        )
        txts = test_build()
        times3 = [pth.stat().st_mtime for pth in files]
        for idx, (t3, t2) in enumerate(zip(times3, times2)):
            assert t3 > t2, f"file {files[idx]} not regenerated."
        assert "XX Lets do stuff with strings. XX" in txts[0]

        replace_in_file(
            group_py, "Subcommands are here.", "XX Subcommands are here. XX"
        )
        helps = test_build()
        assert "XX Subcommands are here. XX" in helps[0]
        assert "XX Subcommands are here. XX" in helps[1]
        times4 = [pth.stat().st_mtime for pth in files]
        for idx, (t4, t3) in enumerate(zip(times4, times3)):
            if files[idx].name in ["echo.html", "multiply.html", "repeat.html"]:
                continue
            assert t4 > t3, f"file {files[idx]} not regenerated."

        replace_in_file(
            echo_py, "def echo(name: str):", "def echo(name: str, name2: str):"
        )
        helps = test_build()
        assert "name2" in helps[3]
        times5 = [pth.stat().st_mtime for pth in files]
        for idx, (t5, t4) in enumerate(zip(times5, times4)):
            if files[idx].name in ["composite.html", "multiply.html", "repeat.html"]:
                continue
            assert t5 > t4, f"file {files[idx]} not regenerated."

        # check navbar
        navitems = list(
            bs(index_html.read_text(), features="lxml")
            .find("div", class_="sphinxsidebar")
            .find_all("a")
        )
        assert navitems[1].text == "composite"
        assert navitems[2].text.strip() == "python -m cli.py repeat"
        assert navitems[3].text == "cli subgroup"
        assert navitems[4].text == "cli subgroup echo"
        assert navitems[5].text == "cli subgroup multiply"

    finally:
        os.system(f"git checkout {cli_py}")
        os.system(f"git checkout {group_py}")
        os.system(f"git checkout {echo_py}")


def test_typer_ex_subdocdir_latex():
    """
    Regression test for https://github.com/sphinx-contrib/typer/issues/58

    When a typer directive is in a document located in a subdirectory of the
    source root (e.g. via autodoc from a nested module), the image URI must be
    computed relative to the document's directory, not srcdir.  The buggy code
    used ``os.path.relpath(path, self.env.srcdir)`` which resolves to the wrong
    location when ``self.env.docname`` contains a path separator.
    """
    import io

    ex_dir = TYPER_EXAMPLES / "subdocdir"
    bld_dir = ex_dir / "build"
    shutil.rmtree(bld_dir, ignore_errors=True)

    warnings_io = io.StringIO()
    app = Sphinx(
        ex_dir,
        TYPER_EXAMPLES,
        bld_dir / "latex",
        bld_dir / "doctrees",
        buildername="latex",
        warning=warnings_io,
    )
    app.build()
    assert not app.statuscode, "Sphinx build failed"

    # With the buggy URI computation (relative to srcdir instead of the
    # document's directory), Sphinx cannot find the generated PDF and emits an
    # "image file not readable" warning.  A clean build must produce no such
    # warning.
    warning_text = warnings_io.getvalue()
    assert "image.not_readable" not in warning_text, (
        "Image path was not resolved correctly for a directive in a "
        f"subdirectory document (see issue #58).\nWarnings:\n{warning_text}"
    )

    if bld_dir.exists():
        shutil.rmtree(bld_dir)


def test_typer_render_html():
    """
    Render a Typer app to html and verify the iframe/svg/text output as well as
    that the html render hooks fired (and that the cached iframe height avoided
    spinning up a web driver).
    """
    clear_callbacks()

    bld_dir, html = build_example("render", "html", example_dir=TYPER_EXAMPLES)

    help_txt = get_typer_ex_help("render")

    check_html(html, help_txt)
    check_svg(html, help_txt, threshold=0.7)
    check_text(html, help_txt)

    assert check_callback("typer_render_html")
    assert check_callback("typer_get_iframe_height")
    # the :iframe-height: option should short-circuit the browser page hook
    assert not check_callback("typer_get_page")

    if bld_dir.exists():
        shutil.rmtree(bld_dir.parent)


def test_typer_render_latex():
    """
    Render a Typer app to latex and verify the svg->pdf and png conversions, the
    associated render hooks (typer_svg2pdf, typer_convert_png) and the rendered
    pdf/png content.
    """
    clear_callbacks()

    bld_dir, latex = build_example("render", "latex", example_dir=TYPER_EXAMPLES)

    help_txt = get_typer_ex_help("render")

    assert check_callback("typer_svg2pdf")
    assert check_callback("typer_convert_png")
    # png conversion is done with a screenshot from the browser page hook
    assert check_callback("typer_get_page")

    # only the text render emits literal text into the latex source
    assert latex.count("Usage") == 1

    pdfs = list(bld_dir.glob("**/*.pdf"))
    assert len(pdfs) == 1, "Should have rendered the help 1 time as pdf"
    pdf = pdfs[0]
    assert pdf.with_suffix(".svg").is_file()
    assert pdf.name.split(".")[0] in latex
    pdf_txt = pdf_text(pdf)[0]
    assert similarity(pdf_txt, help_txt) > 0.9

    pngs = list(bld_dir.glob("**/*.png"))
    assert len(pngs) == 1, "Should have rendered the help 1 time as png"
    assert img_similarity(TYPER_EXAMPLES / "render" / "render.png", pngs[0]) < 9000

    if bld_dir.exists():
        shutil.rmtree(bld_dir.parent)


def test_typer_factory():
    """
    The directive target may be a factory callable that returns a Typer app
    (the callable branch of resolve_root_command).  Regression test for the
    factory being passed to get_command instead of its return value.
    """
    bld_dir, html = build_example("factory", "html", example_dir=TYPER_EXAMPLES)

    help_txt = get_typer_ex_help("factory")
    check_text(html, help_txt)

    if bld_dir.exists():
        shutil.rmtree(bld_dir.parent)


def test_enums():
    from sphinxcontrib.typer import RenderTarget, RenderTheme

    for target in RenderTarget:
        assert target.value == str(target)
    for theme in RenderTheme:
        assert theme.value == str(theme)
