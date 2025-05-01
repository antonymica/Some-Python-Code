from flask import Flask, render_template, request, redirect, url_for, flash
import ldap
from ldap.modlist import addModlist, modifyModlist
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')

# Configuration LDAP
LDAP_URI = os.environ.get('LDAP_URI', 'ldap://ldap-server:1389')
LDAP_BASE_DN = os.environ.get('LDAP_BASE_DN', 'dc=mycompany,dc=com')
LDAP_ADMIN_DN = os.environ.get('LDAP_ADMIN_DN', 'cn=admin,dc=mycompany,dc=com')
LDAP_ADMIN_PASSWORD = os.environ.get('LDAP_ADMIN_PASSWORD', 'adminpassword')
LDAP_USER_OU = os.environ.get('LDAP_USER_OU', 'users')
LDAP_GROUP_OU = os.environ.get('LDAP_GROUP_OU', 'groups')

def ldap_connection_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            conn = ldap.initialize(LDAP_URI)
            conn.simple_bind_s(LDAP_ADMIN_DN, LDAP_ADMIN_PASSWORD)
            kwargs['ldap_conn'] = conn
            return f(*args, **kwargs)
        except ldap.LDAPError as e:
            flash(f"LDAP Error: {str(e)}", 'error')
            return redirect(url_for('index'))
    return decorated_function

@app.route('/')
@ldap_connection_required
def index(ldap_conn):
    try:
        # Récupération et formatage des utilisateurs
        users = []
        raw_users = ldap_conn.search_s(f'ou={LDAP_USER_OU},{LDAP_BASE_DN}', ldap.SCOPE_ONELEVEL)
        for user in raw_users:
            users.append({
                'uid': user[1].get('uid', [b''])[0].decode('utf-8'),
                'cn': user[1].get('cn', [b''])[0].decode('utf-8'),
                'mail': user[1].get('mail', [b''])[0].decode('utf-8')
            })

        # Récupération et formatage des groupes
        groups = []
        raw_groups = ldap_conn.search_s(f'ou={LDAP_GROUP_OU},{LDAP_BASE_DN}', ldap.SCOPE_ONELEVEL)
        for group in raw_groups:
            groups.append({
                'cn': group[1].get('cn', [b''])[0].decode('utf-8'),
                'description': group[1].get('description', [b''])[0].decode('utf-8') if group[1].get('description') else ''
            })

        return render_template('index.html', 
                            users=users,
                            groups=groups,
                            user_ou=LDAP_USER_OU,
                            group_ou=LDAP_GROUP_OU)

    except Exception as e:
        flash(f"Error retrieving data: {str(e)}", 'error')
        return render_template('index.html', users=[], groups=[])

@app.route('/add_user', methods=['POST'])
@ldap_connection_required
def add_user(ldap_conn):
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    
    if not all([username, password, email, first_name, last_name]):
        flash('All fields are required', 'error')
        return redirect(url_for('index'))
    
    try:
        user_dn = f'uid={username},ou={LDAP_USER_OU},{LDAP_BASE_DN}'
        user_attrs = {
            'objectClass': [b'top', b'inetOrgPerson', b'organizationalPerson', b'person'],
            'uid': [username.encode('utf-8')],
            'cn': [f"{first_name} {last_name}".encode('utf-8')],
            'givenName': [first_name.encode('utf-8')],
            'sn': [last_name.encode('utf-8')],
            'mail': [email.encode('utf-8')],
            'userPassword': [password.encode('utf-8')],
            'userPrincipalName': [f"{username}@mycompany.com".encode('utf-8')]
        }
        
        ldap_conn.add_s(user_dn, addModlist(user_attrs))
        flash(f'User {username} added successfully', 'success')
    except ldap.LDAPError as e:
        error_msg = str(e)
        if 'already exists' in error_msg:
            flash(f'User {username} already exists', 'error')
        else:
            flash(f"Error adding user: {error_msg}", 'error')
    
    return redirect(url_for('index'))

@app.route('/edit_user/<username>', methods=['GET', 'POST'])
@ldap_connection_required
def edit_user(ldap_conn, username):
    if request.method == 'GET':
        try:
            user_dn = f'uid={username},ou={LDAP_USER_OU},{LDAP_BASE_DN}'
            user_data = ldap_conn.search_s(user_dn, ldap.SCOPE_BASE)
            return render_template('edit_user.html', user=user_data[0])
        except Exception as e:
            flash(f"Error retrieving user: {str(e)}", 'error')
            return redirect(url_for('index'))
    
    # Handle POST request
    email = request.form.get('email')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    
    try:
        user_dn = f'uid={username},ou={LDAP_USER_OU},{LDAP_BASE_DN}'
        mod_attrs = [
            (ldap.MOD_REPLACE, 'mail', email.encode('utf-8')),
            (ldap.MOD_REPLACE, 'givenName', first_name.encode('utf-8')),
            (ldap.MOD_REPLACE, 'sn', last_name.encode('utf-8')),
            (ldap.MOD_REPLACE, 'cn', f"{first_name} {last_name}".encode('utf-8'))
        ]
        ldap_conn.modify_s(user_dn, mod_attrs)
        flash(f'User {username} updated successfully', 'success')
    except Exception as e:
        flash(f"Error updating user: {str(e)}", 'error')
    
    return redirect(url_for('index'))

@app.route('/delete_user/<username>')
@ldap_connection_required
def delete_user(ldap_conn, username):
    try:
        user_dn = f'uid={username},ou={LDAP_USER_OU},{LDAP_BASE_DN}'
        ldap_conn.delete_s(user_dn)
        flash(f'User {username} deleted successfully', 'success')
    except Exception as e:
        flash(f"Error deleting user: {str(e)}", 'error')
    
    return redirect(url_for('index'))

@app.route('/add_group', methods=['POST'])
@ldap_connection_required
def add_group(ldap_conn):
    group_name = request.form.get('group_name')
    description = request.form.get('description')
    
    try:
        group_dn = f'cn={group_name},ou={LDAP_GROUP_OU},{LDAP_BASE_DN}'
        group_attrs = {
            'objectClass': [b'top', b'groupOfNames'],
            'cn': [group_name.encode('utf-8')],
            'description': [description.encode('utf-8')] if description else [b''],
            'member': [f'uid=admin,ou={LDAP_USER_OU},{LDAP_BASE_DN}'.encode('utf-8')]
        }
        ldap_conn.add_s(group_dn, addModlist(group_attrs))
        flash(f'Group {group_name} created successfully', 'success')
    except Exception as e:
        flash(f"Error creating group: {str(e)}", 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=os.environ.get('FLASK_DEBUG', False))