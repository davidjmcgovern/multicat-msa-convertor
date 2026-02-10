"""Distributor configuration model and loader."""

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class DistributorConfig(BaseModel):
    distributor_id: str = Field(default="10094001", max_length=8)
    name: str = Field(default="", max_length=32)
    address: str = Field(default="", max_length=90)
    city: str = Field(default="", max_length=25)
    state: str = Field(default="", max_length=2)
    zip_code: str = Field(default="", max_length=9)
    country: str = Field(default="USA", max_length=3)
    contact_last_name: str = Field(default="", max_length=20)
    contact_first_name: str = Field(default="", max_length=20)
    contact_phone: str = Field(default="", max_length=10)
    contact_fax: str = Field(default="", max_length=10)
    contact_email: str = Field(default="", max_length=60)
    test_mode: bool = True


def load_config(path: str | Path) -> DistributorConfig:
    """Load distributor config from a YAML file."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return DistributorConfig(**data)
