from flask import Blueprint, request, jsonify, session, Response
import vobject
from datetime import datetime
import uuid
from ..utils.auth import login_required
from ..utils.settings import get_user_data, log_error

contacts = Blueprint('contacts', __name__, url_prefix='/api/contacts')

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
        client = get_user_data().get_carddav_client()
        books = client.principal().addressbooks()
        return jsonify([{'id': book.id, 'name': book.name} for book in books])
    except Exception as e:
        log_error(session.get('username', 'unknown'), str(e))
        return jsonify({'error': 'Failed to fetch address books'}), 500

@contacts.route('/contacts', methods=['GET'])
@login_required
def get_contacts():
    try:
        book = get_address_book(request.args.get('addressBookId'))
        return jsonify([contact_to_json(vobject.readOne(card.data)) for card in book.cards()])
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        log_error(session.get('username', 'unknown'), str(e))
        return jsonify({'error': 'Failed to fetch contacts'}), 500

@contacts.route('/contacts', methods=['POST'])
@login_required
def create_contact():
    if not request.json:
        return jsonify({'error': 'No contact data provided'}), 400
    
    try:
        data = request.json.copy()
        book = get_address_book(data.pop('addressBookId'))
        vcard = json_to_vcard(data)
        book.save_vcard(vcard.serialize())
        return jsonify(contact_to_json(vcard))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        log_error(session.get('username', 'unknown'), str(e))
        return jsonify({'error': 'Failed to create contact'}), 500

@contacts.route('/contacts/<contact_id>', methods=['PUT'])
@login_required
def update_contact(contact_id):
    if not request.json:
        return jsonify({'error': 'No contact data provided'}), 400
    
    try:
        data = request.json.copy()
        book = get_address_book(data.pop('addressBookId'))
        data['id'] = contact_id
        vcard = json_to_vcard(data)
        book.save_vcard(vcard.serialize())
        return jsonify(contact_to_json(vcard))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        log_error(session.get('username', 'unknown'), str(e))
        return jsonify({'error': 'Failed to update contact'}), 500

@contacts.route('/contacts/<contact_id>', methods=['DELETE'])
@login_required
def delete_contact(contact_id):
    try:
        book = get_address_book(request.args.get('addressBookId'))
        for card in book.cards():
            vcard = vobject.readOne(card.data)
            if getattr(vcard, 'uid', None) and vcard.uid.value == contact_id:
                card.delete()
                return jsonify({'message': 'Contact deleted'})
        return jsonify({'error': 'Contact not found'}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        log_error(session.get('username', 'unknown'), str(e))
        return jsonify({'error': 'Failed to delete contact'}), 500

@contacts.route('/contacts/import', methods=['POST'])
@login_required
def import_contacts():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    if not request.files['file'].filename.endswith('.vcf'):
        return jsonify({'error': 'Invalid file format. Only .vcf files are supported'}), 400
    
    try:
        book = get_address_book(request.form.get('addressBookId'))
        vcards = vobject.readComponents(request.files['file'].read().decode('utf-8'))
        count = 0
        for vcard in vcards:
            book.save_vcard(vcard.serialize())
            count += 1
        return jsonify({'message': f'Imported {count} contacts'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        log_error(session.get('username', 'unknown'), str(e))
        return jsonify({'error': 'Failed to import contacts'}), 500

@contacts.route('/contacts/export', methods=['GET'])
@login_required
def export_contacts():
    try:
        book = get_address_book(request.args.get('addressBookId'))
        return Response(
            ''.join(card.data for card in book.cards()),
            mimetype='text/vcard',
            headers={'Content-Disposition': 'attachment; filename=contacts.vcf'}
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        log_error(session.get('username', 'unknown'), str(e))
        return jsonify({'error': 'Failed to export contacts'}), 500 