from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from ..core.config import settings
from .examples import ex_client_config


class TOKENENDPOINTAUTHMETHODS(str, Enum):
    client_secret_basic = "client_secret_basic"
    client_secret_post = "client_secret_post"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class ClientConfigurationBase(BaseModel):
    client_id: str = Field(default=settings.OIDC_CLIENT_ID)
    client_name: str = Field(default=settings.OIDC_CLIENT_NAME)
    response_types: list[str] = Field(default=["code", "id_token", "token"])
    redirect_uris: list[str]
    token_endpoint_auth_method: TOKENENDPOINTAUTHMETHODS = Field(
        default=TOKENENDPOINTAUTHMETHODS.client_secret_basic
    )

    client_secret: str = Field(default=settings.OIDC_CLIENT_SECRET)

    model_config = ConfigDict(
        populate_by_name=True, json_schema_extra={"example": ex_client_config}
    )


class ClientConfiguration(ClientConfigurationBase):
    pass


class ClientConfigurationRead(ClientConfigurationBase):
    pass


class ClientConfigurationPatch(ClientConfigurationBase):
    client_id: str | None = None
    client_name: str | None = None
    response_types: list[str] | None = None
    redirect_uris: list[str] | None = None
    token_endpoint_auth_method: TOKENENDPOINTAUTHMETHODS | None = None
    client_secret: str | None = None

    pass
