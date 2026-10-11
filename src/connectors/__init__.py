"""Connector module for accessing isolated departmental storage silos."""
from src.connectors.base import Connector
from src.connectors.local import LocalFolderConnector

__all__ = [
    "Connector",
    "LocalFolderConnector",
]