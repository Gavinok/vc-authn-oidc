import time
from typing_extensions import TypedDict
from pydantic import BaseModel, ConfigDict, Field

from .examples import ex_ver_config
from ..core.config import settings
from .helpers import replace_proof_variables


# Slightly modified from ACAPY models.
class AttributeFilter(BaseModel):
    schema_id: str | None = None
    cred_def_id: str | None = None
    schema_name: str | None = None
    schema_issuer_did: str | None = None
    schema_version: str | None = None
    issuer_did: str | None = None


class ReqAttr(BaseModel):
    names: list[str]
    label: str | None = None
    restrictions: list[AttributeFilter]


class ReqPred(BaseModel):
    name: str
    label: str | None = None
    restrictions: list[AttributeFilter]
    p_value: int | str
    p_type: str


class VerificationProofRequest(BaseModel):
    name: str | None = None
    version: str = Field(pattern="[0-9](.[0.9])*", examples=["0.0.1"])
    non_revoked: str | None = None
    requested_attributes: list[ReqAttr]
    requested_predicates: list[ReqPred]


class MetaData(BaseModel):
    title: dict[str, str] | None = Field(default=None)
    claims: dict[str, list[str]] | None = Field(default=None)


class VerificationConfigBase(BaseModel):
    subject_identifier: str = Field()
    proof_request: VerificationProofRequest = Field()
    generate_consistent_identifier: bool | None = Field(default=False)
    include_v1_attributes: bool | None = Field(default=False)
    metadata: MetaData | None = Field(default=None)

    def get_now(self) -> int:
        return int(time.time())

    def generate_proof_request(self):
        result = {
            "name": "proof_requested",
            "version": "0.0.1",
            "requested_attributes": {},
            "requested_predicates": {},
        }
        if self.proof_request.name:
            result["name"] = self.proof_request.name
        for i, req_attr in enumerate(self.proof_request.requested_attributes):
            label = req_attr.label or "req_attr_" + str(i)
            result["requested_attributes"][label] = req_attr.model_dump(
                exclude_none=True
            )
            if settings.SET_NON_REVOKED:
                result["requested_attributes"][label]["non_revoked"] = {
                    "from": int(time.time()),
                    "to": int(time.time()),
                }
        for i, req_pred in enumerate(self.proof_request.requested_predicates):
            label = req_pred.label or "req_pred_" + str(i)
            result["requested_predicates"][label] = req_pred.model_dump(
                exclude_none=True
            )
            if settings.SET_NON_REVOKED:
                result["requested_predicates"][label]["non_revoked"] = {
                    "from": int(time.time()),
                    "to": int(time.time()),
                }
        # Recursively check for subistitution variables and invoke replacement function
        result = replace_proof_variables(result)
        return result

    model_config = ConfigDict(json_schema_extra={"example": ex_ver_config})


class VerificationConfig(VerificationConfigBase):
    ver_config_id: str = Field()


class VerificationConfigRead(VerificationConfigBase):
    ver_config_id: str = Field()


class VerificationConfigPatch(VerificationConfigBase):
    subject_identifier: str | None = Field(None)
    proof_request: VerificationProofRequest | None = Field(None)

    pass
