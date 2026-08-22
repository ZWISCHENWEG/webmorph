from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class VersionRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    version_range: str = Field(min_length=1)
    support_status: str = Field(min_length=1)
    status_class: Literal["y", "a", "n"]


class BrowserRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    browser_name: str = Field(min_length=1)
    versions: list[VersionRecord] = Field(min_length=1)


class CanIUseFeature(BaseModel):
    model_config = ConfigDict(extra="ignore")

    feature_name: str = Field(min_length=1)
    specification_url: HttpUrl
    specification_status: str = Field(min_length=1)
    global_usage_percentage: str
    global_usage_support: str
    global_usage_partial: str
    description: str = Field(min_length=1)
    compatibility_notes: str = Field(min_length=1)
    browser_support: list[BrowserRecord] = Field(min_length=1)

    @field_validator("global_usage_percentage", "global_usage_support", "global_usage_partial")
    @classmethod
    def validate_percentages(cls, v: str) -> str:
        v = v.strip()
        if not v.endswith("%"):
            raise ValueError("Percentage must end with %")
        try:
            float(v[:-1])
        except ValueError as e:
            raise ValueError("Percentage must be parseable as numeric") from e
        return v
