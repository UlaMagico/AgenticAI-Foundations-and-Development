# Target: National Central University
url = 'https://www.ncu.edu.tw/?Lang=en'

import requests
from bs4 import BeautifulSoup
import json

def inspect_page_structure():
    """
    Inspect the actual structure of the page
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print("PAGE STRUCTURE ANALYSIS:")
    print("=" * 50)
    
    # Find all headings
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    if headings:
        print("\nHeadings found:")
        for heading in headings[:15]:
            print(f"  {heading.name}: {heading.get_text(strip=True)[:60]}")
    
    # Find all divs with common classes
    print("\nCommon div classes:")
    divs = soup.find_all('div', class_=True)
    classes = {}
    for div in divs:
        div_classes = div.get('class', [])
        for cls in div_classes:
            classes[cls] = classes.get(cls, 0) + 1
    
    for cls, count in sorted(classes.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  .{cls}: {count}")
    
    # Find all links
    print("\nSample links (first 20):")
    links = soup.find_all('a', href=True)
    for link in links[:20]:
        href = link.get('href')
        text = link.get_text(strip=True)
        if text:
            print(f"  [{text}] → {href[:60]}")


def scrape_ncu_website():
    """
    Scrape NCU website for news titles, course info, and faculty list
    """
    try:
        # Send GET request to the website
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"Failed to fetch website. Status code: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Initialize data containers
        data = {
            'news': [],
            'courses': [],
            'faculty': [],
            'departments': [],
            'all_links': []
        }
        
        # ========== EXTRACT ALL MEANINGFUL CONTENT ==========
        print("=" * 50)
        print("EXTRACTING WEBSITE CONTENT")
        print("=" * 50)
        
        # Get all headings (they usually contain important info)
        print("\n📋 HEADINGS & TITLES:")
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for heading in headings[:30]:
            text = heading.get_text(strip=True)
            if text and len(text) > 3:
                print(f"  • {text}")
                data['news'].append(text)
        
        # Get all meaningful links
        print("\n🔗 AVAILABLE LINKS:")
        links = soup.find_all('a', href=True)
        for link in links:
            text = link.get_text(strip=True)
            href = link.get('href', '')
            
            if text and len(text) > 2:
                # Categorize links
                lower_href = href.lower()
                lower_text = text.lower()
                
                if any(keyword in lower_href or keyword in lower_text 
                       for keyword in ['news', 'announcement', 'article', 'event']):
                    if text not in data['news']:
                        data['news'].append(text)
                        print(f"  📰 {text}")
                
                elif any(keyword in lower_href or keyword in lower_text 
                         for keyword in ['course', 'program', 'class', 'syllabus']):
                    if text not in data['courses']:
                        data['courses'].append(text)
                        print(f"  📚 {text}")
                
                elif any(keyword in lower_href or keyword in lower_text 
                         for keyword in ['faculty', 'staff', 'professor', 'teacher', 'department']):
                    if text not in data['faculty']:
                        data['faculty'].append(text)
                        print(f"  👨‍🏫 {text}")
                
                # Keep track of all unique links
                if text not in [item[0] for item in data['all_links']]:
                    data['all_links'].append((text, href))
        
        # Get text from specific div patterns
        print("\n📝 MAIN CONTENT:")
        containers = soup.find_all(['article', 'main', 'section'])
        for container in containers:
            paragraphs = container.find_all('p')
            for p in paragraphs[:5]:
                text = p.get_text(strip=True)
                if text and len(text) > 20:
                    print(f"  {text[:100]}...")
                    if text not in data['news']:
                        data['news'].append(text[:200])
        
        # ========== SUMMARY ==========
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        print(f"✓ News/Titles items found: {len(data['news'])}")
        print(f"✓ Course items found: {len(data['courses'])}")
        print(f"✓ Faculty/Department items found: {len(data['faculty'])}")
        print(f"✓ Total unique links found: {len(data['all_links'])}")
        
        return data
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the website: {e}")
        return None
    except Exception as e:
        print(f"Error parsing the website: {e}")
        return None


if __name__ == "__main__":
    print(f"Starting to scrape: {url}\n")
    
    # First, inspect the page structure
    print("First, let's analyze the page structure...\n")
    inspect_page_structure()
    
    print("\n" + "=" * 70 + "\n")
    
    # Then scrape the data
    scraped_data = scrape_ncu_website()
    
    # Save to JSON
    if scraped_data:
        with open('ncu_data.json', 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, ensure_ascii=False, indent=2)
        print("\n✓ Data saved to ncu_data.json")
