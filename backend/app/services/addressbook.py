from typing import List, Dict
import vobject
from .vcard import VCardService
from urllib.parse import urljoin
import caldav

class AddressBookService:
    """Service for handling address book operations"""
    
    def __init__(self):
        self.vcard = VCardService()
    
    def _get_client(self, user_data: Dict) -> object:
        if not user_data:
            raise ValueError('User data required')
            
        creds = user_data.get('baikal_credentials')
        if not creds:
            raise ValueError('Missing Baikal credentials')
            
        # Construct address book URL
        base_url = creds['serverUrl'].rstrip('/')
        address_path = creds.get('addressBookPath', '').strip()
        if not address_path:
            address_path = f"/addressbooks/{creds['username']}/default/"
        
        address_url = urljoin(base_url, address_path.lstrip('/'))
            
        return caldav.DAVClient(
            url=address_url,
            username=creds['username'],
            password=creds['password']
        )
    
    def _get_book(self, user_data: Dict, book_id: str = None) -> object:
        if not user_data:
            raise ValueError('User data required')
        client = self._get_client(user_data)
        books = client.principal().addressbooks()
        if not books:
            raise ValueError('No address books found')
        return next(
            (b for b in books if b.url == book_id),
            books[0]
        ) if book_id else books[0]
    
    def get_books(self, user_data: Dict) -> List[Dict]:
        """Get list of available address books"""
        client = self._get_client(user_data)
        return [
            {'id': book.url, 'name': book.name or 'Default'} 
            for book in client.principal().addressbooks()
        ]
    
    def get_contacts(self, user_data: Dict, book_id: str) -> List[Dict]:
        """Get all contacts from an address book"""
        book = self._get_book(user_data, book_id)
        return [
            {**self.vcard.to_json(vobject.readOne(obj.data)), 'addressBookId': book.url}
            for obj in book.objects.values()
        ]
    
    def _save_contact(self, book: object, contact_data: Dict) -> Dict:
        vcard = self.vcard.from_json(contact_data)
        book.save_vcard(vcard.serialize())
        return self.vcard.to_json(vcard)
    
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
        contact = next(
            (obj for obj in book.objects.values() 
             if hasattr(vobject.readOne(obj.data), 'uid') 
             and vobject.readOne(obj.data).uid.value == contact_id),
            None
        )
        if not contact:
            raise ValueError('Contact not found')
        contact.delete()
    
    def import_contacts(self, user_data: Dict, book_id: str, vcard_data: str) -> int:
        """Import contacts from vCard data"""
        book = self._get_book(user_data, book_id)
        imported = 0
        for vcard in self.vcard.parse_vcards(vcard_data):
            try:
                book.save_vcard(self.vcard.ensure_uid(vcard).serialize())
                imported += 1
            except Exception as e:
                from ..utils.settings import log_error
                log_error(user_data.get('username', 'unknown'), f"Import failed: {str(e)}")
        return imported
    
    def export_contacts(self, user_data: Dict, book_id: str) -> str:
        """Export contacts to vCard format"""
        book = self._get_book(user_data, book_id)
        return '\n'.join(obj.data for obj in book.objects.values()) 