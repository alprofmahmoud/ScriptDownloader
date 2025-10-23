#!/usr/bin/env python3
import os

space = " "
left_space = " "
dash = "-"
max_length = 0
dash_number = 39
lines = []
def read_locations_file():
    # Function read file
    lines = []  
    max_length = 0  
    
    try:
        with open("./lct.txt", "r", encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:  
                    lines.append(line)
                    if len(line) > max_length:
                        max_length = len(line)
        return lines, max_length 
    except FileNotFoundError:
        print("⚠️ File lct.txt not found, creating new one...")
        with open("./lct.txt", "w", encoding='utf-8') as file:
            pass
        return [], 0
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return [], 0

def select_output_location():
    global left_space, dash_number

    
    lines, max_length = read_locations_file()
    
    total_items = 2 + len(lines)
    left_space = " "

    # Variables
    slide_title = "Output in, Maximum 15 location"
    default_location ="Default location (downloads)"
    enter_new_location ="Enter New Location"

    # Length Variables
    length_st = len(slide_title)
    length_dl = len(default_location)
    length_enl = len(enter_new_location)


    # Spaces Number
    space_number_st = 38 - length_st
    space_number_dl = 38 - length_dl
    space_number_enl = 38 - length_enl
    
    # Header Select output Location
    if (total_items >= 10):
        dash_nr = 4
        number_sl = 2
    else:
        dash_nr = 3
        number_sl = 1

    print(f"+{dash_nr*dash}+{dash_number*dash}+")
    print(f"|{space}\\{number_sl*space}|{space}{slide_title}{space_number_st*space}|")
    print(f"+{dash_nr*dash}+{dash_number*dash}+")

    # Options List
    locations_ = [
            (default_location,space_number_dl),
            (enter_new_location,space_number_enl)
            ]
    
    # Print Locations
    # Than 10
    # Location from file ./lct.txt
    for number, (folder, space_number) in enumerate(locations_, start=1):
        extra_space = " " if (total_items >= 10 and number < 10) else ""
        print(f"|{space}{number}{extra_space}{left_space}|{space}{folder}{space_number*space}|")
    # Than 10
    # Locatins from file ./lct.txt
    for line_number, line in enumerate(lines, start=3):
        count_lct = len(line)
        space_number_lct = 38 - count_lct
        extra_space = " " if (total_items >= 10 and line_number < 10) else ""
        print(f"|{space}{line_number}{extra_space}{left_space}|{space}{line}{space_number_lct * space}|")

    # Rewrite the file
    if len(lines) >= 18:
        with open("./lct.txt", "w", encoding='utf-8') as file:
            pass

    # Footer Select output Location
    print(f"+{dash_nr*dash}+{dash_number*dash}+")

    try:
        print("Enter number location:")
        num_lct = int(input())
        location = None
        if num_lct == 1:
           print("Location: downloads")
           location = "downloads"
        elif num_lct == 2:
            print("Enter new location:")
            new_location = input()
            print(f"Location: {new_location}")
            location = new_location
             
            # Add the new location to the file
            with open("./lct.txt", "a", encoding='utf-8') as append_file:
                append_file.write(f"{new_location}\n")
        else:
            index = num_lct - 3  
            if 0 <= index < len(lines):
                location = lines[index]
                print(f"Selected location: {location}")
            else:
                print("Invalid location number!")
                return None        
        return location  # Return selected location

    except ValueError:
        print("Error! Please enter a valid integer number")
        return None
    except KeyboardInterrupt:
        print("🛑 Program Stopped")
        return None
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return None
