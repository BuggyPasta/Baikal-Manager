from typing import List, Dict
import vobject
from .vcard import VCardService
from urllib.parse import urljoin
import caldav
from .baikal_client import BaikalClient
import uuid
from datetime import datetime

class AddressBookService:
    """Service for handling address book operations"""
    
    def __init__(self):
        self.vcard = VCardService()
        self.baikal_client = BaikalClient()
    
    def _get_client(self, user_data: Dict) -> caldav.DAVClient:
        if not user_data:
            raise ValueError('User data required')
            
        creds = user_data.get('baikal_credentials')
        if not creds:
            raise ValueError('Missing Baikal credentials')
            
        try:
            success, client_or_error = self.baikal_client.verify_connection(creds)
            if not success:
                raise ValueError(f'Connection failed: {client_or_error}')
                
            success, client_or_error = self.baikal_client.get_client()
            if not success:
                raise ValueError(f'Failed to get client: {client_or_error}')
                
            return client_or_error
        except caldav.lib.error.DAVError as e:
            raise ValueError(f"DAV connection error: {str(e)}")
    
    def _get_book(self, user_data: Dict, book_id: str = None) -> object:
        if not user_data:
            raise ValueError('User data required')
        client = self._get_client(user_data)
        try:
            books = client.principal().address_books()
            if not books:
                raise ValueError('No address books found')
            
            if book_id:
                # Normalize URLs for comparison
                book_id = str(book_id)
                for book in books:
                    if str(book.url) == book_id:
                        return book
                raise ValueError('Address book not found')
            return books[0]
        except caldav.lib.error.DAVError as e:
            raise ValueError(f"Failed to access address books: {str(e)}")
    
    def get_books(self, user_data: Dict) -> List[Dict]:
        """Get list of available address books"""
        client = self._get_client(user_data)
        try:
            return [
                {'id': str(book.url), 'name': book.name or 'Default'} 
                for book in client.principal().address_books()
            ]
        except caldav.lib.error.DAVError as e:
            raise ValueError(f"Failed to fetch address books: {str(e)}")
    
    def get_contacts(self, user_data: Dict, book_id: str) -> List[Dict]:
        """Get all contacts from an address book"""
        book = self._get_book(user_data, book_id)
        contacts = []
        try:
            for obj in book.objects():
                try:
                    vcard = vobject.readOne(obj.data)
                    # Skip invalid vCards
                    if not hasattr(vcard, 'fn'):
                        continue
                    contact_data = self.vcard.to_json(vcard)
                    contact_data['addressBookId'] = str(book.url)
                    contacts.append(contact_data)
                except Exception as e:
                    from ..utils.settings import log_error
                    log_error(user_data.get('user_id', 'unknown'), f"Failed to parse contact: {str(e)}")
            return contacts
        except caldav.lib.error.DAVError as e:
            raise ValueError(f"Failed to fetch contacts: {str(e)}")
    
    def _save_contact(self, book: object, contact_data: Dict) -> Dict:
        try:
            vcard = self.vcard.from_json(contact_data)
            # Ensure UID exists
            if not hasattr(vcard, 'uid'):
                vcard.add('uid')
                vcard.uid.value = str(uuid.uuid4())
            # Ensure proper vCard version for Baikal
            vcard.version.value = '3.0'
            # Add required fields for Baikal
            if not hasattr(vcard, 'rev'):
                vcard.add('rev')
            vcard.rev.value = datetime.now().strftime('%Y%m%dT%H%M%SZ')
            
            try:
                book.add_vcard(vcard.serialize())
                return self.vcard.to_json(vcard)
            except caldav.lib.error.DAVError as e:
                raise ValueError(f"Failed to save contact to server: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to process contact data: {str(e)}")
    
    def create_contact(self, user_data: Dict, book_id: str, contact_data: Dict) -> Dict:
        """Create a new contact"""
        book = self._get_book(user_data, book_id)
        return self._save_contact(book, contact_data)
    
    def update_contact(self, user_data: Dict, book_id: str, contact_data: Dict) -> Dict:
        """Update an existing contact"""
        book = self._get_book(user_data, book_id)
        return self._save_contact(book, contact_data)
    
    def delete_contact(self, user_data: Dict, book_id: str, contact_id: str) -> None:
        """Delete a contact"""
        book = self._get_book(user_data, book_id)
        try:
            # First try to find the contact
            contact = None
            for obj in book.objects():
                try:
                    vcard = vobject.readOne(obj.data)
                    if hasattr(vcard, 'uid') and str(vcard.uid.value) == str(contact_id):
                        contact = obj
                        break
                except Exception as e:
                    from ..utils.settings import log_error
                    log_error(user_data.get('user_id', 'unknown'), f"Failed to parse contact during deletion: {str(e)}")
                    continue
            
            if not contact:
                raise ValueError('Contact not found')
                
            # Then try to delete it
            try:
                contact.delete()
            except caldav.lib.error.DAVError as e:
                raise ValueError(f"Failed to delete contact from server: {str(e)}")
                
        except caldav.lib.error.DAVError as e:
            raise ValueError(f"Failed to access contacts: {str(e)}")
    
    def import_contacts(self, user_data: Dict, book_id: str, vcard_data: str) -> int:
        """Import contacts from vCard data"""
        book = self._get_book(user_data, book_id)
        imported = 0
        for vcard in self.vcard.parse_vcards(vcard_data):
            try:
                # Ensure proper vCard version and required fields
                vcard.version.value = '3.0'
                if not hasattr(vcard, 'uid'):
                    vcard.add('uid')
                    vcard.uid.value = str(uuid.uuid4())
                if not hasattr(vcard, 'rev'):
                    vcard.add('rev')
                vcard.rev.value = datetime.now().strftime('%Y%m%dT%H%M%SZ')
                
                book.add_vcard(vcard.serialize())
                imported += 1
            except Exception as e:
                from ..utils.settings import log_error
                log_error(user_data.get('user_id', 'unknown'), f"Import failed: {str(e)}")
        return imported
    
    def export_contacts(self, user_data: Dict, book_id: str) -> str:
        """Export contacts to vCard format"""
        book = self._get_book(user_data, book_id)
        try:
            valid_vcards = []
            for obj in book.objects():
                try:
                    # Validate each vCard before including it
                    vcard = vobject.readOne(obj.data)
                    if hasattr(vcard, 'fn'):  # Only export valid vCards
                        valid_vcards.append(obj.data)
                except Exception as e:
                    from ..utils.settings import log_error
                    log_error(user_data.get('user_id', 'unknown'), f"Failed to parse contact during export: {str(e)}")
                    continue
            return '\n'.join(valid_vcards)
        except caldav.lib.error.DAVError as e:
            raise ValueError(f"Failed to export contacts: {str(e)}") 