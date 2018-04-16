from selenium import webdriver

def getTextFromURL(url):
    browser = webdriver.Chrome()
    browser.get(url)
    return browser.find_element_by_xpath('//pre[@class="_1YgOS"]').text

def getURLsFromPageURL(url, type):
    result = []
    browser = webdriver.Chrome()
    browser.get(url)
    songs = browser.find_elements_by_xpath('//a[@class="link-primary"]')
    for song in songs:
        songURL = song.get_attribute("href")
        songTitle = song.text + "_" + type
        result.append((songURL, songTitle))
    return result

def getAllURLs():
    urls = []
    nrPages = [13, 8, 3, 3, 1, 1]
    i = 0
    for artist in ("the_beatles_1916", "queen_590", "carole_king_10677"):
        # Chords
        pages = nrPages[i]
        for j in range(1, pages + 1):
            page_url = "https://www.ultimate-guitar.com/artist/" + artist \
                       + "?filter=chords&page=" + str(j)
            extra_urls = getURLsFromPageURL(page_url, "Chords")
            urls = urls + extra_urls
        i = i + 1
        # Tabs
        pages = nrPages[i]
        for j in range(1, pages + 1):
            page_url = "https://www.ultimate-guitar.com/artist/" + artist \
                       + "?filter=tabs&page=" + str(j)
            extra_urls = getURLsFromPageURL(page_url, "Tabs")
            urls = urls + extra_urls
        i = i + 1
    return urls

def make_valid(filename):
    valid_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    new_filename = ''.join(c for c in filename if c in valid_chars)
    return new_filename

def exportURLs(urls):
    index_file = open("E:\Data\Tabs\TabIndex.csv", "w", encoding="utf-8")
    for url in urls:
        title = make_valid(url[1])
        index_file.write(url[0] + ";" + title + ";" + "\n")
    index_file.close()

def writeTabs():
    with open("E:\Data\Tabs\TabIndex.csv", "r", encoding="utf-8") as index_file:
        content = index_file.readlines()
    write_file = open("E:\Data\Tabs\TabPathIndex.csv", "a", encoding="utf-8")
    tabs_path = "E:\Data\Tabs"

    nog = [285, 515, 661, 842, 901, 1030, 1032, 1035]
    for i in nog:
        line = content[i]
        cols = line[:-1 or None].split(';')
        if int(cols[2]) > 0:
            path = tabs_path + "\\" + cols[1] + ".txt"
            tab = getTextFromURL(cols[0])
            f = open(path, "w", encoding="utf-8")
            f.write(tab)
            f.close()
            write_file.write(line[:-1 or None] + ";" + path + "\n")
    write_file.close()

#urls = getAllURLs()
#exportURLs(urls)
#writeTabs()