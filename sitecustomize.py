import sys
import pysqlite3
sys.modules["sqlite3"] = pysqlite3
sys.modules["sqlalchemy.dialects.sqlite.pysqlite"] = pysqlite3
