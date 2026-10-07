from datetime import date

from pydantic import BaseModel, ConfigDict, model_validator


class Schema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, extra="forbid", str_strip_whitespace=True, allow_inf_nan=False
    )


class Patch(Schema):
    @model_validator(mode="before")
    @classmethod
    def reject_null_required(cls, data):
        if isinstance(data, dict):
            required = getattr(cls, "required_non_null", ())
            if any(k in data and data[k] is None for k in required):
                raise ValueError("Required fields cannot be null")
        return data


def not_future(value: date):
    if value > date.today():
        raise ValueError("Date cannot be in the future")
    return value
