#!/usr/bin/env python3
"""
Pinterest Auto-Publisher - Setup ChromeDriver

This script helps detect and setup ChromeDriver for the Pinterest automation.
"""

import os
import sys
import subprocess
import requests
import zipfile
import platform
from pathlib import Path

def get_chrome_version():
    """Get installed Chrome version"""
    try:
        if platform.system() == "Windows":
            import winreg
            # Try different registry paths for Chrome
            paths = [
                r"SOFTWARE\Google\Chrome\BLBeacon",
                r"SOFTWARE\Wow6432Node\Google\Chrome\BLBeacon",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
            ]
            
            for path in paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
                        version, _ = winreg.QueryValueEx(key, "version")
                        return version.split('.')[0]  # Return major version
                except:
                    continue
                    
            # Fallback: try command line
            result = subprocess.run([
                'reg', 'query', 
                'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', 
                '/v', 'version'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'version' in line:
                        version = line.split()[-1]
                        return version.split('.')[0]
                        
        elif platform.system() == "Darwin":  # macOS
            result = subprocess.run([
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', 
                '--version'
            ], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip().split()[-1]
                return version.split('.')[0]
                
        elif platform.system() == "Linux":
            result = subprocess.run(['google-chrome', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip().split()[-1]
                return version.split('.')[0]
                
    except Exception as e:
        print(f"Error detecting Chrome version: {e}")
        
    return None

def download_chromedriver(version):
    """Download appropriate ChromeDriver version"""
    try:
        # ChromeDriver download URL pattern
        base_url = "https://chromedriver.storage.googleapis.com"
        
        # Get platform-specific filename
        if platform.system() == "Windows":
            filename = "chromedriver_win32.zip"
        elif platform.system() == "Darwin":
            filename = "chromedriver_mac64.zip"
        elif platform.system() == "Linux":
            filename = "chromedriver_linux64.zip"
        else:
            print("Unsupported platform")
            return False
            
        # For Chrome 115+, use the new API
        if int(version) >= 115:
            api_url = f"https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
            print("Fetching latest ChromeDriver version...")
            response = requests.get(api_url)
            data = response.json()
            
            # Find the latest stable version
            for version_info in reversed(data['versions']):
                if version_info['version'].startswith(version):
                    downloads = version_info.get('downloads', {})
                    chromedriver_downloads = downloads.get('chromedriver', [])
                    
                    for download in chromedriver_downloads:
                        if platform.system().lower() in download['platform']:
                            download_url = download['url']
                            break
                    else:
                        continue
                    break
            else:
                print(f"No ChromeDriver found for Chrome {version}")
                return False
        else:
            # Use legacy API for older versions
            download_url = f"{base_url}/{version}/chromedriver_{platform.system().lower()}.zip"
            
        print(f"Downloading ChromeDriver from: {download_url}")
        
        # Download ChromeDriver
        response = requests.get(download_url)
        response.raise_for_status()
        
        # Save and extract
        driver_dir = Path("drivers")
        driver_dir.mkdir(exist_ok=True)
        
        zip_path = driver_dir / "chromedriver.zip"
        with open(zip_path, 'wb') as f:
            f.write(response.content)
            
        # Extract
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(driver_dir)
            
        # Make executable on Unix systems
        if platform.system() != "Windows":
            chromedriver_path = driver_dir / "chromedriver"
            os.chmod(chromedriver_path, 0o755)
            
        # Clean up
        zip_path.unlink()
        
        print(f"ChromeDriver installed successfully in: {driver_dir.absolute()}")
        return True
        
    except Exception as e:
        print(f"Error downloading ChromeDriver: {e}")
        return False

def check_chromedriver():
    """Check if ChromeDriver is available"""
    try:
        result = subprocess.run(['chromedriver', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("ChromeDriver is already available in PATH")
            print(result.stdout.strip())
            return True
    except:
        pass
        
    # Check local drivers directory
    driver_path = Path("drivers") / ("chromedriver.exe" if platform.system() == "Windows" else "chromedriver")
    if driver_path.exists():
        print(f"ChromeDriver found locally: {driver_path.absolute()}")
        return True
        
    return False

def main():
    """Main setup function"""
    print("Pinterest Auto-Publisher - ChromeDriver Setup")
    print("=" * 50)
    
    # Check if ChromeDriver is already available
    if check_chromedriver():
        print("✅ ChromeDriver is ready!")
        return
        
    print("ChromeDriver not found. Setting up...")
    
    # Get Chrome version
    chrome_version = get_chrome_version()
    if not chrome_version:
        print("❌ Could not detect Chrome version.")
        print("Please install Google Chrome or manually download ChromeDriver.")
        return
        
    print(f"Detected Chrome version: {chrome_version}")
    
    # Download ChromeDriver
    if download_chromedriver(chrome_version):
        print("✅ ChromeDriver setup complete!")
        print("\nTo use the local ChromeDriver, make sure to update the path in pinterest_automation.py")
    else:
        print("❌ Failed to setup ChromeDriver.")
        print("Please manually download ChromeDriver from: https://chromedriver.chromium.org/")

if __name__ == "__main__":
    main()
