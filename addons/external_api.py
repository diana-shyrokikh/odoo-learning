"""
ODOO EXTERNAL API documentation
https://www.odoo.com/documentation/17.0/developer/reference/external_api.html
"""
import xmlrpc.client

url = "http://localhost:8071"

db = "testdb"

user_name = "admin"
password = "admin"

common = xmlrpc.client.ServerProxy(
    f"{url}/xmlrpc/2/common"
)

print("version info", common.version())

# AUTHENTICATION
uid = common.authenticate(
    db, user_name, password, {}
)

if uid:
    print("authentication success")

    models = xmlrpc.client.ServerProxy(
        f"{url}/xmlrpc/2/object"
    )

    # SEARCH
    partners = models.execute_kw(
        db,
        uid, password,
        "res.partner",
        "search",
        [[["is_company", "=", True]]],
        {"limit": 8}
    )

    print("partners", partners)

    # SEARCH COUNT
    partners_count = models.execute_kw(
        db,
        uid, password,
        "res.partner",
        "search_count",
        [[["is_company", "=", True]]],
    )

    print("partners count", partners_count)

    # READ
    partner_rec = models.execute_kw(
        db,
        uid,
        password,
        "res.partner",
        "read",
        [partners],
        {"fields": ["id", "name"]},
    )

    print(partner_rec)

    # SEARCH READ
    partner_rec_2 = models.execute_kw(
        db,
        uid,
        password,
        "res.partner",
        "search_read",
        [[["is_company", "=", True]]],
        {
            "fields": ["id", "name",],
            "limit": 8
        }

    )

    print("partner_rec_2", partner_rec_2)

    # CREATE
    new_partner_id = models.execute_kw(
        db,
        uid,
        password,
        "res.partner",
        "create",
        [{
            "name": "New Partner",
            "email": "email@gmail.com"
        }]
    )

    print("created record", new_partner_id)

    # WRITE / UPDATE
    models.execute_kw(
        db,
        uid,
        password,
        "res.partner",
        "write",
        [[new_partner_id],
         {
             "phone": "22222222222222222222",
             "name": "33333333333333"
         }]
    )

    updated_partner = models.execute_kw(
        db,
        uid,
        password,
        "res.partner",
        "read",
        [[new_partner_id], ["phone", "name"]]
    )

    print("updated_partner", updated_partner)

    # DELETE / UNLINK
    models.execute_kw(
        db,
        uid,
        password,
        "res.partner",
        "unlink",
        [[new_partner_id]]
    )

else:
    print("authentication failed")
