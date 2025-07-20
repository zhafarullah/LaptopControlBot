# modules/file_manager/operations.py
import os
import string
import shutil
import psutil
import logging
from pathlib import Path
from ctypes import windll
from modules.utils.helpers import format_size, format_time

class FileOperations:
    """Core file operations untuk file manager"""
    
    DEFAULT_PATH = "root"  # Special value untuk root (drive selection)
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_available_drives(self):
        """Get list of available drives on Windows"""
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drives.append(f"{letter}:")
            bitmask >>= 1
        return drives
    
    def list_directory_content(self, path):
        """List directory contents dengan informasi detail"""
        try:
            # Special case untuk root listing
            if path == self.DEFAULT_PATH or path == "root":
                drives = self.get_available_drives()
                content = {
                    'type': 'drives',
                    'drives': [],
                    'current_path': path
                }
                
                for drive in drives:
                    try:
                        usage = psutil.disk_usage(drive)
                        free_space = format_size(usage.free)
                        total_space = format_size(usage.total)
                        content['drives'].append({
                            'name': drive,
                            'free_space': free_space,
                            'total_space': total_space,
                            'accessible': True
                        })
                    except:
                        content['drives'].append({
                            'name': drive,
                            'free_space': 'N/A',
                            'total_space': 'N/A',
                            'accessible': False
                        })
                
                return content
            
            # Normal directory listing
            if not os.path.exists(path):
                raise FileNotFoundError(f"Path does not exist: {path}")
            
            items = []
            
            # Add parent directory if not in root
            if os.path.dirname(path) != path:
                items.append({
                    'name': '..',
                    'type': 'parent',
                    'display': '📂 .. (Parent Directory)'
                })
            
            # List directories and files
            dirs = []
            files = []
            
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                try:
                    stats = os.stat(item_path)
                    
                    if os.path.isdir(item_path):
                        dirs.append({
                            'name': item,
                            'type': 'directory',
                            'display': f"📁 {item}/",
                            'path': item_path
                        })
                    else:
                        size = format_size(stats.st_size)
                        modified = format_time(stats.st_mtime)
                        files.append({
                            'name': item,
                            'type': 'file',
                            'display': f"📄 {item} ({size}, {modified})",
                            'path': item_path,
                            'size': stats.st_size
                        })
                except PermissionError:
                    dirs.append({
                        'name': item,
                        'type': 'directory',
                        'display': f"🚫 {item}/ (Access Denied)",
                        'path': item_path
                    })
                except Exception as e:
                    self.logger.error(f"Error accessing {item_path}: {str(e)}")
            
            # Combine lists
            items.extend(dirs)
            items.extend(files)
            
            return {
                'type': 'directory',
                'items': items,
                'current_path': path,
                'total_items': len(items)
            }
            
        except PermissionError:
            raise PermissionError("Access Denied: You don't have permission to access this location")
        except Exception as e:
            self.logger.error(f"Error in list_directory_content: {str(e)}")
            raise
    
    def change_directory(self, current_path, new_path):
        """Change directory dan return new path"""
        self.logger.info(f"Changing directory from {current_path} to {new_path}")
        
        # Back to root
        if new_path == "\\" or new_path == "/":
            return self.DEFAULT_PATH
        
        # Handle drive letter changes (Windows)
        if os.name == 'nt' and len(new_path) >= 2 and new_path[1] == ':':
            drive = new_path[0].upper() + ':'
            if drive in self.get_available_drives():
                try:
                    drive_path = drive + "\\"
                    os.listdir(drive_path)  # Test access
                    return drive_path
                except PermissionError:
                    raise PermissionError(f"Access Denied: You don't have permission to access drive {drive}")
                except Exception as e:
                    raise Exception(f"Cannot access drive {drive}: {str(e)}")
            else:
                raise FileNotFoundError(f"Drive {drive} is not available")
        
        # Handle parent directory
        if new_path == "..":
            if current_path == self.DEFAULT_PATH:
                return self.DEFAULT_PATH
            if len(current_path) <= 3:  # e.g., "C:\"
                return self.DEFAULT_PATH
            return os.path.dirname(current_path)
        
        # Handle absolute and relative paths
        if os.path.isabs(new_path):
            resolved_path = os.path.abspath(new_path)
        else:
            if current_path == self.DEFAULT_PATH:
                raise ValueError("Please select a drive first")
            resolved_path = os.path.join(current_path, new_path)
        
        # Validate path
        if os.path.exists(resolved_path) and os.path.isdir(resolved_path):
            try:
                os.listdir(resolved_path)  # Test access
                return resolved_path
            except PermissionError:
                raise PermissionError("Access Denied: You don't have permission to access this location")
        else:
            raise FileNotFoundError(f"Directory does not exist: {resolved_path}")
    
    def create_directory(self, current_path, dir_name):
        """Create new directory"""
        if current_path == self.DEFAULT_PATH:
            raise ValueError("Please select a drive first using /cd command")
        
        dir_path = os.path.join(current_path, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        return dir_path
    
    def delete_item(self, current_path, item_name):
        """Delete file or directory"""
        if current_path == self.DEFAULT_PATH:
            raise ValueError("Please select a drive first using /cd command")
        
        item_path = os.path.join(current_path, item_name)
        
        if not os.path.exists(item_path):
            raise FileNotFoundError("Item does not exist!")
        
        if os.path.isfile(item_path):
            os.remove(item_path)
            return f"File deleted: {item_name}"
        else:
            shutil.rmtree(item_path)
            return f"Directory deleted: {item_name}"
    
    def search_files(self, current_path, pattern, max_results=1000):
        """Search for files matching pattern"""
        if current_path == self.DEFAULT_PATH:
            raise ValueError("Please select a drive first using /cd command")
        
        results = []
        search_count = 0
        
        for root, dirs, files in os.walk(current_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for item in dirs + files:
                if pattern.lower() in item.lower():
                    rel_path = os.path.relpath(os.path.join(root, item), current_path)
                    if os.path.isdir(os.path.join(root, item)):
                        results.append({
                            'name': item,
                            'type': 'directory',
                            'path': rel_path,
                            'display': f"📁 {rel_path}/"
                        })
                    else:
                        try:
                            size = format_size(os.path.getsize(os.path.join(root, item)))
                            results.append({
                                'name': item,
                                'type': 'file',
                                'path': rel_path,
                                'display': f"📄 {rel_path} ({size})"
                            })
                        except:
                            results.append({
                                'name': item,
                                'type': 'file',
                                'path': rel_path,
                                'display': f"📄 {rel_path} (size unknown)"
                            })
                    
                    search_count += 1
                    if search_count >= max_results:
                        break
            
            if search_count >= max_results:
                break
        
        return {
            'results': results,
            'total_found': len(results),
            'search_limited': search_count >= max_results,
            'pattern': pattern
        }