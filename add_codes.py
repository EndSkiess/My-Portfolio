"""
One-time script to populate RavenDB with fresh prize codes.
Run from the project root: python add_codes.py
"""
import os
import random
import string
from dotenv import load_dotenv
from ravendb import DocumentStore

load_dotenv()

RAVEN_URL = os.getenv('RAVEN_URL', 'http://localhost:8080')
RAVEN_DB  = os.getenv('RAVEN_DATABASE', 'shizu_bot')
CERT_PATH = os.getenv('RAVEN_CERT_PATH')
DOC_ID    = "easteregg/codes"
NUM_CODES = 20  # How many codes to generate

def make_code():
    part = lambda: ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"SKIES-{part()}-{part()}-{part()}"

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

new_codes = [{"code": make_code(), "used": False} for _ in range(NUM_CODES)]

with store.open_session() as session:
    doc = session.load(DOC_ID)
    doc_exists = doc is not None

if not doc_exists:
    # Document doesn't exist yet — create it fresh
    with store.open_session() as session:
        session.store({"codes": new_codes}, DOC_ID)
        session.save_changes()
    print(f"[+] Created new document '{DOC_ID}' with {NUM_CODES} codes.")
else:
    # Patch the existing document to push new codes into the array
    from ravendb import PatchOperation, PatchRequest

    script = "for (var i = 0; i < $newCodes.length; i++) { this.codes.push($newCodes[i]); }"
    patch_req = PatchRequest(script=script, values={"newCodes": new_codes})
    store.operations.send(PatchOperation(key=DOC_ID, change_vector=None, patch=patch_req))
    print(f"[+] Appended {NUM_CODES} new codes to existing document.")

store.close()
print("[+] Done. Secret page codes have been replenished!")
