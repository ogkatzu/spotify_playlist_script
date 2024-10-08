from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import urllib.parse
import spotify_v1

def read_credentials(file_path):
    credentials = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            credentials[key] = value
    return credentials

def login_to_facebook(driver, username, password):
    driver.get("https://mbasic.facebook.com/")
    email = driver.find_element(by="id", value="email")
    email.send_keys(username)
    pwd = driver.find_element(by="id", value="pass")
    pwd.send_keys(password)
    login_button = driver.find_element(by="xpath", value='/html/body/div[1]/div[1]/div[1]/div/div/div/div[2]/div/div[1]/form/div[2]/button')
    login_button.click()
    sleep(25)  # Wait for login to complete

def navigate_to_page(driver, url):
    driver.get(url)

def extract_spotify_links(driver):
    spotify_links = driver.find_elements(by="xpath", value="//a[contains(@href, 'open.spotify.com')]")
    return [link.get_attribute("href") for link in spotify_links if "open.spotify.com" in link.get_attribute("href")]

def click_next_button(driver):
    next_button = driver.find_element(by="xpath", value="//a[contains(@href, '/profile/timeline/stream/?cursor')]")
    next_button.click()

def extract_spotify_url(facebook_url):
    parsed_url = urllib.parse.urlparse(facebook_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    return query_params['u'][0] if 'u' in query_params else None

def save_links_to_file(links, filename):
    with open(filename, 'w') as file:
        for link in links:
            file.write(f"{link}\n")

def main():
    cred_file = 'cred.txt'
    credentials = read_credentials(cred_file)
    username = credentials.get('USERNAME')
    password = credentials.get('PASSWORD')

    driver = webdriver.Chrome()

    try:
        login_to_facebook(driver, username, password)

        target_url = "https://mbasic.facebook.com/profile.php?id=100090390200346&v=timeline&lst=634807305%3A100090390200346%3A1728324982&eav=Afb_zzDTwjEkM7PHJisDxpoK5W11IByib630Ag95Ba-bgrlNhDfFt0mQLsd-q7VRYxE&paipv=0"
        navigate_to_page(driver, target_url)

        spotify_urls = []
        for _ in range(30):  # iterate over <x> pages
            spotify_urls.extend(extract_spotify_links(driver))
            sleep(5)
            click_next_button(driver)

        clean_spotify_urls = [extract_spotify_url(url) for url in spotify_urls if extract_spotify_url(url)]
        save_links_to_file(clean_spotify_urls, 'spotify_links.txt')

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
    spotify_v1.main()
