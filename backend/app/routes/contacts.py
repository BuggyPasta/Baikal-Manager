from flask import Blueprint, request, jsonify, session, Response
import vobject
from ..utils.auth import login_required
from ..utils.settings import get_user_data, log_error
from ..services.addressbook import AddressBookService

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
    try:
        user_data = get_user_data()
        if not user_data:
            return jsonify({'error': 'User data not found'}), 401
            
        books = addressbook_service.get_books(user_data)
        return jsonify(books)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        log_error(session.get('user_id', 'unknown'), str(e))
        return jsonify({'error': 'Failed to fetch address books'}), 500

@contacts.route('/contacts', methods=['GET'])
@login_required
def get_contacts():
    try:
        user_data = get_user_data()
        if not user_data:
            return jsonify({'error': 'User data not found'}), 401
            
        book_id = request.args.get('addressBookId')
        if not book_id:
            return jsonify({'error': 'Address book ID is required'}), 400
            
        contacts = addressbook_service.get_contacts(user_data, book_id)
        return jsonify(contacts)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        log_error(session.get('user_id', 'unknown'), str(e))
        return jsonify({'error': 'Failed to fetch contacts'}), 500

@contacts.route('/contacts', methods=['POST'])
@login_required
def create_contact():
    if not request.json:
        return jsonify({'error': 'No contact data provided'}), 400
    
    try:
        user_data = get_user_data()
        if not user_data:
            return jsonify({'error': 'User data not found'}), 401
            
        data = request.json.copy()
        book_id = data.pop('addressBookId')
        if not book_id:
            return jsonify({'error': 'Address book ID is required'}), 400
            
        contact = addressbook_service.create_contact(user_data, book_id, data)
        return jsonify(contact)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        log_error(session.get('user_id', 'unknown'), str(e))
        return jsonify({'error': 'Failed to create contact'}), 500

@contacts.route('/contacts/<contact_id>', methods=['PUT'])
@login_required
def update_contact(contact_id):
    if not request.json:
        return jsonify({'error': 'No contact data provided'}), 400
    
    try:
        user_data = get_user_data()
        if not user_data:
            return jsonify({'error': 'User data not found'}), 401
            
        data = request.json.copy()
        book_id = data.pop('addressBookId')
        if not book_id:
            return jsonify({'error': 'Address book ID is required'}), 400
            
        data['id'] = contact_id
        contact = addressbook_service.update_contact(user_data, book_id, data)
        return jsonify(contact)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        log_error(session.get('user_id', 'unknown'), str(e))
        return jsonify({'error': 'Failed to update contact'}), 500

@contacts.route('/contacts/<contact_id>', methods=['DELETE'])
@login_required
def delete_contact(contact_id):
    try:
        user_data = get_user_data()
        if not user_data:
            return jsonify({'error': 'User data not found'}), 401
            
        book_id = request.args.get('addressBookId')
        if not book_id:
            return jsonify({'error': 'Address book ID is required'}), 400
            
        addressbook_service.delete_contact(user_data, book_id, contact_id)
        return jsonify({'message': 'Contact deleted'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        log_error(session.get('user_id', 'unknown'), str(e))
        return jsonify({'error': 'Failed to delete contact'}), 500

@contacts.route('/contacts/import', methods=['POST'])
@login_required
def import_contacts():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    if not request.files['file'].filename.endswith('.vcf'):
        return jsonify({'error': 'Invalid file format. Only .vcf files are supported'}), 400
    
    try:
        user_data = get_user_data()
        if not user_data:
            return jsonify({'error': 'User data not found'}), 401
            
        book_id = request.form.get('addressBookId')
        if not book_id:
            return jsonify({'error': 'Address book ID is required'}), 400
            
        vcard_data = request.files['file'].read().decode('utf-8')
        count = addressbook_service.import_contacts(user_data, book_id, vcard_data)
        return jsonify({'message': f'Imported {count} contacts'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        log_error(session.get('user_id', 'unknown'), str(e))
        return jsonify({'error': 'Failed to import contacts'}), 500

@contacts.route('/contacts/export', methods=['GET'])
@login_required
def export_contacts():
    try:
        user_data = get_user_data()
        if not user_data:
            return jsonify({'error': 'User data not found'}), 401
            
        book_id = request.args.get('addressBookId')
        if not book_id:
            return jsonify({'error': 'Address book ID is required'}), 400
            
        vcard_data = addressbook_service.export_contacts(user_data, book_id)
        return Response(
            vcard_data,
            mimetype='text/vcard',
            headers={'Content-Disposition': 'attachment; filename=contacts.vcf'}
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        log_error(session.get('user_id', 'unknown'), str(e))
        return jsonify({'error': 'Failed to export contacts'}), 500 