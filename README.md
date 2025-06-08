---
title: Pinterest-Auto-Publisher
emoji: 🎯
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
---

# 🎯 Pinterest Auto-Publisher

An AI-powered automation tool for uploading pins to Pinterest using Selenium WebDriver and Gradio interface.

## Features

- 🚀 **Automated Pin Upload**: Upload images to Pinterest with automated form filling
- 🖼️ **Image Support**: Support for various image formats (PNG, JPG, etc.)
- 📝 **Complete Pin Details**: Set title, description, board, and destination links
- 🔒 **Secure**: Credentials are only used during the session
- 🎨 **User-Friendly Interface**: Clean Gradio web interface
- 📱 **Responsive**: Works on desktop and mobile devices

## How to Use

1. **Enter Pinterest Credentials**: Your email and password
2. **Upload Image**: Select the image you want to pin
3. **Fill Pin Details**:
   - Title: Catchy, descriptive title
   - Description: Detailed description with keywords
   - Board Name: Exact name of your Pinterest board
   - Link (Optional): Destination URL for the pin
4. **Upload**: Click "Upload to Pinterest" and wait for completion

## Requirements

- Valid Pinterest account
- Board must already exist in your Pinterest account
- High-quality images recommended (1000x1500px or 2:3 ratio)

## Technical Details

- Built with Python, Selenium WebDriver, and Gradio
- Uses headless Chrome browser for automation
- Supports Pinterest's React-based interface
- Includes anti-detection measures for reliable automation
- **Chrome Version**: 131.0.6778.87 (hardcoded for compatibility)
- **ChromeDriver Version**: 131.0.6778.87 (matching)
- **Production Ready**: Optimized Chrome flags for containerized environments

## Deployment

### Hugging Face Spaces
1. Create a new Space on Hugging Face
2. Use repository name: `pinterest-auto-publisher` (lowercase, hyphens only)
3. Upload all files to the Space
4. The application will auto-deploy using `app.py`

### Other Platforms (Render.com, Railway, etc.)
1. Use `startup_enhanced.py` for robust initialization
2. Run validation with: `python validate_deployment.py`
3. The app includes production Chrome configuration

## Setup for Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Access the interface at `http://localhost:7860`

## Notes

- The automation process takes 30-60 seconds
- Make sure board names match exactly with your Pinterest boards
- Keep your credentials secure
- For production deployment, consider using environment variables for sensitive data
