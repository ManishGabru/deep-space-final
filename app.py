from flask import Flask, jsonify, request, send_from_directory
import requests, random
from flask_cors import CORS

app = Flask(__name__, static_folder="static")
CORS(app)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/get_image')
def get_image():
    try:
        query = request.args.get('query', 'deep space')
        source = request.args.get('source', 'nasa').lower()
        page = int(request.args.get('page', 1))

        if source == 'nasa' or source == 'jwst':
            search_query = f"{query} JWST" if source == 'jwst' else query
            url = f"https://images-api.nasa.gov/search?media_type=image&q={search_query}&page={page}"
            resp = requests.get(url)
            items = resp.json().get('collection', {}).get('items', [])
            items = [item for item in items if 'links' in item and item['links'][0]['href'].endswith(('.jpg', '.png'))]
            if not items:
                return jsonify({"error": "No images found from NASA/JWST."})
            item = random.choice(items)
            metadata = item['data'][0]
            image_url = item['links'][0]['href']
            return jsonify({
                "image_url": image_url,
                "source": "JWST" if source == "jwst" else "NASA",
                "title": metadata.get('title'),
                "date": metadata.get('date_created'),
                "description": metadata.get('description', ''),
            })

        elif source == 'hubble':
            hubble_resp = requests.get("http://hubblesite.org/api/v3/images")
            images = hubble_resp.json()
            if not images:
                return jsonify({"error": "No images found from Hubble."})
            image = random.choice(images)
            image_id = image.get('id')
            meta_resp = requests.get(f"http://hubblesite.org/api/v3/image/{image_id}")
            metadata = meta_resp.json()
            image_files = metadata.get('image_files', [])
            if not image_files:
                return jsonify({"error": "No valid image file found."})
            largest_image = image_files[-1]['file_url']
            return jsonify({
                "image_url": largest_image,
                "source": "Hubble",
                "title": metadata.get('name', 'Hubble Image'),
                "date": metadata.get('news_name', 'N/A'),
                "description": metadata.get('description', '')
            })
        else:
            return jsonify({"error": "Invalid source selected."})
    except Exception as e:
        return jsonify({"error": str(e)})
