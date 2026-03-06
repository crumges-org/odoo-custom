import xmlrpc.client

url = 'http://localhost:18069'
db = 'odoo_pruebasv18'
username = 'admin'
password = '123'

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# Nos aseguramos que los ejecutores tengan permiso para seguir el documento y escribir
# Para Odoo 17+, los usuarios internos por defecto ya pueden, el problema es que la interfaz
# del mail.thread desactiva el boton "Enviar Mensaje" si NO eres usuario con permisos WRITE en el modelo.
