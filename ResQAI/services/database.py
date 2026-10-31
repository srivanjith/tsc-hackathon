try:
    from pymongo import MongoClient, errors
    _PYMONGO_AVAILABLE = True
except ImportError:
    _PYMONGO_AVAILABLE = False
    MongoClient = None
    errors = None

from config import MONGO_URI, MONGO_DB

_client = None
_db = None
_error = None


def get_database():
    global _client, _db, _error
    if _db is not None:
        return _db
    if not _PYMONGO_AVAILABLE:
        _error = "PyMongo is not installed; running in local in-memory fallback mode."
        return None
    if not MONGO_URI:
        _error = "MONGO_URI is not configured; using in-memory demo mode."
        return None
    try:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2500, connectTimeoutMS=2500)
        _client.admin.command("ping")
        _db = _client[MONGO_DB]
        _error = None
        return _db
    except Exception as exc:
        _error = f"MongoDB unavailable: {exc.__class__.__name__}: {exc}"
        _client = None
        _db = None
        return None


def collection(name: str):
    """Returns a direct PyMongo collection reference, or None if in-memory demo mode."""
    db = get_database()
    return db[name] if db is not None else None


def connection_status():
    db=get_database()
    return (db is not None,_error or ("MongoDB Atlas connected" if db is not None else "Demo mode"))


def load_collection(name):
    db=get_database()
    if db is None: return None
    return list(db[name].find({}, {"_id":0}))


def replace_collection(name, documents):
    db=get_database()
    if db is None: return False
    db[name].delete_many({})
    if documents: db[name].insert_many(documents)
    return True


def create_document(collection, document):
    """Insert one document and return the inserted ID, or None in demo mode."""
    db=get_database()
    if db is None: return None
    result=db[collection].insert_one(document)
    return str(result.inserted_id)


def read_documents(collection, query=None):
    """Read documents matching a MongoDB query; returns None in demo mode."""
    db=get_database()
    if db is None: return None
    return list(db[collection].find(query or {}, {"_id":0}))


def update_document(collection, query, updates):
    """Update fields on matching documents; returns modified count or None."""
    db=get_database()
    if db is None: return None
    result=db[collection].update_many(query, {"$set":updates})
    return result.modified_count


def delete_document(collection, query):
    """Delete matching documents; returns deleted count or None."""
    db=get_database()
    if db is None: return None
    result=db[collection].delete_many(query)
    return result.deleted_count
