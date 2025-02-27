"""Simple API to access Billboard charts."""


import requests
from bs4 import BeautifulSoup
import re
import os

from playx.playlist.playlistbase import (
    PlaylistBase, SongMetadataBase
)

from playx.logger import (
    Logger
)

# Setup logger
logger = Logger('Billboard')


"""
__author__ = Deepjyoti Barman
__github__ = github.com/deepjyoti30

"""


class Song(SongMetadataBase):
    """Class to store song details."""

    def __init__(self, title='', artist='', rank=0):
        super().__init__()
        self.title = title
        self.artist = artist
        self.rank = 0
        self._create_search_querry()
        self._remove_duplicates()

    def _create_search_querry(self):
        """
        Create a search querry using the title and the artist name.
        """
        self.search_querry = self.title + ' ' + self.artist


class BillboardIE:
    """Class to store billboard charts."""

    def __init__(self, URL):
        """Initiate the basic stuff."""
        self.baseurl = "https://www.billboard.com/charts/"
        self.URL = self.baseurl + URL
        self.soup = self.get_soup()
        self.chart = []
        self.chart_name = ""
        self.get_name_of_chart()
        self.get_chart()
        self.replace_symbols()

    def get_soup(self):
        """Return the soup for the response."""
        response = requests.get(self.URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    def replace_symbols(self):
        """Replace symbols like &amp with &"""
        for i in self.chart:
            i.title = re.sub(r'&amp', '&', i.title)
            i.artist = re.sub(r'&amp', '&', i.artist)

    def get_name_of_chart(self):
        """Get the name of the chart from the webpage."""
        name = self.soup.findAll('h1',
                                attrs={'class': 'charts-hero__chart-name'})
        name = re.sub(
                    r'>|<',
                    '',
                    re.findall(
                        r'>.*<',
                        re.findall(r'<span.*/span>', str(name[0]))[0]
                        )[0]
                    )
        logger.debug(name)
        self.chart_name = name

    def get_chart(self):
        """New method to extract billboard chart data."""
        chart_contents = self.soup.findAll('li',
                                    attrs={'class': 'chart-list__element'})

        for chart_element in chart_contents:
            rank = re.sub(
                        r'>|<',
                        '',
                        re.findall(
                                r'>.*<',
                                str(chart_element.findAll(
                                        'span',
                                        attrs={'class': 'chart-element__rank__number'})[0])
                            )[0]
                    )
            track = re.sub(
                        r'>|<',
                        '',
                        re.findall(
                                r'>.*<',
                                str(chart_element.findAll(
                                        'span',
                                        attrs={'class': 'chart-element__information__song'})[0])
                            )[0]
                    )
            artist = re.sub(
                        r'>|<',
                        '',
                        re.findall(
                                r'>.*<',
                                str(chart_element.findAll(
                                        'span',
                                        attrs={'class': 'chart-element__information__artist'})[0])
                            )[0]
                    )
            self.chart.append(Song(track, artist, rank))


class BillboardPlaylist(PlaylistBase):
    """Class to store Billboards Charts data."""

    def __init__(self, playlist_name, pl_start=None, pl_end=None):
        """Init the chart name."""
        super().__init__(pl_start, pl_end)
        self.playlist_name = playlist_name
        self.list_content_tuple = []

    def extract_list_contents(self):
        """Extract the playlist data."""
        Chart = BillboardIE(self.playlist_name)
        self.list_content_tuple = Chart.chart
        self.strip_to_start_end()
        self.playlist_name = Chart.chart_name


def get_chart_names_online(url="https://www.billboard.com/charts"):
    try:
        response = requests.get(url, timeout=5)
    except requests.exceptions.ConnectionError:
        return []
    except requests.exceptions.ReadTimeout:
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=re.compile(r'.*/charts/.+'))
    chart_names = set()
    for link in links:
        href = link['href']
        name = href.split("/")[-1]
        if name:
            chart_names.add(name.lower())
    return chart_names


def get_chart_names(filename):
    """Get the chart names from the local chart file."""
    path = os.path.expanduser(filename)
    return [name.strip() for name in open(path).readlines()]


def dump_to_file(names):
    """Dump the billboard chart names to a local file."""
    path = '~/.playx/logs/billboard'
    path = os.path.expanduser(path)
    with open(path, 'w') as f:
        f.write('\n'.join(names).strip())


def get_data(URL, pl_start, pl_end):
    """Generic function. Should be called only when
    it is checked if the URL is a billboard chart.

    Returns a tuple containing the songs and name of
    the chart.
    """

    logger.info("Extracting Playlist Content")
    billboard_playlist = BillboardPlaylist(
                                            URL,
                                            pl_start,
                                            pl_end
                                        )
    billboard_playlist.extract_list_contents()

    return billboard_playlist.list_content_tuple, billboard_playlist.playlist_name


if __name__ == "__main__":
    # Chart = Billboard("youtube")
    # for i in Chart.chart:
    #     # print(i.title)
    #     print("{}: {} by {}".format(i.rank, i.title, i.artist))
    chart_names = get_chart_names_online()
    dump_to_file(chart_names)
    print(get_chart_names('~/.playx/logs/billboard'))
