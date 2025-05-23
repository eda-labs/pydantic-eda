# generated by datamodel-codegen:
#   filename:  siteinfo.json

from __future__ import annotations
from typing import Annotated, Any, Dict, List, Optional
from pydantic import BaseModel, Field, RootModel


class AppGroupVersion(BaseModel):
    groupVersion: Optional[str] = None
    version: Optional[str] = None


class ErrorIndex(BaseModel):
    index: Optional[int] = None


class ErrorItem(BaseModel):
    error: Optional[Dict[str, Any]] = None
    type: Optional[str] = None


class ErrorResponse(BaseModel):
    """
    Generic error response for REST APIs
    """

    code: Annotated[
        int, Field(description="the numeric HTTP error code for the response.")
    ]
    details: Annotated[
        Optional[str], Field(description="The optional details of the error response.")
    ] = None
    dictionary: Annotated[
        Optional[Dict[str, Any]],
        Field(
            description='Dictionary/map of associated data/information relevant to the error.\nThe error "message" may contain {{name}} escapes that should be substituted\nwith information from this dictionary.'
        ),
    ] = None
    errors: Annotated[
        Optional[List[ErrorItem]],
        Field(
            description="Collection of errors in cases where more than one exists. This needs to be\nflexible so we can support multiple formats"
        ),
    ] = None
    index: Optional[ErrorIndex] = None
    internal: Annotated[
        Optional[int],
        Field(
            description="Internal error code in cases where we don't have an array of errors"
        ),
    ] = None
    message: Annotated[
        str, Field(description="The basic text error message for the error response.")
    ]
    ref: Annotated[
        Optional[str],
        Field(
            description="Reference to the error source. Should typically be the URI of the request"
        ),
    ] = None
    type: Annotated[
        Optional[str],
        Field(
            description="URI pointing at a document that describes the error and mitigation steps\nIf there is no document, point to the RFC for the HTTP error code"
        ),
    ] = None


class K8SPatchOp(BaseModel):
    from_: Annotated[Optional[str], Field(alias="from")] = None
    op: str
    path: str
    value: Optional[Dict[str, Any]] = None
    x_permissive: Annotated[Optional[bool], Field(alias="x-permissive")] = None


class Patch(RootModel[List[K8SPatchOp]]):
    root: List[K8SPatchOp]


class Resource(BaseModel):
    kind: Optional[str] = None
    name: Optional[str] = None
    namespaced: Optional[bool] = None
    readOnly: Optional[bool] = None
    singularName: Optional[str] = None
    uiCategory: Optional[str] = None


class ResourceHistoryEntry(BaseModel):
    author: Optional[str] = None
    changeType: Optional[str] = None
    commitTime: Optional[str] = None
    hash: Optional[str] = None
    message: Optional[str] = None
    transactionId: Optional[int] = None


class ResourceList(BaseModel):
    apiVersion: Optional[str] = None
    groupVersion: Optional[str] = None
    kind: Optional[str] = None
    resources: Optional[List[Resource]] = None


class StatusDetails(BaseModel):
    group: Optional[str] = None
    kind: Optional[str] = None
    name: Optional[str] = None


class UIResult(RootModel[str]):
    root: str


class BannerSpec(BaseModel):
    """
    BannerSpec allows the configuration of login and MOTD (Message of the Day) banners on selected nodes. The banners can be applied to specific nodes or selected using label selectors.
    """

    loginBanner: Annotated[
        Optional[str],
        Field(
            description="This is the login banner displayed before a user has logged into the Node.",
            title="Login Banner",
        ),
    ] = None
    motd: Annotated[
        Optional[str],
        Field(
            description="This is the MOTD banner displayed after a user has logged into the Node.",
            title="MOTD",
        ),
    ] = None
    nodeSelector: Annotated[
        Optional[List[str]],
        Field(
            description="Labe selector to select nodes on which to configure the banners.",
            title="Node Selector",
        ),
    ] = None
    nodes: Annotated[
        Optional[List[str]],
        Field(
            description="List of nodes on which to configure the banners.",
            title="Nodes",
        ),
    ] = None


class BannerStatus(BaseModel):
    """
    BannerStatus defines the observed state of Banner
    """

    nodes: Annotated[
        Optional[List[str]],
        Field(
            description="List of nodes this banner has been applied to", title="Nodes"
        ),
    ] = None


class BannerDeletedResourceEntry(BaseModel):
    commitTime: Optional[str] = None
    hash: Optional[str] = None
    name: Optional[str] = None
    namespace: Optional[str] = None
    transactionId: Optional[int] = None


class BannerDeletedResources(RootModel[List[BannerDeletedResourceEntry]]):
    root: List[BannerDeletedResourceEntry]


class BannerMetadata(BaseModel):
    annotations: Optional[Dict[str, str]] = None
    labels: Optional[Dict[str, str]] = None
    name: Annotated[
        str,
        Field(
            max_length=253,
            pattern="^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$",
        ),
    ]
    namespace: str


class AppGroup(BaseModel):
    apiVersion: Optional[str] = None
    kind: Optional[str] = None
    name: Optional[str] = None
    preferredVersion: Optional[AppGroupVersion] = None
    versions: Optional[List[AppGroupVersion]] = None


class ResourceHistory(RootModel[List[ResourceHistoryEntry]]):
    root: List[ResourceHistoryEntry]


class Status(BaseModel):
    apiVersion: Optional[str] = None
    details: Optional[StatusDetails] = None
    kind: Optional[str] = None
    string: Optional[str] = None


class Banner(BaseModel):
    """
    Banner is the Schema for the banners API
    """

    apiVersion: str
    kind: str
    metadata: BannerMetadata
    spec: Annotated[
        BannerSpec,
        Field(
            description="BannerSpec allows the configuration of login and MOTD (Message of the Day) banners on selected nodes. The banners can be applied to specific nodes or selected using label selectors.",
            title="Specification",
        ),
    ]
    status: Annotated[
        Optional[BannerStatus],
        Field(
            description="BannerStatus defines the observed state of Banner",
            title="Status",
        ),
    ] = None


class BannerList(BaseModel):
    """
    BannerList is a list of banners
    """

    apiVersion: str
    items: Optional[List[Banner]] = None
    kind: str
