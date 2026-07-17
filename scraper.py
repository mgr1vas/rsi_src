import sys
import time
import random
import requests
from bs4 import BeautifulSoup

# FORCE THE TERMINAL TO SUPPORT GREEK CHARACTERS (UTF-8)
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

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
    except requests.exceptions.RequestException as e:
        print ("[-] Error fetching " + str(url) + ": " + str(e))
        return None

def parse_naxos_data(html_content):
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, "html.parser")
    scraped_items = []

    # LIST OF KEYWORDS
    keywords = [
        "τροχαίο", 
        "ατύχημα", 
        "σύγκρουση", 
        "παράσυρση", 
        "δρόμος", 
        "όχημα", 
        "κυκλοφορία",
        "μοτοσικλέτα",
        "εγκατάλειψη"
    ]

    headlines = soup.find_all(["h2", "h3"])

    for headline in headlines:
        link_element = headline.find("a")
        if not link_element:
            continue
            
        title = link_element.text.strip()
        link = link_element["href"] if link_element.has_attr("href") else "#"
        
        if len(title) < 10:
            continue

        parent = headline.parent
        summary_element = parent.find("div", class_=lambda c: c and "excerpt" in c.lower() if c else False)
        
        if not summary_element:
            summary_element = parent.find("p")

        summary = summary_element.text.strip() if summary_element else "No summary available"

        text_to_check = (title + " " + summary).lower()
        
        is_relevant = False
        for word in keywords:
            if word in text_to_check:
                is_relevant = True
                break
                
        if is_relevant:
            scraped_items.append({
                "title": title,
                "summary": summary,
                "link": link
            })
        
    return scraped_items

def main():
    print ("[+] Initializing Naxos MVP scraper for historical traffic news...")
    
    all_records = []
    pages_to_scrape = 5 # CHANGE THIS NUMBER TO DIG DEEPER INTO THE PAST
    
    for page_num in range(1, pages_to_scrape + 1):
        # HANDLE THE DIFFERENCE BETWEEN PAGE 1 AND THE REST
        if page_num == 1:
            target_url = "https://www.kykladiki.gr/category/kyklades/naxos/"
        else:
            target_url = "https://www.kykladiki.gr/category/kyklades/naxos/page/" + str(page_num) + "/"
            
        print ("[*] Scraping page " + str(page_num) + "...")
        raw_html = fetch_page_content(target_url)
        
        if raw_html:
            page_data = parse_naxos_data(raw_html)
            all_records.extend(page_data)
            print ("    -> Found " + str(len(page_data)) + " relevant records on this page.")
        else:
            print ("[-] Stopping scraper at page " + str(page_num) + " due to connection issue.")
            break
            
        # POLITENESS DELAY (CRITICAL WHEN LOOPING PAGES SO WE DON'T GET BANNED)
        time.sleep(random.uniform(2.0, 4.0))
        
    # PRINT THE FINAL CONSOLIDATED RESULTS
    print ("[+] Scraping complete! Total relevant records found: " + str(len(all_records)))
    
    if len(all_records) > 0:
        index = 1
        for item in all_records:
            print ("\n--- Road Safety Alert #" + str(index) + " ---")
            print ("Title: " + item['title'])
            print ("Summary: " + item['summary'])
            print ("Link: " + item['link'])
            index += 1

if __name__ == "__main__":
    main()
