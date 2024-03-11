from typing import Union
import pydantic


class InferenceSchema(pydantic.BaseModel):
    usage_freq: int
    amount_spend: Union[int, float]
    uniq_merchant: int
    k: int
