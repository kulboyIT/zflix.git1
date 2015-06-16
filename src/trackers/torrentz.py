#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
try:
    import bs4
except:
    print("BeautifulSoup4 is not installed.")
    exit()

class torrentz:
    def __init__(self):
        self.domain = 'https://www.torrentz.com'

        self.locations = {"h33t": {"url": "http://www.h33t.to",
                                   "dl": "h33t.to/get/"},
                          "demonoid": {"url": "www.demonoid.pw",
                                       "dl": "www.demonoid.pw/files/download/"},
                          "seedpeer.eu": {"url": "www.seedpeer.eu/",
                                          "dl": "/download/"},
                          "rarbg": {"url": "rarbg.com/torrent/",
                                    "dl": "rarbg.com/download.php?id="},
                          #"tpb": {"url": "http://thepiratebay.org",
                          #        "dl": "http://torrents.thepiratebay.org"},
                          "yourbittorrent": {"url": "yourbittorent.com/torrent/",
                                             "dl": "/down/*.torrent"},
                          "isohunt": {"url": "http://isohunt.to",
                                      "dl": "torrent.isohunt.to/download.php?id="},
                          "torrentfunk.com": {"url": "/tor/*.torrent",
                                              "dl": "www.torrentfunk.com/tor/*.torrent"},
                          "limetorrents.cc": {"url": "http://www.limetorrents.cc",
                                              "dl": "itorrents.org/torrent/"},
                           "torrents.net": {"url": "http://www.torrents.net",
                                            "dl": "torrents.net/down/*.torrent"},
                          "vertor": {"url": "http://www.vertor.com",
                                     "dl": "?mod=download."},
                          "monova": {"url": "www.monova.org/torrent/",
                                     "dl": "www.monova.org/download/torrent/"},
                          "torrentdl": {"url": "torrentdownloads.me/torrent/",
                                        "dl": "itorrents.org/torrent/"}
                          #"torlock": {"url": "www.torlock.com",
                          #            "dl": ".torrent"},
                          #"torrentproject": {"url": "torrentproject.se",
                          #                   "dl": "torrentproject.se/torrent/*.torrent"}
                          }

    def get_magnet_from_tracker(self, trackerPage):
        """
        Get a magnet link on a webpage

        ARGUMENT:
            trackerPage: A link to a tracker.

        RETURN VALUE:
            A magnet link.
        """
        soup = bs4.BeautifulSoup(trackerPage)
        urls = soup.find_all('a')

        i = 0
        res = False
        while res is False and i < len(urls):
            if 'magnet:' in urls[i].get('href'):
                print('Getting ' + urls[i].get('href'))
                res = urls[i].get('href')
            i += 1

        return res

    def get_specific_tracker(self, pageLink):
        """
        Get the a supported tracker from a torrentz page.

        ARGUMENT:
            pageLink: A torrentz download page.

        RETURN VALUE:
            The page of a supported tracker, and the name of the tracker.
        """
        page = requests.get(pageLink)
        page = page.text
        soup = bs4.BeautifulSoup(page)

        trackersUrls = soup.find('div', class_="download")
        # Get the div with the links first
        trackersUrls = trackersUrls.find_all('a')
        trackersUrls.pop(0)
        # Every trackers listed in the page

        # TODO USE SELF LOCATION 'URL'
        # TODO LOCATION IS NOW USELESS WITH MAGNET !!!!

        for tracker in map(lambda x: x.get('href'), trackersUrls):
            for location in self.locations:
                if location in tracker:
                    trackerPage = requests.get(tracker)
                    yield trackerPage.text, location
                    break # Trying another tracker if this one is not OK.


        print("Error: Torrent found in none of the locations")

    def get_magnet(self, pageLink):
        """
        Function returning the magnet link for the torrent.

        ARGUMENT:
            pageLink: The link of the page you want to get the torrent.

        RETURN VALUE:
            A magnet link.
        """
        downloadLocationTest = self.get_specific_tracker(self.domain + pageLink)
        magnet = False

        while magnet is False:
            trackerPage, trackerName = next(downloadLocationTest, (None, None))
            if trackerPage is not None:
                magnet = self.get_magnet_from_tracker(trackerPage)
            else:
                break

        return magnet

    def search_torrent(self, search):
        """
        Add to the dic "queryResult" with a refernce used for the key
        a list of returned torrent link with a specific search term.

        ARGUMENTS:
            search: The user searcher torrents.
            queryResult: A dict proxy where the result will be stocked.
        """
        torrentzPage = requests.get(self.domain + '/any?f=' + search)
        torrentzPage = torrentzPage.text
        soup = bs4.BeautifulSoup(torrentzPage)
        torrentLinks = soup.find('div', class_="results")
        torrentLinks = torrentLinks.find_all('dl')

        result = []
        for link in torrentLinks[:-1]:
            newEntry = {}

            mainCell = link.find("a")
            newEntry['title'] = mainCell.text
            newEntry['link'] = mainCell.get("href")

            try:
                newEntry['size'] = link.find("span", class_="s").text
            except AttributeError:
                newEntry['size'] = "Pending"

            # Don't need to be converted in an int.
            newEntry['seeds'] = link.find("span", class_="u"
                                          ).text.replace(',', '')
            newEntry['peers'] = link.find("span", class_="d"
                                          ).text.replace(',', '')

            newEntry['ref'] = self

            result.append(newEntry)

        return result
