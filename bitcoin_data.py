# IMPORTS
from bs4 import BeautifulSoup
import requests
import time
from selenium import webdriver 
from selenium.webdriver.common.by import By
from collections import Counter
from selenium.common.exceptions import NoSuchElementException
import random
from selenium.webdriver.chrome.options import Options

# GLOBAL VARIABLE OPTIONS FOR CHROMEDRIVER
options = Options()
options.add_argument("--headless")

# USER AGENTS FOR REQUESTS -> TO AVOID BEING DETECTED AS A BOT
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15']


# --------------------------------------
#GEOGRAPHICAL DIVERSITY INDEX
# --------------------------------------
def btc_geo_index():
    """Return a list of the number of nodes in each country."""

    btc_node_list = []

    # Loop through the pages and get the number of nodes in each country
    for i in range(1, 7):
        nodes_request = requests.get('https://bitnodes.io/nodes/all/countries/1d/?page='+str(i), headers={"User-Agent":random.choice(user_agents)})
        time.sleep(10)

        # Select the table with the data
        soup = BeautifulSoup(nodes_request.content, 'html.parser')
        desired_table = soup.select_one('table.table.table-striped.table-hover.table-condensed')
        data_elements = desired_table.select('tr:not(.text-center) td:nth-of-type(3)')

        # Get the number of nodes in each country
        for td in data_elements:
            btc_node_list.append(int(td.get_text(strip=True).split()[0])) # Split the text to get the number of nodes

    return btc_node_list


# --------------------------------------
# OWNER CONTROL
# --------------------------------------
def btc_owner_control():
    """Return a list of the amount of pre-mined BTC and its current supply."""

    btc_supply_list = [700000] # Pre-mined BTC by the founders-> Source: Sai, A. R., Buckley, J., Fitzgerald, B., & Le Gear, A. (2021). Taxonomy of centralization in public blockchain systems: A systematic literature review. Information Processing & Management, 58(4), 102584.

    btc_current_supply_response = requests.get('https://explorer.btc.com/de/btc', headers={"User-Agent":random.choice(user_agents)}) # Check if the first source is available
    if btc_current_supply_response.status_code == 200:
        time.sleep(10) # Let the page load

        # Get the current supply of BTC
        soup = BeautifulSoup(btc_current_supply_response.content, 'html.parser')
        element = soup.find_all('span', class_ = 'Info_value__2AXVi home_item-value__328tl')
        elements_text = element[1].get_text(strip=True).replace(",","").replace(" BTC", "") # Clean the data
        btc_supply_list.append(float(elements_text))

        return btc_supply_list
    
    else: # If the first request fails, try another source

        driver = webdriver.Chrome(options=options)
        driver.get("https://coinmarketcap.com/currencies/bitcoin/")
        time.sleep(10)

        supply_element = driver.find_element(By.XPATH, '//*[@id="section-coin-stats"]/div/dl/div[4]/div[1]/dd') # Find the relevant section

        # Scenario planning as sometimes the website displays the supply in millions and sometimes in full numbers
        if "M" in supply_element.text:
            btc_supply_list.append(float(supply_element.text.replace(",", "").replace(" BTC", "").replace("M", ""))*1000000)

        else:
            btc_supply_list.append(float(supply_element.text.replace(",", "").replace(" BTC", "")))

        driver.quit()

        return btc_supply_list


# --------------------------------------
# IMPROVEMENT PROTOCOL
# --------------------------------------
def btc_improvement_protocol():
    """Return a list of the amount of BIPs per author."""

    btc_ip_list = []

    driver = webdriver.Chrome(options=options)
    driver.get('https://github.com/bitcoin/bips')
    time.sleep(10)

    # Find the relevant table that stores the IP data
    tables = driver.find_elements(By.CSS_SELECTOR, 'table') 
    table_wanted = tables[1]

    # Find the authors of the BIPs
    ip_authors = table_wanted.find_elements(By.CSS_SELECTOR, 'table td:nth-child(4)')
    ip_author_name_list = []
    for author in ip_authors:
        ip_author_name_list.append(author.text)

    individual_names = [name.strip() for names in ip_author_name_list for name in names.split(',')] # Split the names if multiple authors have contributed to a BIP

    name_counts = Counter(individual_names) # Count the number of BIPs per author
    btc_ip_list = list(name_counts.values())

    driver.quit()

    return btc_ip_list


