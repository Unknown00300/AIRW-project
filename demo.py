import requests
from bs4 import BeautifulSoup

url = "https://en.wikipedia.org/wiki/List_of_World_Heritage_Sites_in_India"
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

# Find the table containing the list of World Heritage Sites
table = soup.find('table', class_='wikitable')

# Check if the table is found
if table:
    # Find all table rows
    rows = table.find_all('tr')
    
    # Iterate over each row
    for row in rows:
        # Find all table data cells in the row
        cells = row.find_all('td')
        
        # Extract and print relevant information from each cell
        if len(cells) > 0:
            name = cells[0].text.strip()
            location = cells[1].text.strip()
            year = cells[2].text.strip()
            criteria = cells[3].text.strip()
            description = cells[4].text.strip()
            
            # Find the image tag within the cell
            img_tag = cells[0].find('img')
            if img_tag:
                img_link = img_tag['src']
            else:
                img_link = None
            
            print("Name:", name)
            print("Location:", location)
            print("Year:", year)
            print("Criteria:", criteria)
            print("Description:", description)
            print("Image Link:", img_link)
            print()
else:
    print("Table not found.")
