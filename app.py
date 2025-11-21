import os
from dotenv import load_dotenv
load_dotenv()

import logging
from datetime import datetime

from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient, ContentSettings, PublicAccess
from azure.data.tables import TableServiceClient

# ================================
# CONFIGURATION
# ================================
PORT = int(os.getenv("PORT", 8080))
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_BYTES", 10 * 1024 * 1024))  # 10 MB default

CONTAINER = os.environ.get("IMAGES_CONTAINER", "affordable-resources")
AZURE_CONN = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
TABLE_NAME = os.environ.get("RESOURCES_TABLE", "resources")

app = Flask(__name__, static_folder="static", template_folder="templates")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("affordable_it_resources")

if not AZURE_CONN:
    logger.warning("AZURE_STORAGE_CONNECTION_STRING is not set. Upload/resources APIs will fail without it.")


# ================================
# HELPERS
# ================================
def get_blob_service():
    if not AZURE_CONN:
        raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING not configured")
    return BlobServiceClient.from_connection_string(AZURE_CONN)


def ensure_container_public():
    """Create the blob container if needed and make it public-read."""
    bsc = get_blob_service()
    cc = bsc.get_container_client(CONTAINER)

    try:
        cc.create_container()
        logger.info(f"Created container {CONTAINER}")
    except Exception:
        # Probably already exists
        pass

    try:
        cc.set_container_access_policy(public_access=PublicAccess.Container)
        logger.info(f"Set public access for container {CONTAINER}")
    except Exception as e:
        logger.warning(f"Could not set public access policy: {e}")

    return cc


def get_table_client():
    """Create (if needed) and return the Azure Table client."""
    if not AZURE_CONN:
        raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING not configured")

    tsc = TableServiceClient.from_connection_string(AZURE_CONN)
    table_client = tsc.get_table_client(TABLE_NAME)

    try:
        table_client.create_table()
        logger.info(f"Created table {TABLE_NAME}")
    except Exception:
        # Already exists
        pass

    return table_client


def allowed_file_size(content_length):
    return content_length and int(content_length) <= MAX_FILE_SIZE


# ================================
# CORE ROUTES
# ================================
@app.get("/")
def index():
    # Resource hub page (card layout)
    return render_template("index.html")


@app.get("/submit")
def submit():
    # Submit-a-resource page
    return render_template("submit.html")


@app.get("/health")
def health():
    return jsonify(ok=True, service="affordable-it-resources")


# ================================
# IMAGE UPLOAD / GALLERY
# ================================
@app.post("/api/v1/upload")
def upload():
    if "file" not in request.files:
        return jsonify(ok=False, error="No file uploaded"), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify(ok=False, error="Empty filename"), 400

    if request.content_length and not allowed_file_size(request.content_length):
        return jsonify(ok=False, error=f"File too large (max {MAX_FILE_SIZE} bytes)"), 413

    filename = secure_filename(file.filename)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    blob_name = f"{timestamp}-{filename}"

    try:
        cc = ensure_container_public()
        blob_client = cc.get_blob_client(blob_name)

        data = file.read()
        if len(data) > MAX_FILE_SIZE:
            return jsonify(ok=False, error=f"File too large (max {MAX_FILE_SIZE} bytes)"), 413

        cs = ContentSettings(content_type=file.mimetype or "application/octet-stream")
        blob_client.upload_blob(data, overwrite=True, content_settings=cs)

        url = blob_client.url
        logger.info(f"Uploaded image {blob_name} -> {url}")
        return jsonify(ok=True, url=url)
    except Exception as e:
        logger.exception("Upload failed")
        return jsonify(ok=False, error=str(e)), 500


@app.get("/api/v1/gallery")
def gallery():
    try:
        bsc = get_blob_service()
        cc = bsc.get_container_client(CONTAINER)
        urls = [f"{cc.url}/{b.name}" for b in cc.list_blobs()]
        urls.sort(reverse=True)
        return jsonify(ok=True, gallery=urls)
    except Exception as e:
        logger.exception("Could not list gallery")
        return jsonify(ok=False, error=str(e)), 500


# ================================
# RESOURCES API (TABLE STORAGE)
# ================================
@app.post("/api/v1/resources")
def create_resource():
    """
    Create a new resource in Azure Table Storage.
    JSON body:
    {
      "name": "Girls Who Code",
      "url": "https://girlswhocode.com",
      "category": "coding",
      "tags": ["women", "students"],
      "notes": "Free coding programs"
    }
    """
    try:
        data = request.get_json() or {}
    except Exception:
        return jsonify(ok=False, error="Invalid JSON"), 400

    name = data.get("name")
    url = data.get("url")

    if not name or not url:
        return jsonify(ok=False, error="'name' and 'url' required"), 400

    category = (data.get("category") or "general").strip().lower()
    tags = data.get("tags") or []
    if isinstance(tags, list):
        tags_str = ",".join(t.strip() for t in tags if t)
    else:
        tags_str = str(tags)

    notes = data.get("notes") or ""

    table_client = get_table_client()
    now = datetime.utcnow()
    row_key = now.strftime("%Y%m%dT%H%M%S%f")

    entity = {
        "PartitionKey": category or "general",
        "RowKey": row_key,
        "name": name,
        "url": url,
        "category": category or "general",
        "tags": tags_str,
        "notes": notes,
        "created_at": now.isoformat() + "Z",
    }

    try:
        table_client.create_entity(entity=entity)
        logger.info(f"Created resource entity {row_key} in table {TABLE_NAME}")
        return jsonify(ok=True, resource=entity), 201
    except Exception as e:
        logger.exception("Failed to create resource")
        return jsonify(ok=False, error=str(e)), 500


@app.get("/api/v1/resources")
def list_resources():
    """
    List all resources stored in Azure Table Storage.
    (You can use this later if you want a dynamic hub.)
    """
    try:
        table_client = get_table_client()
        entities = list(table_client.list_entities())

        resources = []
        for e in entities:
            tags_raw = e.get("tags") or ""
            tags = [t for t in tags_raw.split(",") if t.strip()] if tags_raw else []

            resources.append({
                "partition": e.get("PartitionKey"),
                "id": e.get("RowKey"),
                "name": e.get("name"),
                "url": e.get("url"),
                "category": e.get("category"),
                "tags": tags,
                "notes": e.get("notes"),
                "created_at": e.get("created_at"),
            })

        resources.sort(key=lambda r: r.get("created_at") or "", reverse=True)
        return jsonify(ok=True, resources=resources)
    except Exception as e:
        logger.exception("Failed to list resources")
        return jsonify(ok=False, error=str(e)), 500


# ================================
# ENTRYPOINT
# ================================
if __name__ == "__main__":
    # Make sure your env var is set, then:
    #   python3 app.py
    app.run(host="0.0.0.0", port=PORT)
