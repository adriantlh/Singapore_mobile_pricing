from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ProductVariantInput(BaseModel):
    brand_name: str
    family_name: str
    family_slug: str
    variant_name: str
    attributes: Dict[str, Any] = Field(default_factory=dict)
    source_name: str
    source_url: Optional[str] = None
    price: float
    currency: str = "SGD"
    url: str
    image_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
