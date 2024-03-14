from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_world_heritage_sites():
    # Define the URL of the Wikipedia page
    url = "https://en.wikipedia.org/wiki/List_of_World_Heritage_Sites_in_India"
    
    try:
        # Fetch the Wikipedia page
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table containing the list of World Heritage Sites
        table = soup.find('table', class_='wikitable')

        if table:
            # Initialize a dictionary to store site information
            sites = {}

            # Find all table rows
            rows = table.find_all('tr')
            
            # Iterate over each row
            for row in rows:
                # Find all table data cells in the row
                cells = row.find_all('td')
                name_cells = row.find_all('th')
                print(cells)
                
                # Extract and store relevant information from each cell
                if len(cells) > 0:
                    name = name_cells[0].text.strip()
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
                    
                    # print(img_link)
                    # Add site information to the dictionary with site name as key
                    sites[name] = {
                        'name': name,
                        'location': location,
                        'year': year,
                        'criteria': criteria,
                        'description': description,
                        'image_link': img_link
                    }
            
            return sites
        
        else:
            return None
    
    except Exception as e:
        print("Error:", e)
        return None

@app.route('/search', methods=['POST'])
def search_world_heritage_sites():
    # Get the query from the request body
    query_data = request.json
    print(query_data)
    query = query_data.get('query', '').strip().lower()
    print(query)
    
    # Retrieve world heritage sites
    sites = get_world_heritage_sites()
    
    if sites:
        # Search for the query in site names
        results = [sites[name] for name in sites if query in name.lower()]
        
        if results:
            return jsonify({'results': results})
        else:
            return jsonify({'message': 'No matching results found.'}), 404
    else:
        return jsonify({'message': 'Failed to retrieve world heritage sites data.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
