from rich.terminal_theme import TerminalTheme

red_sands = {
    'theme': TerminalTheme(
        (132,  42,  38),     # background
        (210, 193, 159),     # text
        [
            (210, 193, 159), # 
            (  0,   0,   0), # required
            ( 77, 218,  77), # option on short name
            (227, 189,  57), # Usage/metavar
            (210, 193, 159), #
            (  0,  18, 140), # option off
            ( 75, 214, 225), # option on/command names
            (210, 193, 159), #
        ]
    )
}
