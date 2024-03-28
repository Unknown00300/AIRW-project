# Integrated CORS in backend and connected and designed a minimalistic frontend.


from flask import Flask, jsonify, request   
import requests
from flask_cors import CORS
from bs4 import BeautifulSoup
from whoosh.index import create_in
from whoosh.fields import *
import os
from whoosh.qparser import QueryParser
from whoosh.index import open_dir
import json
from whoosh.analysis import StandardAnalyzer

app = Flask(__name__)
CORS(app) 

# Create an analyzer
analyzer = StandardAnalyzer()

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

            # Define schema for the index
            schema = Schema(
                name=TEXT(stored=True),
                location=TEXT(stored=True),
                year=TEXT(stored=True),
                criteria=TEXT(stored=True),
                description=TEXT(stored=True),
                tokens=TEXT(analyzer=StandardAnalyzer(), stored=True),
                image_link=TEXT(stored=True)
            )

            # Create a directory named "indexdir" for the index
            if not os.path.exists("indexdir"):
                os.mkdir("indexdir")

            # Create index
            ix = create_in("indexdir", schema)
            
            # Get the writer
            writer = ix.writer()  
            # Add each site to the index
            for row in rows:
                cells = row.find_all('td')
                name_cells = row.find_all('th')
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

                    # Concatenate all details
                    all_details = f"{name} {location} {year} {criteria} {description}"

                    # Preprocess and tokenize the details
                    tokens = [token.text for token in analyzer(all_details)]

                    # Add site information to the dictionary with site name as key
                    sites[name] = {
                        'name': name,
                        'location': location,
                        'year': year,
                        'criteria': criteria,
                        'description': description,
                        'image_link': img_link,
                        'tokens': tokens
                    }
                    # Add each site to the index
                    writer.add_document(**sites[name])

            # Commit the changes
            writer.commit()
        
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
    # print(query_data)
    query = query_data.get('query', '').strip().lower()
    print(query)

    # Retrieve world heritage sites
    sites = get_world_heritage_sites()
    ix = open_dir("indexdir")  # Open the directory that contains the index

    # Create a query parser that searches the 'description' field
    parser = QueryParser("tokens", ix.schema)

    # Parse the query string
    query = parser.parse(query)

    with ix.searcher() as searcher:
        results = searcher.search(query)

        # Collect the results
        result_list = []
        for hit in results:
            result_list.append({
                'name': hit['name'],
                'location': hit['location'],
                'year': hit['year'],
                'criteria': hit['criteria'],
                'description': hit['description'],
                'image_link': hit['image_link']
            })

        if result_list:

            return jsonify({'results': result_list})
        else:
            return jsonify({'message': 'No matching results found.'}), 404


if __name__ == '__main__':
    app.run(debug=True)

#handling wrong queries
#showing similar results based on relevance and tokens of queries

#query preprocessing
#novelty : integrate api to generate the data about the 