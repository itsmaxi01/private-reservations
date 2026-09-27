from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

