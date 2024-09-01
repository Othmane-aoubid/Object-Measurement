from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io

app = Flask(__name__)
CORS(app)

def process_image(image_data):
    # Decode base64 image
    image_data = image_data.split(',')[1]
    image_bytes = base64.b64decode(image_data)
    
    # Convert image to grayscale pixel array
    image = []
    with io.BytesIO(image_bytes) as byte_stream:
        # Skip JPEG header (first two bytes)
        byte_stream.read(2)
        
        while True:
            # Read image data in 3-byte chunks (RGB)
            chunk = byte_stream.read(3)
            if not chunk:
                break
            # Convert RGB to grayscale
            gray = int(0.299 * chunk[0] + 0.587 * chunk[1] + 0.114 * chunk[2])
            image.append(gray)
    
    # Determine image dimensions (assuming square image for simplicity)
    width = height = int(len(image) ** 0.5)
    
    # Convert flat array to 2D array
    pixel_array = [image[i:i+width] for i in range(0, len(image), width)]
    
    return pixel_array, width, height

def create_binary_image(pixel_array, width, height):
    # Calculate threshold (simple average)
    threshold = sum(sum(row) for row in pixel_array) / (width * height)
    
    # Create binary image
    return [[0 if pixel < threshold else 1 for pixel in row] for row in pixel_array]

def detect_edges(image):
    height = len(image)
    width = len(image[0])
    edges = [[0 for _ in range(width)] for _ in range(height)]
    
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if image[y][x] != image[y-1][x] or \
               image[y][x] != image[y+1][x] or \
               image[y][x] != image[y][x-1] or \
               image[y][x] != image[y][x+1]:
                edges[y][x] = 1
    
    return edges

def find_object_boundaries(edges):
    height = len(edges)
    width = len(edges[0])
    min_x, min_y = width, height
    max_x, max_y = 0, 0
    
    for y in range(height):
        for x in range(width):
            if edges[y][x] == 1:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    
    return min_x, min_y, max_x, max_y

def calculate_dimensions(min_x, min_y, max_x, max_y):
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    return width, height

@app.route('/measure', methods=['POST'])
def measure_object():
    image_data = request.json['image']
    
    pixel_array, width, height = process_image(image_data)
    binary_image = create_binary_image(pixel_array, width, height)
    edges = detect_edges(binary_image)
    min_x, min_y, max_x, max_y = find_object_boundaries(edges)
    object_width, object_height = calculate_dimensions(min_x, min_y, max_x, max_y)
    
    return jsonify({
        'width': object_width,
        'height': object_height
    })

if __name__ == '__main__':
    app.run(debug=True)