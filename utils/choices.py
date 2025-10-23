#!/bin/env python
space=" "
dash="-"
number_dash=40

def individual_options():
    name_slide="Select an Option"
    quick_download_option ="Quick Download and Best Format Option"
    show_formats_list_option ="Show Formats List Option"
    thumbnails_download_option ="Thumbnails Download Option"
    list_playlist_formats_option ="Show Formats List (Playlist)"
    history_option ="View Download History Option"
    show_incomplete_downloads_option ="Show Incomplete Downloads Option"
    skip="Skip"

    length_ns = len(name_slide)
    length_qdo = len(quick_download_option)
    length_sflo = len(show_formats_list_option)
    length_tdo = len(thumbnails_download_option)
    length_lpfo = len(list_playlist_formats_option)
    length_ho = len(history_option)
    length_sido = len(show_incomplete_downloads_option)
    length_skip = len(skip)

    number_spaces_ns = 39 - length_ns
    number_spaces_qdo = 39 - length_qdo
    number_spaces_sflo = 39 - length_sflo
    number_spaces_tdo = 39 - length_tdo
    number_spaces_lpfo = 39 - length_lpfo
    number_spaces_ho = 39 - length_ho
    number_spaces_sido = 39 - length_sido
    number_spaces_skip = 39 - length_skip

    # Header Individual Options
    print(f"+---+{number_dash*dash}+")
    print(f"| \\ |{space}{name_slide}{number_spaces_ns*space}|")
    print(f"+---+{number_dash*dash}+")

    # Individual Options List
    options = [
        (quick_download_option, number_spaces_qdo),
        (show_formats_list_option, number_spaces_sflo),
        (thumbnails_download_option, number_spaces_tdo),
        (list_playlist_formats_option, number_spaces_lpfo),
        (history_option, number_spaces_ho),
        (show_incomplete_downloads_option, number_spaces_sido),
    ]

    # Print Option
    for number, (option, number_spaces) in enumerate(options, start=1):
        print(f"|{space}{number}{space}|{space}{option}{number_spaces*space}|")
    # Footer Individual Options List    
    print(f"+---+{number_dash*dash}+")
    print(f"|{space}0{space}|{space}{skip}{number_spaces_skip*space}|")
    print(f"+---+{number_dash*dash}+")

def other_options():

    name_slide ="Other Download Options"
    playlist_download_option ="Playlist download option"
    batch_file ="File containing URLs to download"
    go_back ="Return"

    length_ns = len(name_slide)
    length_pdo = len(playlist_download_option)
    length_bf = len(batch_file)
    length_gb = len(go_back)

    number_spaces_ns = 39 - length_ns
    number_spaces_pdo = 39 - length_pdo
    number_spaces_bf = 39 - length_bf
    number_spaces_gb = 39 - length_gb

    # Header other Options
    print (f"+---+{number_dash*dash}+")
    print (f"| \\ |{space}{name_slide}{number_spaces_ns*space}|")
    print (f"+---+{number_dash*dash}+")
    
    # Other Options List
    options = [
            (playlist_download_option,number_spaces_pdo),
            (batch_file,number_spaces_bf)
            ]
    # Print Option
    for number, (option, number_spaces) in enumerate(options, start =1):
                         print (f"|{space}{number}{space}|{space}{option}{number_spaces*space}|")
    # Footer Other Options

    print (f"+---+{number_dash*dash}+")
    print (f"|{space}R{space}|{space}{go_back}{number_spaces_gb*space}|")
    print (f"+---+{number_dash*dash}+")

def load_URLs_from_file():

    name_slide ="Load URLs from File"
    show_formats_list_option ="Show Formats List and Download Option"
    best_format_option ="Download Best Format"
    format_input_option ="Format Input Option"
    go_back ="Return"

    length_ns = len(name_slide)
    length_sflo = len(show_formats_list_option)
    length_bfo = len(best_format_option)
    length_fio = len(format_input_option)
    length_gb = len(go_back)

    number_spaces_ns = 39 - length_ns
    number_spaces_sflo = 39 - length_sflo
    number_spaces_bfo = 39 - length_bfo
    number_spaces_fio = 39 - length_fio
    number_spaces_gb = 39 - length_gb

    # Header Load URLs from File Options
    print (f"+---+{number_dash*dash}+")
    print (f"| \\ |{space}{name_slide}{number_spaces_ns*space}|")
    print (f"+---+{number_dash*dash}+")
    
    # Load URLs from File Options List
    options = [
            (show_formats_list_option,number_spaces_sflo),
            (best_format_option,number_spaces_bfo),
            (format_input_option,number_spaces_fio)
            ]
    # Print Option
    for number, (option, number_spaces) in enumerate(options, start =1):
                         print (f"|{space}{number}{space}|{space}{option}{number_spaces*space}|")
    # Footer Load URLs from File Options

    print (f"+---+{number_dash*dash}+")
    print (f"|{space}R{space}|{space}{go_back}{number_spaces_gb*space}|")
    print (f"+---+{number_dash*dash}+")

