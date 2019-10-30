#!/usr/bin/env python3
"""It is an abstract module for searching songs"""

from playx.youtube import search_youtube
from playx.stringutils import (
    get_closest_match_ignorecase,
    fix_title
)
import random

def search(song, no_kw_in_search):
    """Search the song in youtube."""
    videos = search_youtube(song, no_kw_in_search)
    try:
        video = videos[0]
    except IndexError:
        return None
    return video


def search_with_exclude(song, songs_to_exclude):
    """Search the song in youtube."""
    videos = search_youtube(song, skip_kw=True)
    string_list = []
    for video in videos:
        fixed_title = fix_title(video.title)
        string_list.append(fixed_title)
    
    to_remove = get_closest_match_ignorecase(string_list,songs_to_exclude[0])
    index = string_list.index(to_remove)

    del string_list[index]
    del videos[index]

    print(index)
    return random.choice(videos)
