import pytest
from sphinx.application import Sphinx
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


def img_similarity(expected, to_compare):
    """
    Calculate the Mean Squared Error between two images.
    MSE is a non-negative value, where 0 indicates perfect similarity.
    Higher values indicate less similarity.
    """
    img_a, img_b = resize_image_to_match(expected, to_compare)
    io.imsave(str(expected.parent / f'resized_{expected.name}'), img_a)
    err = np.sum((img_a.astype("float") - img_b.astype("float")) ** 2)
    err /= float(img_a.shape[0] * img_a.shape[1])
    return err

def resize_image_to_match(source_image_path, target_image_path):
    target = io.imread(target_image_path)[:,:,:3]
    source = io.imread(source_image_path)[:,:,:3]
    resized = resize(
        source,
        target.shape[0:2],
        anti_aliasing=True
    )
    return np.clip(resized * 255, 0, 255).astype(np.uint8), target


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

    assert app.config.typer_iframe_height_padding == 30
    assert app.config.typer_iframe_height_cache_path == SRC_DIR / 'typer_cache.json'

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
    if (CLICK_EXAMPLES / 'cache.json').exists():
        os.remove(CLICK_EXAMPLES / 'cache.json')

    os.chdir(CLICK_EXAMPLES / name)

    app = Sphinx(
        ex_dir,
        CLICK_EXAMPLES,
        bld_dir / builder,
        bld_dir / 'doctrees',
        buildername=builder
    )

    assert app.config.typer_iframe_height_padding == 40
    assert app.config.typer_iframe_height_cache_path == CLICK_EXAMPLES / 'cache.json'

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
    ret = subprocess.run(
        [
            'poetry',
            'run',
            'python',
            CLICK_EXAMPLES / name / f'{name}.py',
            *subcommands,
            '--help'
        ],
        capture_output=True
    )
    return ret.stdout.decode() or ret.stderr.decode()


def check_html(html, help_txt, iframe_number=0, threshold=0.85):
    soup = bs(html, 'html.parser')
    iframe = soup.find_all('iframe')[iframe_number]
    assert iframe is not None
    iframe_src = bs(iframe.attrs['srcdoc'], 'html.parser')
    assert iframe_src is not None
    code = iframe_src.find('code')
    assert code is not None
    assert similarity(code.text, help_txt) > threshold

def check_svg(html, help_txt, svg_number=0, threshold=0.75):
    soup = bs(html, 'html.parser')
    svg = soup.find_all('svg')[svg_number]
    assert svg is not None
    assert similarity(svg.text.strip(), help_txt) > threshold


def check_text(html, help_txt, txt_number=0, threshold=0.95):
    soup = bs(html, 'html.parser')
    txt = soup.find_all('pre')[txt_number]
    assert txt is not None
    assert similarity(txt.text.strip(), help_txt) > threshold


def test_click_ex_validation():
    clear_callbacks()

    bld_dir, html = build_click_example('validation', 'html')
    assert (CLICK_EXAMPLES / 'cache.json').is_file()

    help_txt = get_click_ex_help('validation')

    check_html(html, help_txt)

    assert check_callback('typer_render_html')
    assert check_callback('typer_get_iframe_height')
    assert check_callback('typer_get_web_driver')

    check_svg(html, help_txt)
    check_text(html, help_txt)

    if bld_dir.exists():
        shutil.rmtree(bld_dir.parent)


def test_click_ex_termui():
    """
    tests :make-sections: and :show-nested: options
    """
    clear_callbacks()

    bld_dir, html = build_click_example('termui', 'html')

    help_txt = get_click_ex_help('termui')
    clear_help = get_click_ex_help('termui', 'clear')
    colordemo_help = get_click_ex_help('termui', 'colordemo')
    edit_help = get_click_ex_help('termui', 'edit')
    locate_help = get_click_ex_help('termui', 'locate')
    menu_help = get_click_ex_help('termui', 'menu')
    open_help = get_click_ex_help('termui', 'open')
    pager_help = get_click_ex_help('termui', 'pager')
    pause_help = get_click_ex_help('termui', 'pause')
    progress_help = get_click_ex_help('termui', 'progress')

    # verifies :show-nested:
    check_html(html, help_txt)
    check_html(html, clear_help, 1)
    check_html(html, colordemo_help, 2)
    check_html(html, edit_help, 3)
    check_html(html, locate_help, 4)
    check_html(html, menu_help, 5)
    check_html(html, open_help, 6)
    check_html(html, pager_help, 7)
    check_html(html, pause_help, 8)
    check_html(html, progress_help, 9)
    check_html(html, menu_help, 10)

    # verify :make-sections:
    soup = bs(html, 'html.parser')
    assert soup.find('section').find('h1').text.startswith('termui')
    assert soup.find_all('section')[1].find('h2').text.startswith('clear')
    assert soup.find_all('section')[2].find('h2').text.startswith('colordemo')
    assert soup.find_all('section')[3].find('h2').text.startswith('edit')
    assert soup.find_all('section')[4].find('h2').text.startswith('locate')
    assert soup.find_all('section')[5].find('h2').text.startswith('menu')
    assert soup.find_all('section')[6].find('h2').text.startswith('open')
    assert soup.find_all('section')[7].find('h2').text.startswith('pager')
    assert soup.find_all('section')[8].find('h2').text.startswith('pause')
    assert soup.find_all('section')[9].find('h2').text.startswith('progress')

    assert soup.find_all('section')[10].find('h1').text.startswith('termui menu')

    # verify correct name of subcommand
    assert 'Usage: termui menu [OPTIONS]' in bs(
        soup.find_all('iframe')[10].attrs['srcdoc'],
        'html.parser'
    ).find('code').text

    if bld_dir.exists():
        shutil.rmtree(bld_dir.parent)


