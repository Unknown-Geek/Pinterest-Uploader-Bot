---
title: Pinterest Auto-Publisher
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
