import pytest
import re
from sphinx.application import Sphinx
from sphinx import version_info as sphinx_version
from typer import __version__ as typer_version
import typing as t
import os
from pathlib import Path
import shutil
import subprocess
from bs4 import BeautifulSoup as bs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from skimage import io
from skimage.transform import resize
from pypdf import PdfReader
import numpy as np
import json

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


def similarity(text1, text2):
    """
    Compute the cosine similarity between two texts.
    https://en.wikipedia.org/wiki/Cosine_similarity

    We use this to lazily evaluate the output of --help to our
    renderings.
    """
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]


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
    io.imsave(str(expected.parent / f"resized_{expected.name}"), img_a)
    err = np.sum((img_a.astype("float") - img_b.astype("float")) ** 2)
    err /= float(img_a.shape[0] * img_a.shape[1])
    return err


def resize_image_to_match(source_image_path, target_image_path):
    target = io.imread(target_image_path)[:, :, :3]
    source = io.imread(source_image_path)[:, :, :3]
    resized = resize(source, target.shape[0:2], anti_aliasing=True)
    return np.clip(resized * 255, 0, 255).astype(np.uint8), target


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
            bs(index_html.read_text()).find("div", class_="sphinxsidebar").find_all("a")
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
    # the :iframe-height: option should short-circuit the selenium web driver
    assert not check_callback("typer_get_web_driver")

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
