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

else:
    print("authentication failed")