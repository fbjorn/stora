from unittest.mock import Mock

import google.auth.credentials
from google.cloud import firestore


def _make_credentials() -> Mock:
    return Mock(spec=google.auth.credentials.Credentials)


def get_firestore_emulator_client(project_name) -> firestore.Client:
    return firestore.Client(project=project_name, credentials=_make_credentials())