# --------------------------------------
# REFERENCE-CLIENT CONTRIBUTION
# --------------------------------------
def btc_reference_client_concentration():
    """Return a list of the number of commits to the BTC reference client per contributor."""

    btc_commits_list = []

    while not btc_commits_list:  # Keep retrying until the list is not empty, as the website may not load properly
        try:

            driver = webdriver.Chrome(options=options)
            driver.get('https://github.com/bitcoin/bitcoin/graphs/contributors')
            time.sleep(15)

            # Find all the contributors to the Cardano Foundation's developer portal
            contributors = driver.find_elements(By.CSS_SELECTOR, 'a.Link--secondary.text-normal')

            for contributor in contributors: 
                btc_commits_list.append(int(contributor.text.replace(",","").replace(" commits", "").replace(" commit", ""))) # Clean the data

            driver.quit()

            if btc_commits_list == []: # If the the page did not load properly, retry
                print("Error: Bitcoin's Commit Page did not load properly. Retrying...")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    return btc_commits_list


# --------------------------------------
# DECISION MAKING
# --------------------------------------
def btc_decision_making():
    """Return a list of the current hashrate per mining pool."""

    btc_hashrate_list = []

    response = requests.get('https://explorer.btc.com/de', headers={"User-Agent":random.choice(user_agents)}) # Check if the first source is available
    if response.status_code == 200:
        driver = webdriver.Chrome(options=options)
        driver.get('https://explorer.btc.com/de')
        time.sleep(10)

        cookies_button = driver.find_element(By.CSS_SELECTOR, 'span.CookiePolicy_close__15vD9') # Click the cookies button to enable scraping
        cookies_button.click()

        # Find the relevant section
        relevant_section = driver.find_element(By.CSS_SELECTOR, 'div.ant-col.ant-col-xs-24.ant-col-lg-12')
        hashrate_elements = relevant_section.find_elements(By.CSS_SELECTOR, 'span.undefined.home_hash-rate-text__1HjQg')

        # Get the hashrate of each mining pool
        for e in hashrate_elements:
            btc_hashrate_list.append(float(e.text))

        driver.quit()

        return btc_hashrate_list
    
    else: # If the first source is not available, try another source

        driver = webdriver.Chrome(options=options)
        driver.get('https://hashrateindex.com/hashrate/pools')
        time.sleep(10)

        # Find the relvant table column
        hastrate_elements = driver.find_elements(By.CSS_SELECTOR, 'td:nth-child(4)')

        # Get the hashrate of each mining pool
        for e in hastrate_elements:
            btc_hashrate_list.append(float(e.text.replace(' EH/s', '')))

        driver.quit()

        return btc_hashrate_list


# --------------------------------------
#HOSTING CONCENTRATION
# --------------------------------------
def btc_hosting_concentration():
    """Return a list of the number of nodes per hosting organization."""

    btc_hosting_list = []

    driver = webdriver.Chrome(options=options)
    driver.get('https://btc.cryptoid.info/btc/#!network')
    time.sleep(5)

    # Click the relevant tab
    relevant_tab = driver.find_element(By.ID, 'network-org-link')
    relevant_tab.click()
    time.sleep(5)

    # Get the table with the hosting data
    hosting_elements = driver.find_element(By.XPATH, '//*[@id="network-orgs"]')
    table_html = hosting_elements.get_attribute('outerHTML') # Get the HTML content of the table
    soup = BeautifulSoup(table_html, 'html.parser')

    # Select the relevant column
    column_index = 1
    rows = soup.find_all('tr')

    for row in rows:
        # Find all cells in the row
        cells = row.find_all('td')
        # Check if the column index is within the range of the cells
        if column_index < len(cells):
            btc_hosting_list.append(int(cells[column_index].text))

    driver.quit()

    return btc_hosting_list


