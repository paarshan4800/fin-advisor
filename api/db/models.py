from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class User(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    updated_at: datetime

class Account(BaseModel):
    id: str
    user_id: str
    account_number: str
    created_at: datetime
    updated_at: datetime

class Merchant(BaseModel):
    id: str
    name: str
    type: str
    category: str
    created_at: datetime
    updated_at: datetime

class Transaction(BaseModel):
    id: str
    transaction_id: str
    user_id: str
    from_account_id: str
    to_account_id: Optional[str]
    merchant_id: str
    amount: float
    currency: str
    transaction_type: str
    transaction_mode: str
    status: str
    initiated_at: datetime
    completed_at: Optional[datetime]
    failed_at: Optional[datetime]
    remarks: Optional[str]
    description: str
    reference_number: str
    order_id: str
    created_at: datetime
    updated_at: datetime