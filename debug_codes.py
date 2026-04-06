import os
from dotenv import load_dotenv
from ravendb import DocumentStore

load_dotenv()

RAVEN_URL = os.getenv('RAVEN_URL', 'http://localhost:8080')
RAVEN_DB  = os.getenv('RAVEN_DATABASE', 'shizu_bot')
CERT_PATH = os.getenv('RAVEN_CERT_PATH')
DOC_ID    = "easteregg/codes"

def get_store():
    urls = RAVEN_URL.split(',')
    store = DocumentStore(urls=urls, database=RAVEN_DB)
    if CERT_PATH and os.path.exists(CERT_PATH):
        if hasattr(store, 'certificate_pem_path'):
            store.certificate_pem_path = CERT_PATH
        else:
            store.certificate = CERT_PATH
    store.conventions.disable_topology_updates = True
    store.initialize()
    return store

store = get_store()

with store.open_session() as session:
    doc = session.load(DOC_ID)
    if doc:
        print(f"Document found: {DOC_ID}")
        if isinstance(doc, dict):
            codes = doc.get("codes", [])
            print(f"Type: dict. Codes count: {len(codes)}")
        else:
            codes = getattr(doc, "codes", [])
            print(f"Type: {type(doc)}. Codes count: {len(codes)}")
        
        if codes:
            sample = codes[0]
            print(f"Sample entry type: {type(sample)}")
            print(f"Sample entry: {sample}")
            
            unused = []
            for entry in codes:
                # Mirroring app.py logic exactly
                is_dict = isinstance(entry, dict)
                used = entry.get("used", True) if is_dict else getattr(entry, "used", True)
                if not used:
                    unused.append(entry)
            
            print(f"App.py logic would find {len(unused)} unused codes.")
    else:
        print("Document NOT found.")

store.close()
