import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import urljoin
import inquirer
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

class ZombiesDataCleaner:
    def __init__(self):
        nltk.download('punkt')
        nltk.download('stopwords')
        self.stop_words = set(stopwords.words('english'))
        
    def clean_text(self, text):
        if not text:
            return ""
            
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)
        
        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s.,!?]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Remove gaming-unrelated terms
        gaming_stopwords = {'click', 'subscribe', 'like', 'comment', 'video', 'watch'}
        words = text.split()
        words = [w for w in words if w.lower() not in gaming_stopwords]
        
        return ' '.join(words).strip()
    
    def is_relevant(self, text, keywords):
        """Check if text contains relevant keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)
    
    def structure_sentences(self, text):
        """Split text into well-formed sentences"""
        sentences = sent_tokenize(text)
        return [s.strip() for s in sentences if len(s.strip()) > 20]

class ZombiesDataCollector:
    def __init__(self):
        self.cleaner = ZombiesDataCleaner()
        self.sources = {
            "Nazi Zombies Wiki": {
                "base_url": "https://nazizombies.fandom.com",
                "maps_path": "/wiki/Call_of_Duty:_Black_Ops_II#Zombies",
                "weapons_path": "/wiki/Category:Call_of_Duty:_Black_Ops_II_Zombies_Weapons",
                "perks_path": "/wiki/Category:Call_of_Duty:_Black_Ops_II_Perks"
            },
            "COD Fandom": {
                "base_url": "https://callofduty.fandom.com",
                "maps_path": "/wiki/Call_of_Duty:_Black_Ops_II_Zombies",
                "weapons_path": "/wiki/Category:Call_of_Duty:_Black_Ops_II_Weapons",
                "perks_path": "/wiki/Perk-a-Cola"
            },
            "Game Guides": {
                "urls": [
                    "https://www.ign.com/wikis/call-of-duty-black-ops-2/Zombies",
                    "https://www.gamesradar.com/call-of-duty-black-ops-2-zombies-guide/",
                    # Add more guide URLs
                ]
            },
            "YouTube Guides": {
                "video_ids": [
                    # Add relevant YouTube video IDs
                    "XXXXX",  # Replace with actual video IDs
                ]
            },
            "Reddit Discussions": {
                "subreddits": ["CODZombies", "blackops2"],
                "search_terms": ["Black Ops 2", "BO2 zombies", "Black Ops II zombies"]
            }
        }
        
        self.collected_data = {
            "maps": {},
            "weapons": {},
            "perks": {},
            "characters": {},
            "easter_eggs": {},
            "gameplay_mechanics": {}
        }
        
        # Create data directory if it doesn't exist
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
    def get_soup(self, url, retry_count=3):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        
        for attempt in range(retry_count):
            try:
                time.sleep(1)  # Be nice to servers
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return BeautifulSoup(response.text, 'html.parser')
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == retry_count - 1:
                    print(f"Failed to fetch {url} after {retry_count} attempts")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def ask_sources(self):
        questions = [
            inquirer.Checkbox('sources',
                message="Which sources would you like to scrape?",
                choices=list(self.sources.keys())),
            inquirer.Checkbox('data_types',
                message="What type of data would you like to collect?",
                choices=['Maps', 'Weapons', 'Perks', 'Characters', 'Easter Eggs']),
        ]
        
        answers = inquirer.prompt(questions)
        return answers

    def collect_map_data(self, source_name, map_url, map_name):
        print(f"\nCollecting data for map: {map_name} from {source_name}")
        soup = self.get_soup(map_url)
        if not soup:
            return
            
        map_data = {
            "description": "",
            "features": [],
            "locations": [],
            "weapons": [],
            "easter_eggs": [],
            "strategies": [],
            "source": source_name
        }
        
        # Get main content
        content = soup.find('div', {'class': 'mw-parser-output'})
        if content:
            # Get description
            first_p = content.find('p')
            if first_p:
                map_data["description"] = first_p.get_text().strip()
            
            # Get sections
            sections = content.find_all(['h2', 'h3'])
            for section in sections:
                section_title = section.get_text().lower()
                next_elem = section.find_next_sibling()
                
                while next_elem and next_elem.name not in ['h2', 'h3']:
                    if next_elem.name in ['p', 'ul', 'li']:
                        text = next_elem.get_text().strip()
                        if text:
                            if any(keyword in section_title for keyword in ['location', 'area', 'room']):
                                map_data["locations"].append(text)
                            elif any(keyword in section_title for keyword in ['weapon', 'armory', 'gun']):
                                map_data["weapons"].append(text)
                            elif any(keyword in section_title for keyword in ['easter egg', 'secret']):
                                map_data["easter_eggs"].append(text)
                            elif any(keyword in section_title for keyword in ['strateg', 'guide', 'tip']):
                                map_data["strategies"].append(text)
                            elif any(keyword in section_title for keyword in ['feature', 'mechanic']):
                                map_data["features"].append(text)
                    next_elem = next_elem.find_next_sibling()
        
        if map_name not in self.collected_data["maps"]:
            self.collected_data["maps"][map_name] = map_data
        else:
            # Merge data from multiple sources
            for key, value in map_data.items():
                if isinstance(value, list):
                    self.collected_data["maps"][map_name][key].extend(value)
                elif not self.collected_data["maps"][map_name][key]:
                    self.collected_data["maps"][map_name][key] = value

    def collect_weapons_data(self, source_name, base_url, weapons_path):
        print(f"\nCollecting weapons data from {source_name}")
        weapons_url = urljoin(base_url, weapons_path)
        soup = self.get_soup(weapons_url)
        if not soup:
            return
        
        weapon_links = soup.find_all('a', href=re.compile(r'/wiki/.*'))
        for link in weapon_links:
            weapon_url = urljoin(base_url, link['href'])
            weapon_name = link.get_text().strip()
            
            if not weapon_name or len(weapon_name) < 3:
                continue
                
            print(f"Processing weapon: {weapon_name}")
            weapon_soup = self.get_soup(weapon_url)
            if not weapon_soup:
                continue
                
            weapon_data = {
                "stats": self.extract_weapon_stats(weapon_soup),
                "description": self.extract_weapon_description(weapon_soup),
                "pack_a_punch": self.extract_pack_a_punch(weapon_soup),
                "locations": self.extract_weapon_locations(weapon_soup),
                "source": source_name
            }
            
            if weapon_name not in self.collected_data["weapons"]:
                self.collected_data["weapons"][weapon_name] = weapon_data
            else:
                # Merge data from multiple sources
                self.merge_weapon_data(weapon_name, weapon_data)

    def extract_weapon_stats(self, soup):
        stats = {}
        stats_table = soup.find('table', {'class': re.compile(r'.*stats.*')})
        if stats_table:
            rows = stats_table.find_all('tr')
            for row in rows:
                cols = row.find_all(['th', 'td'])
                if len(cols) >= 2:
                    stat_name = cols[0].get_text().strip()
                    stat_value = cols[1].get_text().strip()
                    stats[stat_name] = stat_value
        return stats

    def extract_weapon_description(self, soup):
        first_p = soup.find('p')
        return first_p.get_text().strip() if first_p else ""

    def extract_pack_a_punch(self, soup):
        pap_section = soup.find(lambda tag: tag.name in ['h2', 'h3'] and 
                              'pack-a-punch' in tag.get_text().lower())
        if pap_section:
            next_elem = pap_section.find_next_sibling()
            if next_elem and next_elem.name == 'p':
                return next_elem.get_text().strip()
        return ""

    def extract_weapon_locations(self, soup):
        locations = []
        location_section = soup.find(lambda tag: tag.name in ['h2', 'h3'] and 
                                   'location' in tag.get_text().lower())
        if location_section:
            next_elem = location_section.find_next_sibling()
            while next_elem and next_elem.name in ['p', 'ul', 'li']:
                locations.append(next_elem.get_text().strip())
                next_elem = next_elem.find_next_sibling()
        return locations

    def merge_weapon_data(self, weapon_name, new_data):
        current_data = self.collected_data["weapons"][weapon_name]
        for key, value in new_data.items():
            if isinstance(value, list):
                current_data[key].extend(value)
            elif isinstance(value, dict):
                current_data[key].update(value)
            elif not current_data[key]:
                current_data[key] = value

    def collect_youtube_data(self):
        print("\nCollecting YouTube transcripts...")
        youtube_data = []
        
        for video_id in self.sources["YouTube Guides"]["video_ids"]:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                full_text = " ".join([entry['text'] for entry in transcript])
                
                # Clean and structure the transcript
                cleaned_text = self.cleaner.clean_text(full_text)
                if self.cleaner.is_relevant(cleaned_text, ['zombie', 'map', 'weapon']):
                    sentences = self.cleaner.structure_sentences(cleaned_text)
                    youtube_data.extend(sentences)
                    
            except Exception as e:
                print(f"Error processing video {video_id}: {str(e)}")
        
        return youtube_data

    def collect_reddit_data(self):
        print("\nCollecting Reddit discussions...")
        reddit_data = []
        
        # Initialize Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            for subreddit in self.sources["Reddit Discussions"]["subreddits"]:
                for search_term in self.sources["Reddit Discussions"]["search_terms"]:
                    url = f"https://www.reddit.com/r/{subreddit}/search/?q={search_term}&restrict_sr=1"
                    driver.get(url)
                    
                    # Wait for posts to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "Post"))
                    )
                    
                    # Get post content
                    posts = driver.find_elements(By.CLASS_NAME, "Post")
                    for post in posts:
                        try:
                            title = post.find_element(By.CLASS_NAME, "title").text
                            content = post.find_element(By.CLASS_NAME, "content").text
                            
                            combined_text = f"{title} {content}"
                            cleaned_text = self.cleaner.clean_text(combined_text)
                            
                            if self.cleaner.is_relevant(cleaned_text, ['zombie', 'map', 'weapon']):
                                sentences = self.cleaner.structure_sentences(cleaned_text)
                                reddit_data.extend(sentences)
                                
                        except Exception as e:
                            continue
                            
        finally:
            driver.quit()
        
        return reddit_data

    def collect_guide_data(self):
        print("\nCollecting game guides...")
        guide_data = []
        
        for url in self.sources["Game Guides"]["urls"]:
            try:
                soup = self.get_soup(url)
                if not soup:
                    continue
                
                # Find main content area (adjust selectors based on the site)
                content = soup.find('article') or soup.find('div', class_='article-content')
                if content:
                    text = content.get_text()
                    cleaned_text = self.cleaner.clean_text(text)
                    
                    if self.cleaner.is_relevant(cleaned_text, ['zombie', 'map', 'weapon']):
                        sentences = self.cleaner.structure_sentences(cleaned_text)
                        guide_data.extend(sentences)
                        
            except Exception as e:
                print(f"Error processing guide {url}: {str(e)}")
        
        return guide_data

    def save_data(self):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Clean and structure all collected data
        for category in self.collected_data:
            for item_name, item_data in self.collected_data[category].items():
                if isinstance(item_data, dict):
                    for key, value in item_data.items():
                        if isinstance(value, str):
                            item_data[key] = self.cleaner.clean_text(value)
                        elif isinstance(value, list):
                            cleaned_list = []
                            for text in value:
                                cleaned_text = self.cleaner.clean_text(text)
                                if cleaned_text and self.cleaner.is_relevant(cleaned_text, ['zombie', 'map', 'weapon']):
                                    cleaned_list.extend(self.cleaner.structure_sentences(cleaned_text))
                            item_data[key] = cleaned_list
        
        # Save structured data
        structured_filename = os.path.join(self.data_dir, f'zombies_dataset_structured_{timestamp}.json')
        with open(structured_filename, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
        
        # Create enhanced training data
        training_data = self.create_training_data()
        
        # Save training data
        training_filename = os.path.join(self.data_dir, f'zombies_dataset_training_{timestamp}.json')
        with open(training_filename, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
            
        print(f"\nData saved to:")
        print(f"- {structured_filename}")
        print(f"- {training_filename}")

    def create_training_data(self):
        """Create well-structured training examples"""
        training_data = []
        
        # Create map-specific examples
        for map_name, map_data in self.collected_data["maps"].items():
            # Basic information
            training_data.append({
                "question": f"What is {map_name}?",
                "answer": map_data["description"]
            })
            
            # Features and locations
            if map_data["features"]:
                training_data.append({
                    "question": f"What are the features of {map_name}?",
                    "answer": ". ".join(map_data["features"])
                })
            
            if map_data["locations"]:
                training_data.append({
                    "question": f"What are the locations in {map_name}?",
                    "answer": ". ".join(map_data["locations"])
                })
            
            # Easter eggs
            if map_data["easter_eggs"]:
                training_data.append({
                    "question": f"What easter eggs are in {map_name}?",
                    "answer": ". ".join(map_data["easter_eggs"])
                })
        
        # Create weapon-specific examples
        for weapon_name, weapon_data in self.collected_data["weapons"].items():
            training_data.append({
                "question": f"Tell me about the {weapon_name}",
                "answer": weapon_data["description"]
            })
            
            if weapon_data["stats"]:
                training_data.append({
                    "question": f"What are the stats for {weapon_name}?",
                    "answer": ". ".join([f"{k}: {v}" for k, v in weapon_data["stats"].items()])
                })
        
        return training_data

    def collect_all_data(self):
        # Ask user for sources and data types
        answers = self.ask_sources()
        
        if not answers or not answers['sources']:
            print("No sources selected. Exiting...")
            return
            
        for source_name in answers['sources']:
            source = self.sources[source_name]
            print(f"\nCollecting data from {source_name}...")
            
            if 'Maps' in answers['data_types']:
                # Collect map data
                main_url = urljoin(source['base_url'], source['maps_path'])
                soup = self.get_soup(main_url)
                if soup:
                    map_links = soup.find_all('a', href=re.compile(r'/wiki/.*map.*'))
                    for link in map_links:
                        map_url = urljoin(source['base_url'], link['href'])
                        map_name = link.get_text().strip()
                        self.collect_map_data(source_name, map_url, map_name)
            
            if 'Weapons' in answers['data_types']:
                self.collect_weapons_data(source_name, source['base_url'], source['weapons_path'])
            
            # Add similar collection methods for other data types...
        
        self.save_data()
        print("\nData collection completed!")

if __name__ == "__main__":
    collector = ZombiesDataCollector()
    collector.collect_all_data() 