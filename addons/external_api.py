import xmlrpc.client

url = "http://localhost:8071"

db_name = "testdb"

user_name = "admin"
password = "admin"

common = xmlrpc.client.ServerProxy(
    f"{url}/xmlrpc/2/common"
)

print("version info", common.version())

uid = common.authenticate(
    db_name, user_name, password, {}
)

if uid:
    print("authentication success")

else:
    print("authentication failed")
