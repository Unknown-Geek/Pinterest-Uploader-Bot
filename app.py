from flask import Flask, request, render_template, jsonify, flash, redirect, url_for
import os
import logging
from werkzeug.utils import secure_filename
from pinterest_automation import PinterestAutomation
from selenium.webdriver.common.by import By
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pinterest_bot.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pin():
    try:
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password')
        title = request.form.get('title')
        description = request.form.get('description')
        board_name = request.form.get('board_name')
        link_url = request.form.get('link_url', '')
        
        # Validate required fields
        if not all([email, password, title, description, board_name]):
            return jsonify({'success': False, 'message': 'All required fields must be filled'})
        
        # Check if file was uploaded
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'No image file uploaded'})
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No image file selected'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WEBP'})
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Create Pinterest automation instance
        pinterest_bot = PinterestAutomation()
        
        # Upload to Pinterest
        result = pinterest_bot.upload_pin(
            email=email,
            password=password,
            image_path=filepath,
            title=title,
            description=description,
            board_name=board_name,
            link_url=link_url
        )
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        if result['success']:
            return jsonify({
                'success': True, 
                'message': 'Pin uploaded successfully!',
                'pin_url': result.get('pin_url', '')
            })
        else:
            return jsonify({
                'success': False, 
                'message': f"Upload failed: {result['message']}"
            })
            
    except Exception as e:
        logging.error(f"Error in upload route: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@app.route('/test_login', methods=['POST'])
def test_login():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'})
        
        pinterest_bot = PinterestAutomation()
        result = pinterest_bot.test_login(email, password)
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error in test_login route: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@app.route('/get_boards', methods=['POST'])
def get_boards():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'})
        
        pinterest_bot = PinterestAutomation()
        result = pinterest_bot.get_user_boards(email, password)
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error in get_boards route: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@app.route('/debug_fields', methods=['POST'])
def debug_fields():
    """Debug route to test field detection on Pinterest"""
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'})
        
        pinterest_bot = PinterestAutomation()
        
        # Login first
        login_result = pinterest_bot.login(email, password)
        if not login_result:
            return jsonify({'success': False, 'message': 'Login failed'})
        
        # Go to pin creation page
        pinterest_bot.driver.get("https://www.pinterest.com/pin-builder/")
        pinterest_bot._human_delay(3, 5)
        
        debug_info = {
            'description_field': None,
            'link_field': None,
            'all_inputs': []
        }
        
        # Test description field
        try:
            desc_field = pinterest_bot.driver.find_element(By.CSS_SELECTOR, "textarea[placeholder='Tell everyone what your Pin is about']")
            debug_info['description_field'] = {
                'found': True,
                'visible': desc_field.is_displayed(),
                'enabled': desc_field.is_enabled(),
                'placeholder': desc_field.get_attribute('placeholder')
            }
        except Exception as e:
            debug_info['description_field'] = {
                'found': False,
                'error': str(e)
            }
        
        # Test link field
        try:
            link_field = pinterest_bot.driver.find_element(By.CSS_SELECTOR, "input[placeholder='Add a destination link']")
            debug_info['link_field'] = {
                'found': True,
                'visible': link_field.is_displayed(),
                'enabled': link_field.is_enabled(),
                'placeholder': link_field.get_attribute('placeholder')
            }
        except Exception as e:
            debug_info['link_field'] = {
                'found': False,
                'error': str(e)
            }
        
        # Get all visible input fields for analysis
        inputs = pinterest_bot.driver.find_elements(By.CSS_SELECTOR, "input, textarea")
        for inp in inputs:
            if inp.is_displayed():
                debug_info['all_inputs'].append({
                    'tag': inp.tag_name,
                    'type': inp.get_attribute('type') or '',
                    'placeholder': inp.get_attribute('placeholder') or '',
                    'aria_label': inp.get_attribute('aria-label') or '',
                    'id': inp.get_attribute('id') or '',
                    'class': inp.get_attribute('class') or ''
                })
        
        pinterest_bot.close()
        
        return jsonify({
            'success': True,
            'debug_info': debug_info,
            'message': 'Field detection completed'
        })
        
    except Exception as e:
        logging.error(f"Error in debug_fields route: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
