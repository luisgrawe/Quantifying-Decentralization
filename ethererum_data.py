#IMPORTS
from bs4 import BeautifulSoup
import requests
import time
import re
import json
from collections import Counter
from selenium import webdriver 
from selenium.webdriver.common.by import By
import random
from selenium.common.exceptions import NoSuchElementException
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
# GEOGRAPHIC DIVERSITY
# --------------------------------------
def eth_geo_index():
    """Return a list of the number of nodes in each country."""

    node_response = requests.get("https://etherscan.io/nodetracker",headers={"User-Agent":random.choice(user_agents)}) # Check if the first source is available
    if node_response.status_code == 200:
        time.sleep(10)
        node_html = node_response.content

        # Create a pattern to search for node data in the HTML content
        pattern = re.compile(r'var data = (\[.*?\]);', re.DOTALL)

        # Search for the pattern in the HTML content
        match = pattern.search(node_html.decode('utf-8'))

        if match:
            # Extract the matched data
            data_str = match.group(1)

            # Convert the string representation of the data to a list of dictionaries
            data_list = json.loads(data_str)

            # Extract the "value" from each dictionary in the list
            eth_geo_list = [entry.get('value') for entry in data_list]

            print(f"Ethereum's geographical distribution of nodes: {eth_geo_list}")

            return eth_geo_list
        
        else: # If the first source is not available, try the second source

            driver = webdriver.Chrome(options=options)
            driver.get('https://www.ethernodes.org/countries')
            time.sleep(10)

            country_elements = driver.find_elements(By.CSS_SELECTOR, 'span.float-right.text-muted') # Find all the country elements

            eth_geo_list = [int(country.text.split()[0]) for country in country_elements] # Clean data and extract the number of nodes per country
            driver.quit()

            print(f"Ethereum's distribution of nodes per country: {eth_geo_list}")

            return eth_geo_list


# --------------------------------------
# OWNER CONTROL
# --------------------------------------
def eth_owner_control():
    """Return a list of the amount of pre-mined ETH and its current supply."""

    eth_owner_list = [12000000] # Pre-mined ETH by the founders -> Source: Sai, A. R., Buckley, J., Fitzgerald, B., & Le Gear, A. (2021). Taxonomy of centralization in public blockchain systems: A systematic literature review. Information Processing & Management, 58(4), 102584.

    current_supply_response = requests.get("https://etherscan.io/stat/supply", headers={"User-Agent":random.choice(user_agents)}) # Check if the first source is available
    if current_supply_response.status_code == 200:
        time.sleep(10)

        # Find the current supply data
        supply_html = current_supply_response.content
        soup = BeautifulSoup(supply_html, 'html.parser')
        span_element = soup.find('span', {'class': 'h4 mb-1'})

        # Check if the element exists before accessing its text content
        if span_element:
            number_text = span_element.text.strip().replace(',', '') # Clean the data
            number_value = float(number_text)

        eth_owner_list.append(number_value)

        print(f"Ethereum's pre-mined ETH and current supply: {eth_owner_list}")

        return eth_owner_list
    
    else: # If the first source is not available, try the second source

        driver = webdriver.Chrome(options=options)
        driver.get("https://coinmarketcap.com/currencies/ethereum/")
        time.sleep(10)

        # Find the relevant section
        supply_element = driver.find_element(By.XPATH, '//*[@id="section-coin-stats"]/div/dl/div[4]/div[1]/dd')

        # Scenario planning as sometimes the website displays the supply in millions and sometimes in full numbers
        if "M" in supply_element.text:
            eth_owner_list.append(float(supply_element.text.replace(",", "").replace(" ETH", "").replace("M", ""))*1000000)
        else:
            eth_owner_list.append(float(supply_element.text.replace(",", "").replace(" ETH", "")))

        driver.quit()

        print(f"Ethereum's pre-mined ETH and current supply: {eth_owner_list}")

        return eth_owner_list


