'''Scrap Youtube to get the related list from youtube'''

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from pathlib import Path
import json

from playx.playlist.playlistbase import (
    SongMetadataBase, PlaylistBase
)

from playx.logger import Logger

logger = Logger('YoutubeRelated')


class YoutubeMetadata(SongMetadataBase):
    """
    Class to hold contents of the playlist.
    """
    def __init__(self, title):
        super().__init__()
        self.title = title
        self._create_search_querry()

    def _create_search_querry(self):
        """
        Create a search querry.
        """
        self.search_querry = self.title


class YoutubeRelatedIE(PlaylistBase):
    """Youtube Related songs extractor."""

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.playlist_name = ''

    def _not_name(self, name):
        """
        Check the passed name to see if its actually a name of song.

        While extracting sometimes playlists are suggested in which
        the extraction algo extracts the time of the playlist instead
        of the name, so we need to remove it from the list of songs.
        """
        match = re.match(r'[0-9][0-9]?:[0-9][0-9]', name)
        if match is None:
            return False
        else:
            return True

    def extract_songs(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(chrome_options=chrome_options)

        driver.implicitly_wait(30)
        driver.get(self.url)
        songs = driver.find_elements_by_tag_name('ytd-compact-video-renderer')
        logger.debug(str(len(songs)))

        for i in songs:
            contents = i.text.split('\n')
            song_name = contents[0]
            logger.debug(song_name)
            if not self._not_name(song_name):
                self.list_content_tuple.append(YoutubeMetadata(song_name))

        driver.quit()


def get_data(url):
    logger.debug("Extracting related songs")
    logger.debug("Checking if file is present.")

    CACHE_PATH = Path("~/.playx/playlist").expanduser()
    FILE_NAME = "related_{}.json".format(url.split('\\=')[-1])
    FILE_PATH = CACHE_PATH.joinpath(Path(FILE_NAME))

    logger.info("Checking related playlist cache")
    # Check if FILE_NAME is present in CACHE_PATH
    for file in CACHE_PATH.iterdir():
        logger.debug("{}".format(file))
        if file == FILE_PATH:
            # Extract the data from FILE_PATH
            with open(FILE_PATH) as RSTREAM:
                data = json.load(RSTREAM)[1]["data"]
                data_ = []
                for title in data:
                    data_.append(YoutubeMetadata(title))
            return data_

    logger.info("Fetching data online")
    youtube_related = YoutubeRelatedIE(url)
    youtube_related.extract_songs()
    logger.debug("Saving the data...")
    logger.debug(str(len(youtube_related.list_content_tuple)))

    if len(youtube_related.list_content_tuple):
        save_data(url, youtube_related.list_content_tuple)

    return youtube_related.list_content_tuple


def save_data(url, data):
    """
    Save the data in a json file so that it can be accessed later.
    """
    CACHE_PATH = Path("~/.playx/playlist").expanduser()
    FILE_NAME = "related_{}.json".format(url.split('=')[-1])
    FILE_PATH = CACHE_PATH.joinpath(Path(FILE_NAME))

    FILE_PATH.touch()

    # Make the data a bit proper
    data_ = []
    for entity in data:
        data_.append(entity.title)

    with open(FILE_PATH, 'w') as WSTREAM:
        DATA = [{'URL': url}, {'data': data_}]
        json.dump(DATA, WSTREAM)


if __name__ == '__main__':
    # print(str(get_data('https://www.youtube.com/watch?v=xDbK1eZYVzg')))
    d = get_data('https://www.youtube.com/watch?v=xDbK1eZYVzg')
    for i in d:
        print(i.title)
