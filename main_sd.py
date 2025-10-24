#!/bin/env python
from utils.choices import *
from utils.select_output_location import *
from single_downloader_mode_sd import SingleDownloader
from load_urls_from_file import LoadURLsFromFile

def main_other_options():
    other_options()
    print("Select an Option")
    print("Enter the Selection Number :")
    option_number =input()

    #If Condition Other Options
    if option_number == "1":
        print("Playlist download option")

    elif option_number == "2":
        print("Load URLs from File")
        main_load_URLs_from_file()

    elif option_number == "r":
        Main()
    else:
        print("No option")

def main_load_URLs_from_file():
    # Object from class LoadURLsFromFile
    ob_urls_from_file = LoadURLsFromFile()

    load_URLs_from_file()
    print("Select an Option")
    print("Enter the Selection Number :")
    option_number =input()

    # If Condition Load URLs from File
    if option_number == "1":
        print("Show Formats List and Download Option")
        ob_urls_from_file.show_formats_list_urls_from_file()
    elif option_number == "2":
        print("Download Best Format")
        ob_urls_from_file.downloader_from_file()
    elif option_number == "3":
        print("Format Input Option")
    elif option_number == "r":
        main_other_options()
    else:
        print("No option")

def Main():
    # Object from class SingleDownloader
    downloader = SingleDownloader()

    try:
        individual_options()
        print("Select an Option")
        print("Enter the Selection Number :")
        # Create Object
        option_number = input()
        
        if option_number == "1":
            print("Quick Download and Best Format Option")
            downloader.download_single_video()

        elif option_number == "2":
            print("Show Format Fist and Download Option")
            downloader.show_format_list()
            #downloader.download_single_video()

        elif option_number == "3":
            print("Thumbnails Download Option")
            print("your location: ",select_output_location())

        elif option_number == "4":
            print("Show Formats List (Playlist)")

        elif option_number == "5":
            print("View Download History Option")

        elif option_number == "6":
            print("Show Incomplete Downloads Option")

        elif option_number == "0":
            print("Skip Individual Selections")
            main_other_options()

        else:
            print("No option")
            
    except KeyboardInterrupt:
        print("\n🛑 Program Stopped")
        return     
    except Exception as e:
        print(f"❌ Unexpected Error Occurred: {e}")


if __name__ == "__main__":
    Main()