# --------------------------------------
#IMPROVEMENT PROTOCOL
# --------------------------------------
def eth_improvement_protocol():
    """Return a list of the amount of EIPs per author."""

    ip_response = requests.get("https://eips.ethereum.org/all") # Autognereated website of Ethereum's EIP GitHub repository -> easer to scrape the data from
    time.sleep(10)
    ip_html = ip_response.content
    soup = BeautifulSoup(ip_html, "html.parser")

    authors_list = []

    # Find all author elements in the tables
    author_elements = soup.select('.eiptable .author')

    # Extract authors and split them by commas
    for author_element in author_elements:

        authors = [author.strip() for author in author_element.get_text(separator=',', strip=True).split(',')]
        authors_list.extend(authors)

    undesired_authors = ['et al.', 'Author', '>', ')'] # Undesired elements in the authors list

    for element in undesired_authors: # Clean the data by removing undesired elements

        while element in authors_list:
            authors_list.remove(element)

    # Create a new list with cleaned authors
    cleaned_authors_list = [author.replace('\xa0<', '').replace("\xa0(", "").strip() for author in authors_list
                        if '@' not in author and all(undesired not in author for undesired in undesired_authors)]

    eth_ip_list = list(Counter(cleaned_authors_list).values()) # Count the number of EIPs per author

    print(f"Ethereum's distribution of EIPs: {eth_ip_list}")

    return eth_ip_list


# --------------------------------------
# REFERENCE-CLIENT CONTRIBUTION
# --------------------------------------
def eth_reference_client_concentration():
    """Return a list of the number of commits to the ETH reference client per contributor."""

    eth_commits_list = []

    while not eth_commits_list:  # Keep retrying until the list is not empty, as the website sometimes fails to load

        try:
            driver = webdriver.Chrome(options=options)
            driver.get('https://github.com/ethereum/go-ethereum/graphs/contributors')
            time.sleep(15)

            # Find all the contributors and extract the number of commits per contributor
            contributors = driver.find_elements(By.CSS_SELECTOR, 'a.Link--secondary.text-normal')

            for contributor in contributors: 
                eth_commits_list.append(int(contributor.text.replace(",","").replace(" commits", "").replace(" commit", "")))

            driver.quit()

            if eth_commits_list == []: # If the website was not able to load the data, retry
                print("Error: Ethereum's Commit Page did not load properly. Retrying...")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    print(f"Ethereum's distribution of commits to the reference client: {eth_commits_list}")

    return eth_commits_list


# --------------------------------------
# DECISION MAKING
# --------------------------------------
def eth_decision_making():
    """Return a list of the amount of staked ETH per validator."""

    eth_stakes_list = []

    response = requests.get("https://explorer.btc.com/de/eth") # Check if the first source is available
    if response.status_code == 200:
        driver = webdriver.Chrome(options=options)
        driver.get('https://explorer.btc.com/de/eth')
        time.sleep(10)

        # Find the relevant section
        relevant_card = driver.find_element(By.CSS_SELECTOR, 'div.ant-col.home_responsive-right__3DCbr.ant-col-xs-24.ant-col-lg-12')
        stake_elements = relevant_card.find_elements(By.CSS_SELECTOR, 'td:nth-child(3)')

        # Extract the amount of staked ETH per validator
        for element in stake_elements:
            eth_stakes_list.append(float(element.text.replace(",", "")))

        driver.quit()

        print(f"Ethereum's distribution of staked ETH: {eth_stakes_list}")

        return eth_stakes_list
    
    else: # If the first source is not available, try the second source

        driver = webdriver.Chrome(options=options)
        driver.get("https://beaconcha.in/pools")
        time.sleep(10)

        # Find the relevant section
        pool_elements = driver.find_elements(By.CSS_SELECTOR, "td:nth-child(2)")

        # Skip the header and extract the amount of staked ETH per validator (multiply by 32 as that is the amount of ETH that must be staked per validator)
        for element in pool_elements[2:]:
            eth_stakes_list.append(int(element.text)*32)

        driver.quit()

        print(f"Ethereum's distribution of staked ETH: {eth_stakes_list}")

        return eth_stakes_list