# --------------------------------------
# EXCHANGE CONCENTRATION
# --------------------------------------
def btc_exchange_concentration():
    """Return a list of the volume of BTC traded on each exchange."""

    btc_exchange_list = []

    response = requests.get('https://coinranking.com/coin/bitcoin-btc/exchanges', headers={"User-Agent":random.choice(user_agents)}) # Check if the first source is available
    if response.status_code == 200:
        driver = webdriver.Chrome(options=options)
        driver.get('https://coinranking.com/coin/bitcoin-btc/exchanges')
        time.sleep(5)

        # Click the cookies button
        cookies_button = driver.find_element(By.CSS_SELECTOR, 'button.fc-button.fc-cta-consent.fc-primary-button')
        cookies_button.click()
        time.sleep(1)

        # Get the volume of BTC traded on each exchange per page
        while True:
            btc_exchange_elements = driver.find_elements(By.CSS_SELECTOR, 'td:nth-child(3)')

            for e in btc_exchange_elements:
                
                # Clean the data
                if " billion" in e.text:
                    btc_exchange_list.append(float(e.text.replace(" billion", "").replace("$ ", "").replace(",", "")) * 1000000000)
                elif " million" in e.text:
                    btc_exchange_list.append(float(e.text.replace(" million", "").replace("$ ", "").replace(",", "")) * 1000000)
                else: 
                    btc_exchange_list.append(float(e.text.replace("$ ", "").replace(",", "")))

            # Attempt to click the next page button
            try:
                next_page_button = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[3]/section/section/div[3]/a/img')
                driver.execute_script("arguments[0].scrollIntoView();", next_page_button)

                # Exit the loop if the next page button is disabled -> last page
                if next_page_button.find_element(By.XPATH, '..').get_attribute('class') == 'active-link pagination__button pagination__button--disabled':
                    break

                next_page_button.click()
                time.sleep(2)

            except NoSuchElementException:
                break  # Exit the loop if there is no next page button (last page)

        driver.quit()

        return btc_exchange_list
    
    else: # If the first source is not available, try another source

        driver = webdriver.Chrome(options=options)
        driver.get('https://cryptorank.io/price/bitcoin/exchanges')
        time.sleep(10)

        while True:

            # Find the relevant elements
            relevant_table = driver.find_element(By.CSS_SELECTOR, '#root-container > section > div.sc-be4b7d84-0.sc-e739bd4e-0.lfEaaA.bxDZvl > div > div.sc-7145b3a-0.kcNxkD > table')
            time.sleep(1)
            exchange_elements = relevant_table.find_elements(By.CSS_SELECTOR, 'td:nth-child(8)')

            # Clean the data
            for e in exchange_elements:
                if "N/A" in e.text:
                    pass
                elif "B" in e.text.split()[1]:
                    btc_exchange_list.append(float(e.text.split()[1].replace("B", "").replace("$ ", "").replace(",", "")) * 1000000000)
                elif "M" in e.text.split()[1]:
                    btc_exchange_list.append(float(e.text.split()[1].replace("M", "").replace("$ ", "").replace(",", "")) * 1000000)
                elif "K" in e.text.split()[1]:
                    btc_exchange_list.append(float(e.text.split()[1].replace("K", "").replace("$ ", "").replace(",", "")) * 1000)
                else: 
                    btc_exchange_list.append(float(e.text.split()[1].replace("$ ", "").replace(",", "")))

            # Locate the next page button
            next_page = relevant_table.find_element(By.XPATH, '//*[@id="root-container"]/section/div[1]/div/div[3]/div[1]/button[9]')
            time.sleep(1)

            # Exit the loop if the next page button is disabled -> last page
            if next_page.get_attribute('disabled'):
                break

            # Attempt to click the next page button
            else:
                try:
                    next_page.click()
                    time.sleep(3)

                except NoSuchElementException:
                    break

        driver.quit()

        return btc_exchange_list


