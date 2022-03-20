import os
MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PWD", "root_raw_password"),
    "database": os.environ.get("MYSQL_DB", "switch"),
    "port": 3306,
    "charset": "utf8mb4",
}