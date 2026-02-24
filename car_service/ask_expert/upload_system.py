"""
Modern File Upload System for Ask Expert
Supports: File picker, Camera, Drag & Drop, Mobile compatibility
"""

import os
import base64
import mimetypes
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image, ExifTags
import io

class ModernUploadSystem:
    """Modern upload system with file picker, camera, and drag & drop support"""
    
    ALLOWED_EXTENSIONS = {
        'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'heic', 'heif'],
        'document': ['pdf', 'doc', 'docx', 'txt'],
        'video': ['mp4', 'mov', 'avi', 'mkv']
    }
    
    MAX_FILE_SIZE = {
        'image': 10 * 1024 * 1024,  # 10MB
        'document': 5 * 1024 * 1024,  # 5MB
        'video': 50 * 1024 * 1024    # 50MB
    }
    
    def __init__(self, upload_dir):
        self.upload_dir = upload_dir
        self.ensure_upload_structure()
    
    def ensure_upload_structure(self):
        """Create organized upload directories"""
        dirs = [
            'temp',           # Temporary uploads
            'pending',        # Pending approval
            'approved',       # Approved files
            'rejected',       # Rejected files
            'camera',         # Camera captures
            'mobile'          # Mobile uploads
        ]
        
        for dir_name in dirs:
            dir_path = os.path.join(self.upload_dir, dir_name)
            os.makedirs(dir_path, exist_ok=True)
    
    def validate_file(self, file, file_type='image'):
        """Validate uploaded file"""
        if not file or not file.filename:
            return False, "No file selected"
        
        # Check file extension
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if ext not in self.ALLOWED_EXTENSIONS.get(file_type, []):
            return False, f"File type .{ext} not allowed"
        
        # Check file size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        
        max_size = self.MAX_FILE_SIZE.get(file_type, 10 * 1024 * 1024)
        if size > max_size:
            return False, f"File too large. Max size: {max_size // (1024*1024)}MB"
        
        return True, "File valid"
    
    def process_uploaded_file(self, file, request_id, source='web'):
        """Process uploaded file from any source"""
        try:
            # Validate file
            is_valid, message = self.validate_file(file)
            if not is_valid:
                return False, message
            
            # Generate unique filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            original_name = secure_filename(file.filename)
            filename = f"{timestamp}_{source}_{original_name}"
            
            # Determine upload path
            if source == 'camera':
                upload_path = os.path.join(self.upload_dir, 'camera', f'req_{request_id}')
            elif source == 'mobile':
                upload_path = os.path.join(self.upload_dir, 'mobile', f'req_{request_id}')
            else:
                upload_path = os.path.join(self.upload_dir, 'pending', f'req_{request_id}')
            
            os.makedirs(upload_path, exist_ok=True)
            file_path = os.path.join(upload_path, filename)
            
            # Save file
            file.save(file_path)
            
            # Process image if needed
            if self.is_image_file(filename):
                self.process_image(file_path)
            
            return True, {
                'filename': filename,
                'path': file_path,
                'size': os.path.getsize(file_path),
                'source': source,
                'request_id': request_id
            }
            
        except Exception as e:
            return False, f"Upload failed: {str(e)}"
    
    def is_image_file(self, filename):
        """Check if file is an image"""
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        return ext in self.ALLOWED_EXTENSIONS['image']
    
    def process_image(self, file_path):
        """Process uploaded image (optimize, rotate, etc.)"""
        try:
            with Image.open(file_path) as img:
                # Fix orientation based on EXIF data
                if hasattr(img, '_getexif'):
                    exif = img._getexif()
                    if exif is not None:
                        for tag, value in exif.items():
                            if tag in ExifTags.TAGS and ExifTags.TAGS[tag] == 'Orientation':
                                if value == 3:
                                    img = img.rotate(180, expand=True)
                                elif value == 6:
                                    img = img.rotate(270, expand=True)
                                elif value == 8:
                                    img = img.rotate(90, expand=True)
                                break
                
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Optimize image (resize if too large)
                max_size = (1920, 1080)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save optimized image
                img.save(file_path, 'JPEG', quality=85, optimize=True)
                
        except Exception as e:
            print(f"Image processing failed: {e}")
    
    def handle_camera_capture(self, image_data, request_id):
        """Handle camera capture from web/mobile"""
        try:
            # Decode base64 image data
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
            
            image_bytes = base64.b64decode(image_data)
            
            # Create PIL Image
            img = Image.open(io.BytesIO(image_bytes))
            
            # Generate filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_camera_capture.jpg"
            
            # Save to camera directory
            camera_dir = os.path.join(self.upload_dir, 'camera', f'req_{request_id}')
            os.makedirs(camera_dir, exist_ok=True)
            file_path = os.path.join(camera_dir, filename)
            
            # Process and save
            img.save(file_path, 'JPEG', quality=85, optimize=True)
            
            return True, {
                'filename': filename,
                'path': file_path,
                'size': os.path.getsize(file_path),
                'source': 'camera',
                'request_id': request_id
            }
            
        except Exception as e:
            return False, f"Camera capture failed: {str(e)}"
    
    def handle_drag_drop(self, files, request_id):
        """Handle drag and drop files"""
        results = []
        
        for file in files:
            success, result = self.process_uploaded_file(file, request_id, 'drag_drop')
            results.append({
                'filename': file.filename,
                'success': success,
                'result': result
            })
        
        return results
    
    def get_file_info(self, file_path):
        """Get detailed file information"""
        try:
            stat = os.stat(file_path)
            filename = os.path.basename(file_path)
            
            info = {
                'filename': filename,
                'size': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'type': mimetypes.guess_type(filename)[0] or 'unknown'
            }
            
            # Additional image info
            if self.is_image_file(filename):
                try:
                    with Image.open(file_path) as img:
                        info.update({
                            'width': img.width,
                            'height': img.height,
                            'format': img.format,
                            'mode': img.mode
                        })
                except:
                    pass
            
            return info
            
        except Exception as e:
            return {'error': str(e)}
    
    def create_thumbnail(self, file_path, size=(150, 150)):
        """Create thumbnail for images"""
        try:
            if not self.is_image_file(file_path):
                return None
            
            with Image.open(file_path) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Create thumbnail filename
                filename = os.path.basename(file_path)
                name, ext = os.path.splitext(filename)
                thumb_filename = f"{name}_thumb{ext}"
                thumb_path = os.path.join(os.path.dirname(file_path), thumb_filename)
                
                # Save thumbnail
                img.save(thumb_path, 'JPEG', quality=70)
                
                return thumb_path
                
        except Exception as e:
            print(f"Thumbnail creation failed: {e}")
            return None


