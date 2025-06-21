#!/usr/bin/env python3
"""
Chrome Setup Script for Pinterest Automation Bot
Downloads and installs Chrome and ChromeDriver based on chrome_config.json
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError
import stat


class ChromeSetup:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.config_path = self.root_dir / "chrome_config.json"
        self.config = self._load_config()
        self.temp_dir = None
        
    def _load_config(self):
        """Load Chrome configuration"""
        if not self.config_path.exists():
            print("❌ Chrome configuration file not found: chrome_config.json")
            sys.exit(1)
            
        with open(self.config_path) as f:
            config = json.load(f)
            
        print(f"📋 Loaded configuration for Chrome {config['version']} on {config['platform']}")
        return config
    
    def _create_temp_dir(self):
        """Create temporary directory for downloads"""
        self.temp_dir = tempfile.mkdtemp(prefix="chrome_setup_")
        print(f"📁 Created temporary directory: {self.temp_dir}")
        
    def _cleanup_temp_dir(self):
        """Remove temporary directory and its contents"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Cleaned up temporary directory: {self.temp_dir}")
    
    def _download_file(self, url, filename):
        """Download file with progress indication"""
        filepath = os.path.join(self.temp_dir, filename)
        
        try:
            print(f"⬇️  Downloading {filename}...")
            print(f"   URL: {url}")
            
            # Create request with user agent to avoid blocking
            request = Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            with urlopen(request) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                
                with open(filepath, 'wb') as f:
                    downloaded = 0
                    chunk_size = 8192
                    
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r   Progress: {percent:.1f}% ({downloaded:,} / {total_size:,} bytes)", end='', flush=True)
                    
                    print()  # New line after progress
            
            print(f"✅ Downloaded {filename} successfully")
            return filepath
            
        except URLError as e:
            print(f"❌ Failed to download {filename}: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error downloading {filename}: {e}")
            return None
    
    def _extract_archive(self, archive_path, extract_to):
        """Extract archive file"""
        try:
            print(f"📦 Extracting {os.path.basename(archive_path)}...")
            
            if archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
            elif archive_path.endswith(('.tar.gz', '.tgz')):
                import tarfile
                with tarfile.open(archive_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(extract_to)
            else:
                print(f"❌ Unsupported archive format: {archive_path}")
                return False
                
            print(f"✅ Extracted successfully to {extract_to}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to extract {archive_path}: {e}")
            return False
    
    def _make_executable(self, filepath):
        """Make file executable on Unix systems"""
        if os.name != 'nt':  # Not Windows
            try:
                current_permissions = os.stat(filepath).st_mode
                os.chmod(filepath, current_permissions | stat.S_IEXEC)
                print(f"✅ Made {filepath} executable")
            except Exception as e:
                print(f"⚠️  Warning: Could not make {filepath} executable: {e}")
    
    def setup_chrome(self):
        """Download and setup Chrome browser"""
        print("🌐 Setting up Chrome browser...")
        
        chrome_dir = self.root_dir / "chrome_portable"
        chrome_dir.mkdir(exist_ok=True)
        
        platform = self.config['platform']
        version = self.config['version']
        
        if platform == 'linux':
            # For Linux, we'll download Chrome for Testing
            chrome_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/linux64/chrome-linux64.zip"
            chrome_filename = "chrome-linux64.zip"
            
        elif platform == 'windows':
            chrome_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/win64/chrome-win64.zip"
            chrome_filename = "chrome-win64.zip"
            
        elif platform == 'mac':
            chrome_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/mac-x64/chrome-mac-x64.zip"
            chrome_filename = "chrome-mac-x64.zip"
            
        else:
            print(f"❌ Unsupported platform: {platform}")
            return False
        
        # Download Chrome
        chrome_archive = self._download_file(chrome_url, chrome_filename)
        if not chrome_archive:
            return False
        
        # Extract Chrome to temporary location first
        temp_extract_dir = os.path.join(self.temp_dir, "chrome_extract")
        if not self._extract_archive(chrome_archive, temp_extract_dir):
            return False
        
        # Find the extracted directory and move its contents to chrome_portable
        extracted_dirs = [d for d in Path(temp_extract_dir).iterdir() if d.is_dir()]
        if extracted_dirs:
            chrome_extracted_dir = extracted_dirs[0]
            
            # Move all contents from extracted directory to chrome_portable
            print(f"📂 Moving Chrome files from {chrome_extracted_dir} to {chrome_dir}")
            for item in chrome_extracted_dir.iterdir():
                dest_path = chrome_dir / item.name
                if dest_path.exists():
                    if dest_path.is_dir():
                        shutil.rmtree(dest_path)
                    else:
                        dest_path.unlink()
                shutil.move(str(item), str(dest_path))
            
            # Set up Chrome binary path
            if platform == 'linux':
                chrome_binary = chrome_dir / "chrome"
            elif platform == 'windows':
                chrome_binary = chrome_dir / "chrome.exe"
            elif platform == 'mac':
                chrome_binary = chrome_dir / "Google Chrome for Testing.app" / "Contents" / "MacOS" / "Google Chrome for Testing"
            
            if chrome_binary.exists():
                # Make Chrome executable
                self._make_executable(str(chrome_binary))
                
                # Update the config path to point to the actual binary
                relative_path = chrome_binary.relative_to(self.root_dir)
                self.config['chrome_binary'] = str(relative_path)
                
                print(f"✅ Chrome browser setup complete: {relative_path}")
                return True
            else:
                print(f"❌ Chrome binary not found at expected location: {chrome_binary}")
                return False
        else:
            print("❌ No extracted Chrome directory found")
            return False
    
    def setup_chromedriver(self):
        """Download and setup ChromeDriver"""
        print("🚗 Setting up ChromeDriver...")
        
        drivers_dir = self.root_dir / "drivers"
        drivers_dir.mkdir(exist_ok=True)
        
        platform = self.config['platform']
        version = self.config['version']
        
        if platform == 'linux':
            driver_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/linux64/chromedriver-linux64.zip"
            driver_filename = "chromedriver-linux64.zip"
            driver_binary_name = "chromedriver"
            
        elif platform == 'windows':
            driver_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/win64/chromedriver-win64.zip"
            driver_filename = "chromedriver-win64.zip"
            driver_binary_name = "chromedriver.exe"
            
        elif platform == 'mac':
            driver_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/mac-x64/chromedriver-mac-x64.zip"
            driver_filename = "chromedriver-mac-x64.zip"
            driver_binary_name = "chromedriver"
            
        else:
            print(f"❌ Unsupported platform: {platform}")
            return False
        
        # Download ChromeDriver
        driver_archive = self._download_file(driver_url, driver_filename)
        if not driver_archive:
            return False
        
        # Extract ChromeDriver to temporary location first
        temp_extract_dir = os.path.join(self.temp_dir, "chromedriver_extract")
        if not self._extract_archive(driver_archive, temp_extract_dir):
            return False
        
        # Find the extracted directory and move ChromeDriver to drivers directory
        extracted_dirs = [d for d in Path(temp_extract_dir).iterdir() if d.is_dir()]
        if extracted_dirs:
            driver_extracted_dir = extracted_dirs[0]
            driver_binary = driver_extracted_dir / driver_binary_name
            
            if driver_binary.exists():
                # Move ChromeDriver to drivers directory root
                final_driver_path = drivers_dir / driver_binary_name
                if final_driver_path.exists():
                    final_driver_path.unlink()
                
                shutil.move(str(driver_binary), str(final_driver_path))
                
                # Make ChromeDriver executable
                self._make_executable(str(final_driver_path))
                
                # Update config path
                relative_path = final_driver_path.relative_to(self.root_dir)
                self.config['chromedriver_path'] = str(relative_path)
                
                print(f"✅ ChromeDriver setup complete: {relative_path}")
                return True
            else:
                print(f"❌ ChromeDriver binary not found at expected location: {driver_binary}")
                return False
        else:
            print("❌ No extracted ChromeDriver directory found")
            return False
    
    def update_config(self):
        """Update chrome_config.json with new setup information"""
        try:
            self.config['setup_date'] = str(time.time())
            
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            print(f"✅ Updated configuration file: {self.config_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update configuration: {e}")
            return False
    
    def verify_installation(self):
        """Verify that Chrome and ChromeDriver are properly installed"""
        print("🔍 Verifying installation...")
        
        chrome_binary = self.root_dir / self.config['chrome_binary']
        chromedriver_binary = self.root_dir / self.config['chromedriver_path']
        
        success = True
        
        if chrome_binary.exists():
            print(f"✅ Chrome binary found: {chrome_binary}")
        else:
            print(f"❌ Chrome binary not found: {chrome_binary}")
            success = False
        
        if chromedriver_binary.exists():
            print(f"✅ ChromeDriver binary found: {chromedriver_binary}")
        else:
            print(f"❌ ChromeDriver binary not found: {chromedriver_binary}")
            success = False
        
        # Test ChromeDriver version
        if chromedriver_binary.exists():
            try:
                result = subprocess.run([str(chromedriver_binary), '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"✅ ChromeDriver version: {result.stdout.strip()}")
                else:
                    print(f"⚠️  ChromeDriver version check failed: {result.stderr}")
            except Exception as e:
                print(f"⚠️  Could not check ChromeDriver version: {e}")
        
        return success
    
    def run_setup(self):
        """Run the complete setup process"""
        print("🚀 Starting Chrome and ChromeDriver setup...")
        print("=" * 50)
        
        try:
            # Create temporary directory
            self._create_temp_dir()
            
            # Setup Chrome
            if not self.setup_chrome():
                print("❌ Chrome setup failed")
                return False
            
            # Setup ChromeDriver
            if not self.setup_chromedriver():
                print("❌ ChromeDriver setup failed")
                return False
            
            # Update configuration
            if not self.update_config():
                print("❌ Configuration update failed")
                return False
            
            # Verify installation
            if not self.verify_installation():
                print("❌ Installation verification failed")
                return False
            
            print("=" * 50)
            print("🎉 Chrome and ChromeDriver setup completed successfully!")
            print(f"   Chrome: {self.config['chrome_binary']}")
            print(f"   ChromeDriver: {self.config['chromedriver_path']}")
            print(f"   Version: {self.config['version']}")
            print(f"   Platform: {self.config['platform']}")
            
            return True
            
        except KeyboardInterrupt:
            print("\n⚠️  Setup interrupted by user")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during setup: {e}")
            return False
        finally:
            # Always cleanup temporary files
            self._cleanup_temp_dir()


def main():
    """Main function"""
    print("Chrome Setup for Pinterest Automation Bot")
    print("=========================================")
    
    try:
        setup = ChromeSetup()
        success = setup.run_setup()
        
        if success:
            print("\n✅ Setup completed successfully!")
            print("You can now run the Pinterest automation bot.")
            sys.exit(0)
        else:
            print("\n❌ Setup failed!")
            print("Please check the error messages above and try again.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
