# Pinterest Auto-Publisher

A simple and efficient Flask web application for automatically publishing pins to Pinterest using Selenium WebDriver.

## Features

- 🚀 **Automated Pinterest Login** - Secure login with your Pinterest credentials
- 📸 **Image Upload** - Support for PNG, JPG, JPEG, GIF, WEBP (up to 16MB)
- ✍️ **Smart Content Setting** - Automatically sets title, description, and destination links
- 📌 **Board Selection** - Choose which board to pin to
- 🤖 **Human-like Interactions** - Mimics human behavior to avoid detection
- 🔄 **Retry Mechanisms** - Multiple fallback methods for each operation
- 🎨 **Beautiful UI** - Modern, responsive web interface
- 📊 **Real-time Feedback** - Loading indicators and status updates

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install Chrome WebDriver:**
   - Download ChromeDriver from [https://chromedriver.chromium.org/](https://chromedriver.chromium.org/)
   - Make sure it matches your Chrome browser version
   - Add ChromeDriver to your system PATH

## Usage

1. **Start the Flask application:**

   ```bash
   python app.py
   ```

2. **Open your web browser and go to:**

   ```
   http://localhost:5000
   ```

3. **Fill in the form:**

   - Pinterest email and password
   - Upload your image
   - Enter pin title and description
   - Specify the board name
   - Add destination link (optional)

4. **Test login** (recommended) before uploading

5. **Click "Upload Pin"** and wait for the process to complete

## Configuration

### Headless Mode

To run the browser in headless mode (no GUI), modify `pinterest_automation.py`:

```python
pinterest_bot = PinterestAutomation(headless=True)
```

### Custom Upload Directory

Change the upload directory in `app.py`:

```python
app.config['UPLOAD_FOLDER'] = 'your_custom_uploads_folder'
```

## How It Works

1. **Login Process**: Uses Selenium to navigate to Pinterest and log in
2. **Image Upload**: Finds and interacts with Pinterest's pin builder
3. **Content Setting**: Uses multiple methods to set title, description, and links
4. **Board Selection**: Locates and selects the specified board
5. **Publishing**: Finds and clicks the publish button
6. **Verification**: Checks for success indicators

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**

   - Make sure ChromeDriver is installed and in your PATH
   - Check that the version matches your Chrome browser

2. **Login fails**

   - Verify your Pinterest credentials
   - Check if 2FA is enabled (not currently supported)
   - Try running in non-headless mode to see what's happening

3. **Elements not found**

   - Pinterest occasionally updates their website structure
   - The automation includes multiple fallback methods
   - Check the console logs for detailed error information

4. **Upload fails**
   - Ensure image file is under 16MB
   - Check that the image format is supported
   - Verify board name exists in your Pinterest account

### Debugging

1. **Enable verbose logging** by setting the log level to DEBUG in `pinterest_automation.py`
2. **Run in non-headless mode** to see the browser actions
3. **Check the log file** `pinterest_bot.log` for detailed error information

## Security Notes

- **Never commit credentials** to version control
- Consider using environment variables for sensitive data
- The application stores credentials only temporarily during execution
- Uploaded images are automatically deleted after processing

## Limitations

- Does not support Pinterest accounts with 2FA enabled
- Board names must be exact matches
- Some Pinterest features may not be supported
- Rate limiting may apply for bulk uploads

## Contributing

Feel free to contribute improvements:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Disclaimer

This tool is for educational and personal use only. Users are responsible for complying with Pinterest's Terms of Service and ensuring they have the right to upload the content they're posting.

## License

This project is open source and available under the MIT License.
