"""
Document Upload Service for Car Service Workers
Handles role-specific document uploads with validation
"""

import os
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
import mimetypes

class DocumentService:
    """Service for handling worker document uploads"""
    
    # Document requirements by worker type
    DOCUMENT_REQUIREMENTS = {
        'MECHANIC': {
            'aadhaar_id': {'required': True, 'max_size': 5 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png', '.pdf']},
            'driving_license': {'required': True, 'max_size': 5 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png', '.pdf']},
            'experience_proof': {'required': True, 'max_size': 5 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png', '.pdf']},
            'garage_photo': {'required': True, 'max_size': 10 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png']},
            'skills': {'required': False, 'max_size': 0, 'extensions': [], 'type': 'text'},
            'bank_upi': {'required': True, 'max_size': 2 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png', '.pdf']}
        },
        'FUEL_AGENT': {
            'aadhaar_id': {'required': True, 'max_size': 5 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png', '.pdf']},
            'driving_license': {'required': True, 'max_size': 5 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png', '.pdf']},
            'vehicle_rc': {'required': True, 'max_size': 5 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png', '.pdf']},
            'vehicle_insurance': {'required': True, 'max_size': 5 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png', '.pdf']},
            'vehicle_photo': {'required': True, 'max_size': 10 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png']}
        },
        'TOW_TRUCK': {
            'aadhaar_id': {'required': True, 'max_size': 5 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png', '.pdf']},
            'pan_card': {'required': True, 'max_size': 5 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png', '.pdf']},
            'driving_license': {'required': True, 'max_size': 5 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png', '.pdf']},
            'vehicle_rc': {'required': True, 'max_size': 5 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png', '.pdf']},
            'insurance': {'required': True, 'max_size': 5 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png', '.pdf']},
            'fitness_certificate': {'required': True, 'max_size': 5 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png', '.pdf']},
            'truck_front': {'required': True, 'max_size': 10 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png']},
            'truck_side': {'required': True, 'max_size': 10 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png']},
            'truck_number_plate': {'required': True, 'max_size': 5 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png', '.pdf']}
        },
        'EXPERT': {
            'aadhaar_id': {'required': True, 'max_size': 5 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png', '.pdf']},
            'experience_proof': {'required': True, 'max_size': 5 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg', '.png', '.pdf']},
            'specialization': {'required': False, 'max_size': 0, 'extensions': [], 'type': 'text'},
            'years_experience': {'required': False, 'max_size': 0, 'extensions': [], 'type': 'number'}
        }
    }
    
    def __init__(self, upload_dir: str = None):
        if upload_dir is None:
            # Default to worker_docs in project root
            self.upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "worker_docs")
        else:
            self.upload_dir = upload_dir
        
        self.ensure_upload_structure()
    
    def ensure_upload_structure(self):
        """Create upload directory structure"""
        # Create main upload directory
        os.makedirs(self.upload_dir, exist_ok=True)
        
        # Create subdirectories by worker type
        for worker_type in ['MECHANIC', 'FUEL_AGENT', 'EXPERT']:
            type_dir = os.path.join(self.upload_dir, worker_type.lower())
            os.makedirs(type_dir, exist_ok=True)
    
    def validate_document(self, file, doc_type: str, worker_type: str) -> tuple[bool, str]:
        """Validate uploaded document against requirements"""
        if worker_type not in self.DOCUMENT_REQUIREMENTS:
            return False, f"Invalid worker type: {worker_type}"
        
        requirements = self.DOCUMENT_REQUIREMENTS[worker_type].get(doc_type, {})
        
        # Check if document type is valid for this worker type
        if not requirements:
            return False, f"Document type '{doc_type}' not required for {worker_type}"
        
        # Check file extension
        if file and file.filename:
            filename = secure_filename(file.filename)
            ext = os.path.splitext(filename)[1].lower()
            
            if ext not in requirements['extensions']:
                return False, f"Invalid file type: {ext}. Allowed: {', '.join(requirements['extensions'])}"
        
        # Check file size
        if file and hasattr(file, 'content_length'):
            if file.content_length > requirements['max_size']:
                max_mb = requirements['max_size'] / (1024 * 1024)
                return False, f"File too large. Max size: {max_mb}MB"
        
        return True, "Valid"
    
    def process_document_upload(self, files_dict: dict, worker_type: str, worker_id: int) -> dict:
        """Process document uploads for a worker"""
        documents = {}
        errors = []
        
        # Get requirements for this worker type
        requirements = self.DOCUMENT_REQUIREMENTS.get(worker_type, {})
        
        # Create worker-specific directory
        worker_dir = os.path.join(self.upload_dir, worker_type.lower(), str(worker_id))
        os.makedirs(worker_dir, exist_ok=True)
        
        # Process each document type
        for doc_type, file_list in files_dict.items():
            if doc_type not in requirements:
                errors.append(f"Invalid document type: {doc_type}")
                continue
            
            # Handle multiple files (take first one)
            if isinstance(file_list, list) and file_list:
                file = file_list[0]
            elif hasattr(file_list, 'filename'):
                file = file_list
            else:
                # Text field (skills, specialization, years_experience)
                if doc_type in ['skills', 'specialization', 'years_experience']:
                    documents[doc_type] = str(file_list) if file_list else ""
                    continue
                else:
                    errors.append(f"No file provided for {doc_type}")
                    continue
            
            # Validate file
            is_valid, message = self.validate_document(file, doc_type, worker_type)
            if not is_valid:
                errors.append(f"{doc_type}: {message}")
                continue
            
            # Save file
            try:
                filename = secure_filename(file.filename)
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                saved_filename = f"{timestamp}_{doc_type}_{filename}"
                file_path = os.path.join(worker_dir, saved_filename)
                
                file.save(file_path)
                
                # Process image if needed
                if self.is_image_file(filename):
                    self.process_image(file_path)
                
                documents[doc_type] = saved_filename
                
            except Exception as e:
                errors.append(f"Failed to save {doc_type}: {str(e)}")
        
        # Check required documents
        for doc_type, req in requirements.items():
            if req.get('required', False) and doc_type not in documents:
                errors.append(f"Required document missing: {doc_type}")
        
        return {
            'success': len(errors) == 0,
            'documents': documents,
            'errors': errors,
            'worker_dir': worker_dir
        }
    
    def is_image_file(self, filename: str) -> bool:
        """Check if file is an image"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    
    def process_image(self, file_path: str):
        """Process uploaded image (optimize, resize)"""
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if too large
                max_size = (1920, 1080)
                if img.width > max_size[0] or img.height > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save optimized image
                img.save(file_path, 'JPEG', quality=85, optimize=True)
                
        except Exception as e:
            print(f"Image processing failed: {e}")
    
    def get_worker_documents(self, worker_id: int, worker_type: str) -> dict:
        """Get all documents for a worker"""
        worker_dir = os.path.join(self.upload_dir, worker_type.lower(), str(worker_id))
        
        if not os.path.exists(worker_dir):
            return {}
        
        documents = {}
        for filename in os.listdir(worker_dir):
            file_path = os.path.join(worker_dir, filename)
            if os.path.isfile(file_path):
                # Extract document type from filename
                parts = filename.split('_', 2)
                if len(parts) >= 3:
                    doc_type = parts[1]
                    documents[doc_type] = filename
        
        return documents
    
    def delete_worker_documents(self, worker_id: int, worker_type: str) -> bool:
        """Delete all documents for a worker"""
        worker_dir = os.path.join(self.upload_dir, worker_type.lower(), str(worker_id))
        
        try:
            if os.path.exists(worker_dir):
                shutil.rmtree(worker_dir)
            return True
        except Exception as e:
            print(f"Failed to delete documents: {e}")
            return False
    
    def get_document_info(self, worker_id: int, worker_type: str, doc_type: str) -> dict:
        """Get information about a specific document"""
        documents = self.get_worker_documents(worker_id, worker_type)
        filename = documents.get(doc_type)
        
        if not filename:
            return {'error': 'Document not found'}
        
        file_path = os.path.join(self.upload_dir, worker_type.lower(), str(worker_id), filename)
        
        if not os.path.exists(file_path):
            return {'error': 'File not found'}
        
        stat = os.stat(file_path)
        return {
            'filename': filename,
            'path': file_path,
            'size': stat.st_size,
            'size_mb': stat.st_size / (1024 * 1024),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'type': mimetypes.guess_type(filename)[0] or 'unknown'
        }


# Global instance
document_service = DocumentService()
