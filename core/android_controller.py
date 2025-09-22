import subprocess
import time
import os
from typing import List, Optional


class AndroidController:
    """Manages Android device operations via ADB"""
    
    def __init__(self, target_device_id: Optional[str] = None):
        self.target_device_id = target_device_id
        self._establish_connection()
    
    def _establish_connection(self):
        """Establish connection to Android device via ADB"""
        try:
            cmd_result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, check=True)
            available_devices = [line.split()[0] for line in cmd_result.stdout.strip().split('\n')[1:]
                               if line.strip() and 'device' in line]

            if not available_devices:
                raise Exception("No Android devices detected. Please connect your device and enable USB debugging.")

            self.target_device_id = available_devices[0]

            # Verify UIAutomator functionality
            self._verify_uiautomator()

        except subprocess.CalledProcessError as e:
            raise Exception(f"ADB connection failed: {e}")

    def _verify_uiautomator(self):
        """Verify UIAutomator service is working"""
        try:
            test_result = self.run_adb_command(['shell', 'uiautomator', 'dump', '/sdcard/ui_test.xml'])
            if 'UI hierchary dumped' in test_result or 'dumped' in test_result.lower():
                pass
            else:
                print("UIAutomator service may have issues")
        except:
            print("UIAutomator verification failed")

    def run_adb_command(self, command_args: List[str], timeout_seconds: int = 15) -> str:
        """Execute ADB command and return output"""
        try:
            complete_command = ['adb', '-s', self.target_device_id] + command_args
            cmd_result = subprocess.run(complete_command, capture_output=True, text=True,
                                      check=True, timeout=timeout_seconds)
            return cmd_result.stdout.strip()
        except subprocess.TimeoutExpired:
            print(f"ADB command timed out: {' '.join(command_args)}")
            return ""
        except subprocess.CalledProcessError as e:
            return ""

    def capture_device_screenshot(self, output_path: str) -> bool:
        """Capture device screenshot with retry mechanism"""
        capture_successful = False
        for attempt_num in range(2):
            try:
                # Clean up any existing files
                self.run_adb_command(['shell', 'rm', '/sdcard/screenshot.png'])
                time.sleep(0.5)

                # Take screenshot
                screenshot_result = self.run_adb_command(['shell', 'screencap', '-p', '/sdcard/screenshot.png'], timeout_seconds=10)
                time.sleep(1)

                # Transfer screenshot to local
                transfer_result = self.run_adb_command(['pull', '/sdcard/screenshot.png', output_path], timeout_seconds=10)
                time.sleep(0.5)

                # Clean up device storage
                self.run_adb_command(['shell', 'rm', '/sdcard/screenshot.png'])

                # Verify file integrity
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                    capture_successful = True
                    break

            except Exception as e:
                print(f"Screenshot attempt {attempt_num + 1} failed: {e}")
                time.sleep(1)
        
        return capture_successful

    def capture_ui_hierarchy(self, output_path: str) -> bool:
        """Capture UI hierarchy dump with retry mechanism"""
        capture_successful = False
        for attempt_num in range(2):
            try:
                # Clean up any existing files
                self.run_adb_command(['shell', 'rm', '/sdcard/ui_dump.xml'])
                time.sleep(0.5)

                # Generate UI dump
                dump_result = self.run_adb_command(['shell', 'uiautomator', 'dump', '/sdcard/ui_dump.xml'],
                                                 timeout_seconds=15)
                time.sleep(1)

                # Transfer UI dump to local
                transfer_result = self.run_adb_command(['pull', '/sdcard/ui_dump.xml', output_path], timeout_seconds=10)
                time.sleep(0.5)

                # Clean up device storage
                self.run_adb_command(['shell', 'rm', '/sdcard/ui_dump.xml'])

                # Verify file exists
                if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
                    capture_successful = True
                    break

            except Exception as e:
                print(f"UI dump attempt {attempt_num + 1} failed: {e}")
                time.sleep(1)
        
        return capture_successful

    def perform_tap_action(self, x_coordinate: int, y_coordinate: int):
        """Execute tap action on device"""
        self.run_adb_command(['shell', 'input', 'tap', str(x_coordinate), str(y_coordinate)])
        time.sleep(2)

    def perform_text_input(self, input_text: str):
        """Execute text input with improved handling"""
        # Escape special characters for shell
        escaped_text = input_text.replace(' ', '%s').replace('&', '\\&').replace('(', '\\(').replace(')', '\\)')
        self.run_adb_command(['shell', 'input', 'text', escaped_text])
        time.sleep(2)

        # Send enter key
        self.run_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_ENTER'])
        time.sleep(2)

    def perform_scroll_action(self, scroll_direction: str = 'down'):
        """Execute scroll action on device"""
        if scroll_direction.lower() == 'up':
            self.run_adb_command(['shell', 'input', 'swipe', '500', '300', '500', '1000'])
        else:  # default down
            self.run_adb_command(['shell', 'input', 'swipe', '500', '1000', '500', '300'])
        time.sleep(2)

    def launch_application(self, app_package_name: str) -> bool:
        """Launch application by package name"""

        try:
            # Force stop application for clean start
            self.run_adb_command(['shell', 'am', 'force-stop', app_package_name])
            time.sleep(2)

            # Launch application
            launch_result = self.run_adb_command(['shell', 'monkey', '-p', app_package_name, '-c',
                                               'android.intent.category.LAUNCHER', '1'])
            time.sleep(5)  # Wait for app to load
            return True
        except Exception as e:
            print(f"Failed to launch application: {e}")
            return False 
