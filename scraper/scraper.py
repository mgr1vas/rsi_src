import sys
import time
import random
import requests
import csv # ADDED: PYTHON'S BUILT-IN CSV LIBRARY
from bs4 import BeautifulSoup

# FORCE THE TERMINAL TO SUPPORT GREEK CHARACTERS (UTF-8)
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 1. THE CONFIGURATION DICTIONARY
site_rules = {
    "Kykladiki (Naxos)": {
        "first_page": "https://www.kykladiki.gr/category/kyklades/naxos/",
        "page_template": "https://www.kykladiki.gr/category/kyklades/naxos/page/{}/",
        "headline_tags": ["h2", "h3"],
        "summary_tag": "div",
        "summary_class": "td-excerpt"
    },
    "Kykladiki (Police)": {
        "first_page": "https://www.kykladiki.gr/category/koinonia/astinomika/",
        "page_template": "https://www.kykladiki.gr/category/koinonia/astinomika/page/{}/",
        "headline_tags": ["h2", "h3"],
        "summary_tag": "div",
        "summary_class": "td-excerpt"
    },
    "Naxos Press (Society)": {
        "first_page": "https://www.naxospress.gr/category/koinonia/",
        "page_template": "https://www.naxospress.gr/category/koinonia/page/{}/",
        "headline_tags": ["h1", "h2", "h3"],
        "summary_tag": "div",
        "summary_class": "entry-content"
    },
    "Cyclades24 (Police)": {
        "first_page": "https://cyclades24.gr/category/astynomika/",
        "page_template": "https://cyclades24.gr/category/astynomika/page/{}/",
        "headline_tags": ["h2", "h3"],
        "summary_tag": "p", 
        "summary_class": "" 
    }
}

# 2. KEYWORD FILTERS 
accident_keywords = [
    "τροχαι", "ατυχημ", "συγκρουσ", "παρασυρσ", 
    "δρόμος", "κυκλοφορία", "εγκατάλειψη", "όχημα"
]

location_keywords = [
    "ναξ"
]

def fetch_page_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "el-GR,el;q=0.9,en;q=0.8",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    except requests.exceptions.RequestException:
        print ("[-] Error fetching " + str(url))
        return None

def parse_site_data(html_content, rules, site_name):
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, "html.parser")
    scraped_items = []

    headlines = soup.find_all(rules["headline_tags"])

    for headline in headlines:
        link_element = headline.find("a")
        if not link_element:
            continue
            
        title = link_element.text.strip()
        link = link_element["href"] if link_element.has_attr("href") else "#"
        
        if len(title) < 10:
            continue

        parent = headline.parent
        summary_element = parent.find(rules["summary_tag"], class_=lambda c: c and rules["summary_class"] in c.lower() if c else False)
        
        if not summary_element:
            summary_element = parent.find("p")

        summary = summary_element.text.strip() if summary_element else "No summary available"

        text_to_check = (title + " " + summary).lower()
        text_to_check = text_to_check.replace('ά', 'α').replace('έ', 'ε').replace('ή', 'η').replace('ί', 'ι').replace('ό', 'ο').replace('ύ', 'υ').replace('ώ', 'ω')
        
        is_accident = any(word in text_to_check for word in accident_keywords)
        is_naxos = any(word in text_to_check for word in location_keywords)
                
        if is_accident and is_naxos:
            if not any(item['link'] == link for item in scraped_items):
                scraped_items.append({
                    "source": site_name,
                    "title": title,
                    "summary": summary,
                    "link": link
                })
        
    return scraped_items

def main():
    print ("[+] Initializing Naxos Police & News Scraper...")
    print ("=====================================================")
    
    all_records = []
    pages_to_scrape = 10 
    
    for site_name, rules in site_rules.items():
        print ("\n[*] TARGET: " + str(site_name))
        
        for page_num in range(1, pages_to_scrape + 1):
            if page_num == 1:
                target_url = rules["first_page"]
            else:
                target_url = rules["page_template"].format(page_num)
                
            print ("    -> Scanning page " + str(page_num) + "...")
            raw_html = fetch_page_content(target_url)
            
            if raw_html:
                site_data = parse_site_data(raw_html, rules, site_name)
                all_records.extend(site_data)
                if len(site_data) > 0:
                    print ("       [!] Found " + str(len(site_data)) + " accident records on this page!")
            else:
                print ("    [-] Stopped scanning " + str(site_name) + " due to connection issue or end of pages.")
                break 
                
            time.sleep(random.uniform(1.5, 3.0))
            
    print ("\n=====================================================")
    print ("[+] Scraping complete! Total relevant records found: " + str(len(all_records)))
    print ("=====================================================")
    
    if len(all_records) > 0:
        index = 1
        for item in all_records:
            print ("\n--- Road Safety Alert #" + str(index) + " ---")
            print ("Source:  " + item['source'])
            print ("Title:   " + item['title'])
            print ("Summary: " + item['summary'])
            print ("Link:    " + item['link'])
            index += 1

        # EXPORT TO CSV
        print ("\n[+] Exporting data to naxos_accidents.csv...")
        
        csv_columns = ["source", "title", "summary", "link"]
        csv_filename = "naxos_accidents.csv"
        
        # WE USE 'utf-8-sig' SO EXCEL READS GREEK CHARACTERS CORRECTLY
        try:
            with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                for data in all_records:
                    writer.writerow(data)
            print ("[+] Export successful! Check your folder for " + str(csv_filename))
        except IOError:
            print ("[-] Error writing to CSV file.")

if __name__ == "__main__":
    main()