from pydantic import BaseModel
from typing import List, Dict, Any


class TenantConfig(BaseModel):
    tenant_id: str
    name: str
    system_prompt: str
    kb_namespace: str
    enabled_tools: List[str]
    escalation_contact: str
    business_rules: Dict[str, Any] = {}
