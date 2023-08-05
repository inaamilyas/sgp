import requests
import bs4

def scraper(title):

    # text = "what is AI"
    url = 'https://google.com/search?q=' + title

    request_result = requests.get(url)

    # Creating soup from the fetched request
    soup = bs4.BeautifulSoup(request_result.text, "lxml")

    # all major headings of our search result,
    heading_object = soup.find_all('h3')

    # Links relative to each heading
    link_object = soup.find_all('h3')


    # Getting href of link
    rawlinks = []
    for rawlink in link_object:
        link = rawlink.previous_element.previous_element.previous_element.get(
            'href')
        rawlinks.append(link)

    # Extracting the main url
    link_object = []
    for rawlink in rawlinks:
        if rawlink:
            link = ''
            for ch in rawlink:
                if ch == '&':
                    break
                else:
                    link = link+ch
            link_object.append(link[7:])

    # Saving as list of list
    linksInfo = []
    for index in range(5):
        list = []
        list.append(index)
        list.append(heading_object[index].getText())
        list.append(link_object[index])

        linksInfo.append(list)

    return linksInfo
