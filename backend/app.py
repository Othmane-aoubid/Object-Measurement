from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io

app = Flask(__name__)
CORS(app)

# ... (keep all your existing functions)

@app.route('/api/measure', methods=['POST'])
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

# Remove the following lines:
# if __name__ == '__main__':
#     app.run(debug=True)