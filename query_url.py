#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def display_query_url(query_url=None, total_url=None):
    if total_url is not None:
        total_url = str(total_url)
        len_total_url_content = len(total_url) + 2
    else:
        total_url = ""
        len_total_url_content = 0
    desc_width = 38
    line = "+" + "-"*len_total_url_content + "+" + "-"*desc_width + "+"
    answer1 = "Found in"
    answer0 = "Not found"
    length_answer1 = len(answer1)
    length_answer0 = len(answer0)
    len_total_url_content = len(str(total_url)) if total_url is not None else 0
    if query_url:
        id_content = f" ID: {query_url.get('id', 'N/A')}"
        lct_content = f"Location: {query_url.get('location', 'N/A')}"
        len_id_content = len(id_content)
        len_lct_content = len(lct_content)
        needed_spaces = desc_width - (len_total_url_content+len_id_content+len_lct_content+length_answer1)+2

        if total_url:
            print(line)
            print("|"+" "+total_url+" "+"|"+" "+answer1+id_content+" "+lct_content+" "*needed_spaces+"|")
            print(line)
        else:
            print(line)
            print("|"+answer1+"|"+id_content+"|"+lct_content+" "*needed_spaces+"|")
            print(line)

    else:
        needed_spaces = desc_width - length_answer0 - 1
        print(line)
        print("|" + " " + total_url + " "+"|" + " " + answer0 + " "*needed_spaces+"|")
        print(line)
