from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import json
import base64
from datetime import datetime
import hashlib

class CryptoManager:
    """
    Cryptographic Manager for Autonomous Cybersecurity System
    
    Features:
    1. AES-256 encryption for data at rest
    2. RSA-2048 for agent communication
    3. SHA-256 hashing for integrity
    4. Digital signatures for action verification
    5. Secure key derivation
    """
    
    def __init__(self):
        # Generate RSA key pair for agent communication
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        
        # Master encryption key (derived from password)
        self.master_key = self._derive_master_key("CyberSecAI2024!")
        
        # Initialize encryption log
        self.crypto_log = []
        
        print("🔐 Crypto Manager initialized")
        print(f"   RSA-2048 keys generated")
        print(f"   AES-256 encryption enabled")
    
    def _derive_master_key(self, password):
        """Derive AES-256 key from password using PBKDF2"""
        salt = b'autonomous_cybersec_2024'  # In production: random salt
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        return kdf.derive(password.encode())
    
    def encrypt_data(self, data):
        """
        Encrypt data using AES-256-GCM
        
        Used for: Q-table storage, detection logs, sensitive configs
        """
        # Convert data to JSON string
        if not isinstance(data, str):
            data = json.dumps(data)
        
        # Generate random IV
        iv = os.urandom(12)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        
        encryptor = cipher.encryptor()
        
        # Encrypt
        ciphertext = encryptor.update(data.encode()) + encryptor.finalize()
        
        # Log encryption
        self.crypto_log.append({
            'operation': 'encrypt',
            'algorithm': 'AES-256-GCM',
            'timestamp': datetime.now().isoformat(),
            'data_size': len(data)
        })
        
        # Return IV + Tag + Ciphertext (all base64 encoded)
        return {
            'iv': base64.b64encode(iv).decode(),
            'tag': base64.b64encode(encryptor.tag).decode(),
            'ciphertext': base64.b64encode(ciphertext).decode()
        }
    
    def decrypt_data(self, encrypted_data):
        """Decrypt AES-256-GCM encrypted data"""
        try:
            # Decode base64
            iv = base64.b64decode(encrypted_data['iv'])
            tag = base64.b64decode(encrypted_data['tag'])
            ciphertext = base64.b64decode(encrypted_data['ciphertext'])
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.master_key),
                modes.GCM(iv, tag),
                backend=default_backend()
            )
            
            decryptor = cipher.decryptor()
            
            # Decrypt
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Log decryption
            self.crypto_log.append({
                'operation': 'decrypt',
                'algorithm': 'AES-256-GCM',
                'timestamp': datetime.now().isoformat(),
                'success': True
            })
            
            return plaintext.decode()
            
        except Exception as e:
            print(f"Decryption failed: {e}")
            return None
    
    def sign_action(self, action_data):
        """
        Create digital signature for action verification
        
        Used for: Response actions (blocking, isolation)
        Ensures actions are from legitimate agent
        """
        # Convert to JSON
        message = json.dumps(action_data, sort_keys=True).encode()
        
        # Sign with private key
        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Log signing
        self.crypto_log.append({
            'operation': 'sign',
            'algorithm': 'RSA-PSS-SHA256',
            'timestamp': datetime.now().isoformat(),
            'action': action_data.get('action', 'unknown')
        })
        
        return base64.b64encode(signature).decode()
    
    def verify_signature(self, action_data, signature):
        """Verify digital signature"""
        try:
            message = json.dumps(action_data, sort_keys=True).encode()
            signature_bytes = base64.b64decode(signature)
            
            self.public_key.verify(
                signature_bytes,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception:
            return False
    
    def hash_data(self, data):
        """Create SHA-256 hash for integrity verification"""
        if not isinstance(data, bytes):
            data = str(data).encode()
        
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(data)
        
        return base64.b64encode(digest.finalize()).decode()
    
    def encrypt_agent_message(self, message, recipient_public_key=None):
        """
        Encrypt message for inter-agent communication using RSA
        
        Used for: Detection → Decision → Response communication
        """
        # Use own public key if no recipient specified
        if recipient_public_key is None:
            recipient_public_key = self.public_key
        
        # Convert message to bytes
        if not isinstance(message, bytes):
            message = json.dumps(message).encode()
        
        # Encrypt with RSA
        ciphertext = recipient_public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return base64.b64encode(ciphertext).decode()
    
    def decrypt_agent_message(self, encrypted_message):
        """Decrypt RSA encrypted agent message"""
        try:
            ciphertext = base64.b64decode(encrypted_message)
            
            plaintext = self.private_key.decrypt(
                ciphertext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return plaintext.decode()
            
        except Exception as e:
            print(f"Message decryption failed: {e}")
            return None
    
    def secure_key_exchange(self):
        """
        Simulate Diffie-Hellman key exchange for agent communication
        
        Returns shared secret for session encryption
        """
        # Generate ephemeral key pair
        ephemeral_private = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        ephemeral_public = ephemeral_private.public_key()
        
        # Derive shared secret (simplified)
        shared_secret = os.urandom(32)
        
        self.crypto_log.append({
            'operation': 'key_exchange',
            'protocol': 'RSA-based',
            'timestamp': datetime.now().isoformat()
        })
        
        return shared_secret
    
    def get_crypto_stats(self):
        """Get cryptography statistics"""
        operations = {}
        for log in self.crypto_log:
            op = log['operation']
            operations[op] = operations.get(op, 0) + 1
        
        return {
            'total_operations': len(self.crypto_log),
            'operations_breakdown': operations,
            'encryption_enabled': True,
            'key_strength': 'RSA-2048 / AES-256',
            'last_operation': self.crypto_log[-1] if self.crypto_log else None
        }
    
    def export_public_key(self):
        """Export public key in PEM format"""
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode()