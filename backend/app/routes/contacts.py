from flask import Blueprint, request, jsonify, session, Response
import vobject
from ..utils.auth import login_required
from ..utils.settings import get_user_data, log_error
from ..services.addressbook import AddressBookService
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Only add handler if none exist
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.debug("Contacts routes logger initialized")

contacts = Blueprint('contacts', __name__, url_prefix='/api/contacts')
addressbook_service = AddressBookService()

def contact_to_json(vcard) -> dict:
    return {
        'id': getattr(vcard, 'uid', uuid.uuid4()).value,
        'displayName': getattr(vcard, 'fn', '').value if hasattr(vcard, 'fn') else '',
        'firstName': getattr(vcard, 'n', '').value.given if hasattr(vcard, 'n') else '',
        'lastName': getattr(vcard, 'n', '').value.family if hasattr(vcard, 'n') else '',
        'organization': getattr(vcard, 'org', [''])[0] if hasattr(vcard, 'org') else '',
        'email': getattr(vcard, 'email', '').value if hasattr(vcard, 'email') else '',
        'phone': getattr(vcard, 'tel', '').value if hasattr(vcard, 'tel') else '',
        'address': getattr(vcard, 'adr', '').value.street if hasattr(vcard, 'adr') else '',
        'notes': getattr(vcard, 'note', '').value if hasattr(vcard, 'note') else ''
    }

def json_to_vcard(data: dict) -> vobject.vCard:
    vcard = vobject.vCard()
    vcard.add('uid').value = data.get('id', str(uuid.uuid4()))
    vcard.add('fn').value = data.get('displayName', '')
    vcard.add('n').value = vobject.vcard.Name(
        family=data.get('lastName', ''),
        given=data.get('firstName', '')
    )
    
    optional = {
        'org': lambda v: [v],
        'email': lambda v: v,
        'tel': lambda v: v,
        'adr': lambda v: vobject.vcard.Address(street=v),
        'note': lambda v: v
    }
    
    for field, transform in optional.items():
        if value := data.get(field.replace('tel', 'phone')):
            vcard.add(field).value = transform(value)
            
    vcard.add('rev').value = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    return vcard

def get_address_book(address_book_id: str):
    if not address_book_id:
        raise ValueError('Address book ID is required')
    return get_user_data().get_carddav_client().principal().addressbook(address_book_id)

@contacts.route('/address-books', methods=['GET'])
@login_required
def get_address_books():
    """Get list of available address books"""
    logger.debug(f"Address books request received for user {session.get('user_id')}")
    try:
        user_data = get_user_data()
        if not user_data:
            logger.warning(f"No user data found for user {session.get('user_id')}")
            return jsonify({'error': 'Not authenticated'}), 401
            
        books = addressbook_service.get_books(user_data)
        logger.debug(f"Address books retrieved for user {session.get('user_id')}: {books}")
        return jsonify(books)
    except Exception as e:
        logger.error(f"Failed to get address books for user {session.get('user_id')}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@contacts.route('/contacts', methods=['GET'])
@login_required
def get_contacts():
    """Get contacts from an address book"""
    logger.debug(f"Contacts request received for user {session.get('user_id')}")
    try:
        user_data = get_user_data()
        if not user_data:
            logger.warning(f"No user data found for user {session.get('user_id')}")
            return jsonify({'error': 'Not authenticated'}), 401
            
        book_id = request.args.get('addressBookId')
        if not book_id:
            logger.warning(f"Missing address book ID for user {session.get('user_id')}")
            return jsonify({'error': 'Address book ID is required'}), 400
            
        contacts = addressbook_service.get_contacts(user_data, book_id)
        logger.debug(f"Contacts retrieved for user {session.get('user_id')}: {contacts}")
        return jsonify(contacts)
    except Exception as e:
        logger.error(f"Failed to get contacts for user {session.get('user_id')}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@contacts.route('/contacts', methods=['POST'])
@login_required
def create_contact():
    """Create a new contact"""
    logger.debug(f"Create contact request received for user {session.get('user_id')}")
    if not request.json:
        logger.warning(f"No contact data provided for user {session.get('user_id')}")
        return jsonify({'error': 'No contact data provided'}), 400
    
    try:
        user_data = get_user_data()
        if not user_data:
            logger.warning(f"No user data found for user {session.get('user_id')}")
            return jsonify({'error': 'Not authenticated'}), 401
            
        data = request.json.copy()
        book_id = data.pop('addressBookId')
        if not book_id:
            logger.warning(f"Missing address book ID for user {session.get('user_id')}")
            return jsonify({'error': 'Address book ID is required'}), 400
            
        contact = addressbook_service.create_contact(user_data, book_id, data)
        logger.debug(f"Contact created for user {session.get('user_id')}: {contact}")
        return jsonify(contact)
    except Exception as e:
        logger.error(f"Failed to create contact for user {session.get('user_id')}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@contacts.route('/contacts/<contact_id>', methods=['PUT'])
@login_required
def update_contact(contact_id):
    """Update an existing contact"""
    logger.debug(f"Update contact request received for user {session.get('user_id')}")
    if not request.json:
        logger.warning(f"No contact data provided for user {session.get('user_id')}")
        return jsonify({'error': 'No contact data provided'}), 400
    
    try:
        user_data = get_user_data()
        if not user_data:
            logger.warning(f"No user data found for user {session.get('user_id')}")
            return jsonify({'error': 'Not authenticated'}), 401
            
        data = request.json.copy()
        book_id = data.pop('addressBookId')
        if not book_id:
            logger.warning(f"Missing address book ID for user {session.get('user_id')}")
            return jsonify({'error': 'Address book ID is required'}), 400
            
        data['id'] = contact_id
        contact = addressbook_service.update_contact(user_data, book_id, data)
        logger.debug(f"Contact updated for user {session.get('user_id')}: {contact}")
        return jsonify(contact)
    except Exception as e:
        logger.error(f"Failed to update contact for user {session.get('user_id')}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@contacts.route('/contacts/<contact_id>', methods=['DELETE'])
@login_required
def delete_contact(contact_id):
    """Delete a contact"""
    logger.debug(f"Delete contact request received for user {session.get('user_id')}")
    try:
        user_data = get_user_data()
        if not user_data:
            logger.warning(f"No user data found for user {session.get('user_id')}")
            return jsonify({'error': 'Not authenticated'}), 401
            
        book_id = request.args.get('addressBookId')
        if not book_id:
            logger.warning(f"Missing address book ID for user {session.get('user_id')}")
            return jsonify({'error': 'Address book ID is required'}), 400
            
        addressbook_service.delete_contact(user_data, book_id, contact_id)
        logger.debug(f"Contact deleted for user {session.get('user_id')}")
        return jsonify({'message': 'Contact deleted'})
    except Exception as e:
        logger.error(f"Failed to delete contact for user {session.get('user_id')}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@contacts.route('/contacts/import', methods=['POST'])
@login_required
def import_contacts():
    """Import contacts from a vCard file"""
    logger.debug(f"Import contacts request received for user {session.get('user_id')}")
    if 'file' not in request.files:
        logger.warning(f"No file provided for user {session.get('user_id')}")
        return jsonify({'error': 'No file provided'}), 400
        
    try:
        user_data = get_user_data()
        if not user_data:
            logger.warning(f"No user data found for user {session.get('user_id')}")
            return jsonify({'error': 'Not authenticated'}), 401
            
        book_id = request.form.get('addressBookId')
        if not book_id:
            logger.warning(f"Missing address book ID for user {session.get('user_id')}")
            return jsonify({'error': 'Address book ID is required'}), 400
            
        file = request.files['file']
        if not file.filename.endswith('.vcf'):
            logger.warning(f"Invalid file type for user {session.get('user_id')}")
            return jsonify({'error': 'Invalid file type. Only .vcf files are supported'}), 400
            
        contacts = addressbook_service.import_contacts(user_data, book_id, file)
        logger.debug(f"Contacts imported for user {session.get('user_id')}: {contacts}")
        return jsonify({'message': f'Successfully imported {len(contacts)} contacts'})
    except Exception as e:
        logger.error(f"Failed to import contacts for user {session.get('user_id')}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@contacts.route('/contacts/export', methods=['GET'])
@login_required
def export_contacts():
    """Export contacts to a vCard file"""
    logger.debug(f"Export contacts request received for user {session.get('user_id')}")
    try:
        user_data = get_user_data()
        if not user_data:
            logger.warning(f"No user data found for user {session.get('user_id')}")
            return jsonify({'error': 'Not authenticated'}), 401
            
        book_id = request.args.get('addressBookId')
        if not book_id:
            logger.warning(f"Missing address book ID for user {session.get('user_id')}")
            return jsonify({'error': 'Address book ID is required'}), 400
            
        vcard_data = addressbook_service.export_contacts(user_data, book_id)
        logger.debug(f"Contacts exported for user {session.get('user_id')}")
        return Response(
            vcard_data,
            mimetype='text/vcard',
            headers={'Content-Disposition': 'attachment; filename=contacts.vcf'}
        )
    except Exception as e:
        logger.error(f"Failed to export contacts for user {session.get('user_id')}: {str(e)}")
        return jsonify({'error': str(e)}), 500 