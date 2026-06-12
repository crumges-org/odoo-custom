import xmlrpc.client

url = 'http://localhost:18069'
db = 'odoo'  # Assuming the DB is still 'odoo', or maybe it changed?
username = 'admin'
password = 'admin_password'

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
try:
    uid = common.authenticate(db, username, password, {})
    if uid:
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        data = models.execute_kw(db, uid, password, 'res.users.license', 'get_dashboard_data', [])
        print("DASHBOARD DATA:", data)
    else:
        print("AUTH FAILED")
except Exception as e:
    print("ERROR:", e)