def test_click_ex_repo():
    """
    tests :make-sections: and :show-nested: options
    """
    clear_callbacks()

    bld_dir, html = build_click_example('repo', 'html')

    help_txt = get_click_ex_help('repo')
    clone_help = get_click_ex_help('repo', 'clone')
    commit_help = get_click_ex_help('repo', 'commit')
    copy_help = get_click_ex_help('repo', 'copy')
    delete_help = get_click_ex_help('repo', 'delete')
    setuser_help = get_click_ex_help('repo', 'setuser')

    # verifies :show-nested:
    check_html(html, help_txt)
    check_html(html, clone_help, 1)
    check_html(html, commit_help, 2)
    check_html(html, copy_help, 3)
    check_html(html, delete_help, 4)
    check_html(html, setuser_help, 5)

    # verify :make-sections:
    soup = bs(html, 'html.parser')
    assert len(soup.find_all('section')) == 0, 'Should not have rendered any sections'

    if bld_dir.exists():
        shutil.rmtree(bld_dir.parent)


def test_click_ex_naval():
    """
    tests :make-sections: and :show-nested: options for multi level hierarchies
    """
    clear_callbacks()

    bld_dir, html = build_click_example('naval', 'html')

    help_txt = get_click_ex_help('naval')
    mine_help = get_click_ex_help('naval', 'mine')
    mine_remove_help = get_click_ex_help('naval', 'mine', 'remove')
    mine_set_help = get_click_ex_help('naval', 'mine', 'set')
    ship_help = get_click_ex_help('naval', 'ship')
    ship_move_help = get_click_ex_help('naval', 'ship', 'move')
    ship_new_help = get_click_ex_help('naval', 'ship', 'new')
    ship_shoot_help = get_click_ex_help('naval', 'ship', 'shoot')

    # verifies :show-nested:
    check_svg(html, help_txt)
    check_svg(html, mine_help, 1)
    check_svg(html, mine_remove_help, 2, threshold=0.65)
    check_svg(html, mine_set_help, 3, threshold=0.62)
    check_svg(html, ship_help, 4)
    check_svg(html, ship_move_help, 5, threshold=0.56)
    check_svg(html, ship_new_help, 6)
    check_svg(html, ship_shoot_help, 7, threshold=0.62)


    check_svg(html, ship_new_help, 8)

    # verify :make-sections:
    soup = bs(html, 'html.parser')
    assert len(soup.find_all('section')) == 9, 'Should have rendered 8 sections'

    soup = bs(html, 'html.parser')
    assert soup.find('section').find('h1').text.startswith('naval')
    assert soup.find_all('section')[1].find('h2').text.startswith('mine')
    assert soup.find_all('section')[2].find('h3').text.startswith('remove')
    assert soup.find_all('section')[3].find('h3').text.startswith('set')
    assert soup.find_all('section')[4].find('h2').text.startswith('ship')
    assert soup.find_all('section')[5].find('h3').text.startswith('move')
    assert soup.find_all('section')[6].find('h3').text.startswith('new')
    assert soup.find_all('section')[7].find('h3').text.startswith('shoot')

    assert soup.find_all('section')[8].find('h1').text.startswith('naval ship new')

    if bld_dir.exists():
        shutil.rmtree(bld_dir.parent)


def test_click_ex_inout():
    """
    tests :make-sections: and :show-nested: options for multi level hierarchies
    """
    clear_callbacks()

    bld_dir, html = build_click_example('inout', 'html')

    help_txt = get_click_ex_help('inout')
    # verifies :show-nested:
    check_html(html, help_txt)

    if bld_dir.exists():
        shutil.rmtree(bld_dir.parent)