# Flask route integration
def create_upload_routes(app, upload_system):
    """Create Flask routes for modern upload system"""
    
    @app.route('/upload/file-picker', methods=['POST'])
    def handle_file_picker():
        """Handle file picker upload"""
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        request_id = request.form.get('request_id')
        
        success, result = upload_system.process_uploaded_file(file, request_id, 'file_picker')
        
        if success:
            return jsonify({
                'success': True,
                'file_info': result
            })
        else:
            return jsonify({'error': result}), 400
    
    @app.route('/upload/camera', methods=['POST'])
    def handle_camera_upload():
        """Handle camera capture"""
        image_data = request.json.get('image_data')
        request_id = request.json.get('request_id')
        
        success, result = upload_system.handle_camera_capture(image_data, request_id)
        
        if success:
            return jsonify({
                'success': True,
                'file_info': result
            })
        else:
            return jsonify({'error': result}), 400
    
    @app.route('/upload/drag-drop', methods=['POST'])
    def handle_drag_drop():
        """Handle drag and drop upload"""
        files = request.files.getlist('files')
        request_id = request.form.get('request_id')
        
        results = upload_system.handle_drag_drop(files, request_id)
        
        return jsonify({
            'success': True,
            'results': results
        })
    
    @app.route('/upload/mobile', methods=['POST'])
    def handle_mobile_upload():
        """Handle mobile app upload"""
        file = request.files.get('file')
        request_id = request.form.get('request_id')
        metadata = request.form.get('metadata', '{}')
        
        success, result = upload_system.process_uploaded_file(file, request_id, 'mobile')
        
        if success:
            return jsonify({
                'success': True,
                'file_info': result,
                'metadata': metadata
            })
        else:
            return jsonify({'error': result}), 400
