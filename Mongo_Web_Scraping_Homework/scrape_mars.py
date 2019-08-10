# import dependencies
import time
import pandas as pd
from bs4 import BeautifulSoup
from splinter import Browser
import datetime as dt

def init_browser():
    executable_path = {"executable_path": "chromedriver.exe"}
    news_title, news_paragraph = mars_news(browser)

def scrape ():
    
    browser = init_browser()
    mars_data = {"news_title": news_title,
    "news_paragraph": news_paragraph,
    "featured_image": featured_image(browser),
    "hemispheres": hemispheres(browser),
    "weather": twitter_weather(browser),
    "facts": mars_facts(),
    "last_modified": dt.datetime.now()
    }

    browser.quit()
    return mars_data

def mars_news(browser):
    mars_news_url = "https://mars.nasa.gov/news/"
    browser.visit(mars_news_url)

    # Get list item
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=0.5)

    mars_html = browser.html
    mars_news_soup = BeautifulSoup(html, "html.parser")

    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        news_title = slide_elem.find("div", class_="content_title").get_text()
        news_p = slide_elem.find(
            "div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)

    # Find and click the full image button
    full_image_button = browser.find_by_id("full_image")
    full_image_button.click()

    # Find the more info button and click that
    browser.is_element_present_by_text("more info", wait_time=0.5)
    more_info_button = browser.find_link_by_partial_text("more info")
    more_info_button.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, "html.parser")

    # Find the relative image url
    img = img_soup.select_one("figure.lede a img")

    try:
        img_url_rel = img.get("src")

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f"https://www.jpl.nasa.gov{img_url_rel}"

    return img_url


def hemispheres(browser):

    # A way to break up long strings
    url = (
        "https://astrogeology.usgs.gov/search/"
        "results?q=hemisphere+enhanced&k1=target&v1=Mars"
    )

    browser.visit(url)

    # Click the link, find the sample anchor, return the href
    hemisphere_image_urls = []
    for i in range(4):

        # Find the elements on each loop to avoid a stale element exception
        browser.find_by_css("a.product-item h3")[i].click()

        hemisphere_data = scrape_hemisphere(browser.html)

        # Append hemisphere object to list
        hemisphere_image_urls.append(hemisphere_data)

        # Finally, we navigate backwards
        browser.back()

    return hemisphere_image_urls


def twitter_weather(browser):
    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)

    html = browser.html
    weather_soup = BeautifulSoup(html, "html.parser")

    # First, find a tweet with the data-name `Mars Weather`
    mars_tweet_find = {"class": "tweet", "data-name": "Mars Weather"}
    mars_weather_tweet = weather_soup.find("div", attrs=mars_tweet_find)

    # Next, search within the tweet for the p tag containing the tweet text
    mars_weather = mars_weather_tweet.find("p", "tweet-text").get_text()

    return mars_weather


def scrape_hemisphere(html_text):

    # Soupify the html text
    hemisphere_soup = BeautifulSoup(html_text, "html.parser")

    # Try to get href and text except if error.
    try:
        title_element = hemisphere_soup.find("h2", class_="title").get_text()
        sample_element = hemisphere_soup.find("a", text="Sample").get("href")

    except AttributeError:

        # Image error returns None for better front-end handling
        title_element = None
        sample_element = None

    hemisphere = {
        "title": title_element,
        "img_url": sample_element
    }

    return hemisphere


def mars_facts():
    try:
        df = pd.read_html("http://space-facts.com/mars/")[0]
    except BaseException:
        return None

    df.columns = ["description", "value"]
    df.set_index("description", inplace=True)

    # Add some bootstrap styling to <table>
    return df.to_html(classes="table table-striped")


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())
