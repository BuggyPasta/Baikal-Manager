import vobject
from datetime import datetime
import uuid

class VCardService:
    """Service for handling vCard operations"""
    
    def to_json(self, vcard) -> dict:
        """Convert a vCard to JSON format"""
        return {
            'id': getattr(vcard, 'uid', uuid.uuid4()).value,
            'firstName': vcard.n.value.given if hasattr(vcard, 'n') else '',
            'lastName': vcard.n.value.family if hasattr(vcard, 'n') else '',
            'displayName': vcard.fn.value if hasattr(vcard, 'fn') else '',
            'organization': vcard.org.value[0] if hasattr(vcard, 'org') else '',
            'email': vcard.email.value if hasattr(vcard, 'email') else '',
            'phone': vcard.tel.value if hasattr(vcard, 'tel') else '',
            'address': vcard.adr.value.street if hasattr(vcard, 'adr') else '',
            'notes': vcard.note.value if hasattr(vcard, 'note') else ''
        }
    
    def from_json(self, data: dict) -> vobject.vCard:
        """Convert JSON data to a vCard"""
        vcard = vobject.vCard()
        vcard.add('uid').value = data.get('id', str(uuid.uuid4()))
        vcard.add('n').value = vobject.vcard.Name(family=data.get('lastName', ''), given=data.get('firstName', ''))
        vcard.add('fn').value = data.get('displayName') or f"{data.get('firstName', '')} {data.get('lastName', '')}".strip()
        
        if data.get('organization'): vcard.add('org').value = [data['organization']]
        if data.get('email'): vcard.add('email').value = data['email']
        if data.get('phone'): vcard.add('tel').value = data['phone']
        if data.get('address'): vcard.add('adr').value = vobject.vcard.Address(street=data['address'])
        if data.get('notes'): vcard.add('note').value = data['notes']
        
        vcard.add('rev').value = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        return vcard
    
    def parse_vcards(self, data: str) -> list:
        """Parse vCard data into a list of vCard objects"""
        return list(vobject.readComponents(data))
    
    def serialize_vcard(self, vcard: vobject.vCard) -> str:
        """Serialize a vCard object to string"""
        return vcard.serialize()
    
    def ensure_uid(self, vcard: vobject.vCard) -> vobject.vCard:
        """Ensure a vCard has a UID"""
        if not hasattr(vcard, 'uid'):
            vcard.add('uid').value = str(uuid.uuid4())
        return vcard 