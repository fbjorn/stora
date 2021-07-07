import json
from typing import Optional, Type
from unittest.mock import Mock

import google.auth.credentials
from google.api_core.exceptions import GoogleAPIError
from google.cloud import firestore
from google.cloud.firestore_v1 import DocumentReference
from loguru import logger

from app.widgets.dialogs.error import show_error


def _make_credentials() -> Mock:
    return Mock(spec=google.auth.credentials.Credentials)


def get_firestore_emulator_client(project_name) -> firestore.Client:
    return firestore.Client(project=project_name, credentials=_make_credentials())


def convert_value(value: str, convert_to: Type):
    if convert_to == int:
        return int(value)
    elif convert_to == float:
        return float(value)
    elif convert_to in {dict, list}:
        return json.loads(value)


def update_document_value(
    doc_ref: DocumentReference, key: str, value, convert_to: Optional[Type] = None
) -> bool:
    if convert_to:
        value = convert_value(value, convert_to)
    try:
        doc_ref.update({key: value})
    except GoogleAPIError:
        logger.exception("Failed to update document {path}", path=doc_ref.path)
        show_error("Failed to update document!")
        return False
    return True