# --------------------------------------
# HOSTING CONCENTRATION
# --------------------------------------
def eth_hosting_concentration():
    """Return a list of the number of nodes per hosting provider."""

    eth_hosting_list = []

    driver = webdriver.Chrome(options=options)
    driver.get('https://www.ethernodes.org/networkType/Hosting')
    time.sleep(10)

    # Find the pie chart data and extract the number of nodes per hosting provider
    pie_chart_data = driver.execute_script("return pieChartData;")

    for entry in pie_chart_data:
        eth_hosting_list.append(entry['y'])

    driver.quit()

    print(f"Ethereum's distribution of nodes per hosting provider: {eth_hosting_list}")

    return eth_hosting_list


# --------------------------------------
# EXCHANGE CONCENTRATION
# --------------------------------------
def eth_exchange_concentration():
    """Return a list of the traded amount of ETH per exchange."""

    eth_exchange_list = []

    response = requests.get("https://coinranking.com/coin/ethereum-eth/exchanges") # Check if the first source is available
    if response.status_code == 200:
        driver = webdriver.Chrome(options=options)
        driver.get('https://coinranking.com/coin/ethereum-eth/exchanges')
        time.sleep(10)

        # Click the cookies button
        cookies_button = driver.find_element(By.CSS_SELECTOR, 'button.fc-button.fc-cta-consent.fc-primary-button')
        cookies_button.click()
        time.sleep(1)

        # Get the volume of ETH traded on each exchange per page
        while True:
            eth_exchange_elements = driver.find_elements(By.CSS_SELECTOR, 'td:nth-child(3)')

            # Clean the data
            for e in eth_exchange_elements:

                if " billion" in e.text:
                    eth_exchange_list.append(float(e.text.replace(" billion", "").replace("$ ", "").replace(",", "")) * 1000000000)
                elif " million" in e.text:
                    eth_exchange_list.append(float(e.text.replace(" million", "").replace("$ ", "").replace(",", "")) * 1000000)
                else: 
                    eth_exchange_list.append(float(e.text.replace("$ ", "").replace(",", "")))

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

        print(f"Ethereum's distribution of trading volume per exchange: {eth_exchange_list}")

        return eth_exchange_list
    
    else: # If the first source is not available, try the second source

        driver = webdriver.Chrome(options=options)
        driver.get('https://cryptorank.io/price/ethereum/exchanges')
        time.sleep(10)

        while True:
            
            # Locate the relevant table and elements
            relevant_table = driver.find_element(By.CSS_SELECTOR, '#root-container > section > div.sc-be4b7d84-0.sc-e739bd4e-0.lfEaaA.bxDZvl > div > div.sc-7145b3a-0.kcNxkD > table')
            time.sleep(1)
            exchange_elements = relevant_table.find_elements(By.CSS_SELECTOR, 'td:nth-child(8)')

            # Clean the data
            for e in exchange_elements:
                if "N/A" in e.text:
                    pass
                elif "B" in e.text.split()[1]:
                    eth_exchange_list.append(float(e.text.split()[1].replace("B", "").replace("$ ", "").replace(",", "")) * 1000000000)
                elif "M" in e.text.split()[1]:
                    eth_exchange_list.append(float(e.text.split()[1].replace("M", "").replace("$ ", "").replace(",", "")) * 1000000)
                elif "K" in e.text.split()[1]:
                    eth_exchange_list.append(float(e.text.split()[1].replace("K", "").replace("$ ", "").replace(",", "")) * 1000)
                else: 
                    eth_exchange_list.append(float(e.text.split()[1].replace("$ ", "").replace(",", "")))

            # Attempt to click the next page button
            next_page = relevant_table.find_element(By.XPATH, '//*[@id="root-container"]/section/div[1]/div/div[3]/div[1]/button[9]')
            time.sleep(1)

            # Exit the loop if the next page button is disabled -> last page
            if next_page.get_attribute('disabled'):
                break

            else:
                try:
                    next_page.click()
                    time.sleep(3)

                except NoSuchElementException:
                    break

        driver.quit()

        print(f"Ethereum's distribution of trading volume per exchange: {eth_exchange_list}")

        return eth_exchange_list