@pytest.mark.skipif(TYPER_VERISON >= (0, 11, 0), reason='upstream typer bug?')
def test_click_ex_complex():
    """
    tests :make-sections: and :show-nested: options for multi level hierarchies
    """
    clear_callbacks()

    bld_dir, html = build_click_example('complex', 'html')

    check_text(html, """ Usage: complex [OPTIONS] COMMAND [ARGS]...                      
                                                                 
 A complex command line interface.                               
                                                                 
╭─ Options ─────────────────────────────────────────────────────╮
│ --home             DIRECTORY  Changes the folder to operate   │
│                               on.                             │
│ --verbose  -v                 Enables verbose mode.           │
│ --help                        Show this message and exit.     │
╰───────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────╮
│ init             Initializes a repo.                          │
│ status           Shows file changes.                          │
╰───────────────────────────────────────────────────────────────╯""")
    
    check_text(html, """ Usage: complex init [OPTIONS] [PATH]                            
                                                                 
 Initializes a repository.                                       
                                                                 
╭─ Arguments ───────────────────────────────────────────────────╮
│   path      [PATH]                                            │
╰───────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                   │
╰───────────────────────────────────────────────────────────────╯""", 1)
    check_text(html, """ Usage: complex status [OPTIONS]                                 
                                                                 
 Shows file changes in the current working directory.            
                                                                 
╭─ Options ─────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                   │
╰───────────────────────────────────────────────────────────────╯""", 2)

    soup = bs(html, 'html.parser')
    assert soup.find('section').find('h1').text.startswith('complex')

    for idx, cmd in enumerate(['init', 'status']):
        assert soup.find_all('section')[idx+1].find('h2').text.startswith(cmd)

    if bld_dir.exists():
        shutil.rmtree(bld_dir.parent)


def test_click_ex_completion():
    clear_callbacks()

    bld_dir, html = build_click_example('completion', 'html')

    subcommands = ['group', 'group select-user', 'ls', 'show-env']
    helps = [
        get_click_ex_help('completion'),
        *[get_click_ex_help('completion', *cmd.split()) for cmd in subcommands]
    ]

    for idx, help in enumerate(helps):
        check_text(html, help, idx, threshold=0.82)

    if bld_dir.exists():
        shutil.rmtree(bld_dir.parent)

def test_click_ex_aliases():
    clear_callbacks()

    bld_dir, html = build_click_example('aliases', 'html')

    subcommands = ['alias', 'clone', 'commit', 'pull', 'push', 'status']
    helps = [
        get_click_ex_help('aliases'),
        *[get_click_ex_help('aliases', *cmd.split()) for cmd in subcommands]
    ]

    for idx, help in enumerate(helps):
        check_text(html, help, idx, threshold=0.82)

    # if bld_dir.exists():
    #     shutil.rmtree(bld_dir.parent)


def test_click_ex_imagepipe():
    """
    tests a chained command
    """
    clear_callbacks()

    bld_dir, html = build_click_example('imagepipe', 'html')

    subcommands = [
        'blur', 'crop', 'display', 'emboss', 'open', 'paste',
        'resize', 'save', 'sharpen', 'smoothen', 'transpose'
    ]
    helps = [
        get_click_ex_help('imagepipe'),
        *[get_click_ex_help('imagepipe', cmd) for cmd in subcommands]
    ]

    for idx, help in enumerate(helps):
        check_text(html, help, idx, threshold=0.87)

    check_svg(html, helps[-3], threshold=0.7)

    soup = bs(html, 'html.parser')
    assert len(soup.find_all('section')) == 13, 'Should have rendered 13 sections'

    assert soup.find('section').find('h1').text.startswith('imagepipe')

    for idx, cmd in enumerate(subcommands):
        assert soup.find_all('section')[idx+1].find('h2').text.startswith(cmd)

    assert soup.find_all('section')[len(subcommands)+1].find('h1').text.startswith('imagepipe sharpen')

    # if bld_dir.exists():
    #     shutil.rmtree(bld_dir.parent)


def test_click_text_build_works():

    bld_dir, text = build_click_example('validation', 'text')
    help_txt = get_click_ex_help('validation')
    assert similarity(text, help_txt) > 0.95
    assert text.count('Usage:') == 3, 'Should have rendered the help 3 times as text'
    if bld_dir.exists():
        shutil.rmtree(bld_dir.parent)


def test_click_latex_build_works():
    """
    also tests the convert-png option and typer_svg2pdf and typer_convert_png callbacks.
    """

    bld_dir, latex = build_click_example('validation', 'latex')
    help_txt = get_click_ex_help('validation')

    assert check_callback('typer_svg2pdf')
    assert check_callback('typer_convert_png')

    # make sure the expected text rendered at least once
    assert latex.count('Usage: validation [OPTIONS]') == 1

    # get all pdf files from the build directory
    pdf = bld_dir / 'validation_2a8082c3.pdf'
    
    assert (bld_dir / 'validation_2a8082c3.svg').is_file()

    assert len(list(bld_dir.glob('**/*.pdf'))) == 1, 'Should have rendered the help 1 time as pdf'
    assert pdf.name.split('.')[0] in latex
    pdf_txt = pdf_text(pdf)[0]
    assert similarity(pdf_txt, help_txt) > 0.95

    assert len(list(bld_dir.glob('**/*.png'))) == 1, 'Should have rendered the help 1 time as png'
    html_png = bld_dir / 'validation_4697b61f.png'
    assert img_similarity(CLICK_EXAMPLES / 'validation' / 'html.png', html_png) < 9000

    if bld_dir.exists():
        shutil.rmtree(bld_dir.parent)


def test_enums():
    from sphinxcontrib.typer import RenderTarget, RenderTheme
    for target in RenderTarget:
        assert target.value == str(target)
    for theme in RenderTheme:
        assert theme.value == str(theme)

