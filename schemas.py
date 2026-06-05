from pydantic import BaseModel, HttpUrl
from typing import Optional

class URLRequest(BaseModel):
    url: HttpUrl
    expires_in_days: Optional[int] = None