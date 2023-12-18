import pytest
from sphinx.application import Sphinx
import typing as t
import os
from pathlib import Path
import shutil
import subprocess
from bs4 import BeautifulSoup as bs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from skimage import io
from pypdf import PdfReader
import numpy as np
import json

test_callbacks = {}

DOC_DIR = Path(__file__).parent.parent / 'doc'
SRC_DIR = DOC_DIR / 'source'
BUILD_DIR = DOC_DIR / 'build'

CLICK_EXAMPLES = Path(__file__).parent / 'click'
TEST_CALLBACKS = CLICK_EXAMPLES / 'callback_record.json'


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
    with open(pdf_path, 'rb') as file:
        return [page.extract_text() for page in PdfReader(file).pages]

def img_similarity(image_path1, image_path2):
    """
    Calculate the Mean Squared Error between two images.
    MSE is a non-negative value, where 0 indicates perfect similarity.
    Higher values indicate less similarity.
    """
    img_a = io.imread(image_path1)
    img_b = io.imread(image_path2)
    err = np.sum((img_a.astype("float") - img_b.astype("float")) ** 2)
    err /= float(img_a.shape[0] * img_a.shape[1])
    return err


def test_sphinx_html_build():
    """
    The documentation is extensive and exercises most of the features of the extension so
    we just check to see that our documentation builds!
    """
    shutil.rmtree(BUILD_DIR / 'html', ignore_errors=True)
    if (SRC_DIR / 'typer_cache.json').exists():
        os.remove(SRC_DIR / 'typer_cache.json')

    # Create a Sphinx application instance
    app = Sphinx(
        SRC_DIR,
        SRC_DIR,
        BUILD_DIR / 'html',
        BUILD_DIR / 'doctrees',
        buildername='html'
    )

    # Build the documentation
    app.build()

    # Test passes if no Sphinx errors occurred during build
    assert not app.statuscode, "Sphinx documentation build failed"


def test_sphinx_text_build():
    
    shutil.rmtree(BUILD_DIR / 'text', ignore_errors=True)

    # Create a Sphinx application instance
    app = Sphinx(
        SRC_DIR,
        SRC_DIR,
        BUILD_DIR / 'text',
        BUILD_DIR / 'doctrees',
        buildername='text'
    )

    # Build the documentation
    app.build()

    assert not app.statuscode, "Sphinx documentation build failed"


def test_sphinx_latex_build():
    
    shutil.rmtree(BUILD_DIR / 'latex', ignore_errors=True)

    # Create a Sphinx application instance
    app = Sphinx(
        SRC_DIR,
        SRC_DIR,
        BUILD_DIR / 'latex',
        BUILD_DIR / 'doctrees',
        buildername='latex'
    )

    # Build the documentation
    app.build()

    assert not app.statuscode, "Sphinx documentation build failed"


def build_click_example(name, builder):
    cwd = os.getcwd()
    ex_dir = CLICK_EXAMPLES / name
    bld_dir = ex_dir / 'build'
    if bld_dir.exists():
        shutil.rmtree(bld_dir)

    os.chdir(CLICK_EXAMPLES / name)

    app = Sphinx(
        ex_dir,
        CLICK_EXAMPLES,
        bld_dir / builder,
        bld_dir / 'doctrees',
        buildername=builder
    )

    # Build the documentation
    app.build()
    os.chdir(cwd)
    if builder == 'html':
        result = (bld_dir / builder / 'index.html').read_text()
    elif builder == 'text':
        result = (bld_dir / builder / 'index.txt').read_text()
    elif builder == 'latex':
        from conf import project
        result = (
            bld_dir / builder / 
            f'{project.lower().replace(" ", "")}.tex'
        ).read_text()
    return bld_dir / builder, result


def get_click_ex_help(name, *subcommands):
    return subprocess.run(
        [
            'poetry',
            'run',
            'python',
            CLICK_EXAMPLES / name / f'{name}.py',
            *subcommands,
            '--help'
        ],
        capture_output=True
    ).stdout.decode()


def check_html(html, help_txt, iframe_number=0):
    soup = bs(html, 'html.parser')
    iframe = soup.find_all('iframe')[iframe_number]
    assert iframe is not None
    iframe_src = bs(iframe.attrs['srcdoc'], 'html.parser')
    assert iframe_src is not None
    code = iframe_src.find('code')
    assert code is not None
    assert similarity(code.text, help_txt) > 0.95


def check_svg(html, help_txt, svg_number=0):
    soup = bs(html, 'html.parser')
    svg = soup.find_all('svg')[svg_number]
    assert svg is not None
    assert similarity(svg.text.strip(), help_txt) > 0.75


def check_text(html, help_txt, txt_number=0):
    soup = bs(html, 'html.parser')
    txt = soup.find_all('pre')[txt_number]
    assert txt is not None
    assert similarity(txt.text.strip(), help_txt) > 0.95


def test_click_ex_validation():
    clear_callbacks()

    bld_dir, html = build_click_example('validation', 'html')
    help_txt = get_click_ex_help('validation')

    check_html(html, help_txt)

    assert check_callback('typer_render_html')

    check_svg(html, help_txt)
    check_text(html, help_txt)

    if bld_dir.exists():
        shutil.rmtree(bld_dir.parent)


def test_click_text_build_works():

    bld_dir, text = build_click_example('validation', 'text')
    help_txt = get_click_ex_help('validation')
    assert similarity(text, help_txt) > 0.95
    assert text.count('Usage:') == 3, 'Should have rendered the help 3 times as text'
    if bld_dir.exists():
        shutil.rmtree(bld_dir.parent)


def test_click_latex_build_works():
    """
    also tests the convert-png option
    """

    bld_dir, latex = build_click_example('validation', 'latex')
    help_txt = get_click_ex_help('validation')

    # make sure the expected text rendered at least once
    assert latex.count('Usage: validation [OPTIONS]') == 1

    # get all pdf files from the build directory
    pdf = bld_dir / 'validation_669c6dad.pdf'

    assert (bld_dir / 'validation_669c6dad.svg').is_file()

    assert len(list(bld_dir.glob('**/*.pdf'))) == 1, 'Should have rendered the help 1 time as pdf'
    assert pdf.name.split('.')[0] in latex
    pdf_txt = pdf_text(pdf)[0]
    assert similarity(pdf_txt, help_txt) > 0.95

    assert len(list(bld_dir.glob('**/*.png'))) == 1, 'Should have rendered the help 1 time as png'
    html_png = bld_dir / 'validation_0b121597.png'
    assert img_similarity(CLICK_EXAMPLES / 'validation' / 'html.png', html_png) < 1000
