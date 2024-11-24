import os
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import json
import hashlib
from typing import Optional, Dict, Any
import logging

class SecurityService:
    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.key)
        self.retention_period = timedelta(days=30)  # Default 30 days retention
        self.consent_store = {}  # Store user consent status
        self._setup_logging()

    def _setup_logging(self):
        """Setup security audit logging"""
        logging.basicConfig(
            filename='security_audit.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('security_service')

    def _get_or_create_key(self) -> bytes:
        """Get existing or create new encryption key"""
        key_file = "encryption.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key

    def encrypt_audio_data(self, audio_data: bytes) -> bytes:
        """Encrypt audio data before storage"""
        try:
            return self.cipher_suite.encrypt(audio_data)
        except Exception as e:
            self.logger.error(f"Encryption error: {str(e)}")
            raise

    def decrypt_audio_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt audio data for processing"""
        try:
            return self.cipher_suite.decrypt(encrypted_data)
        except Exception as e:
            self.logger.error(f"Decryption error: {str(e)}")
            raise

    def hash_audio_data(self, audio_data: bytes) -> str:
        """Create hash of audio data for integrity verification"""
        return hashlib.sha256(audio_data).hexdigest()

    def verify_audio_integrity(self, audio_data: bytes, stored_hash: str) -> bool:
        """Verify audio data integrity"""
        return self.hash_audio_data(audio_data) == stored_hash

    def set_user_consent(self, user_id: str, consent_data: Dict[str, bool]):
        """Store user's privacy preferences"""
        self.consent_store[user_id] = {
            'preferences': consent_data,
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0'
        }
        self.logger.info(f"Updated consent preferences for user {user_id}")

    def get_user_consent(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's privacy preferences"""
        return self.consent_store.get(user_id)

    def should_retain_data(self, creation_date: datetime) -> bool:
        """Check if data should be retained based on retention policy"""
        return datetime.utcnow() - creation_date <= self.retention_period

    def anonymize_transcript(self, transcript: str) -> str:
        """Anonymize sensitive information in transcript"""
        # TODO: Implement more sophisticated anonymization
        sensitive_patterns = [
            (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]'),  # Phone numbers
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),  # Email
            (r'\b\d{16}\b', '[CARD_NUMBER]'),  # Credit card numbers
        ]
        
        anonymized = transcript
        for pattern, replacement in sensitive_patterns:
            anonymized = re.sub(pattern, replacement, anonymized)
        return anonymized

    def create_audit_log(self, action: str, user_id: str, details: Dict[str, Any]):
        """Create security audit log entry"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'action': action,
            'user_id': user_id,
            'details': details
        }
        self.logger.info(json.dumps(log_entry))

    def validate_audio_source(self, source_info: Dict[str, Any]) -> bool:
        """Validate audio source information"""
        required_fields = ['device_id', 'user_id', 'timestamp']
        return all(field in source_info for field in required_fields)

    def sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize metadata before storage"""
        # Remove sensitive fields
        sensitive_fields = ['ip_address', 'raw_device_info', 'location']
        return {k: v for k, v in metadata.items() if k not in sensitive_fields}

    def generate_secure_filename(self, original_filename: str) -> str:
        """Generate secure filename for audio storage"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        random_suffix = os.urandom(4).hex()
        return f"audio_{timestamp}_{random_suffix}.wav"
