# generated by datamodel-codegen:
#   filename:  os.json

from __future__ import annotations
from typing import Annotated, Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, RootModel
from enum import Enum


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


class DeployImageSpecChecksChecks(Enum):
    """
    Checks to run before (pre) and after (post) any image changes
    """

    Interface = "Interface"
    DefaultBGP = "DefaultBGP"
    PingISL = "PingISL"
    PingSystem = "PingSystem"


class DeployImageSpecChecks(BaseModel):
    checks: Annotated[
        Union[List[str], DeployImageSpecChecksChecks],
        Field(
            description="Checks to run before (pre) and after (post) any image changes",
            title="checks",
        ),
    ]
    force: Annotated[
        bool, Field(description="Do not prompt for user input, even if checks fail")
    ]
    skip: Annotated[bool, Field(description="Do not run any checks")]


class DeployImageSpecDrains(BaseModel):
    interfaceDisableSelectors: Annotated[
        Optional[List[str]], Field(title="InterfaceDisableSelectors")
    ] = None
    minimumWaitTime: Annotated[Optional[int], Field(title="minimumWaitTime")] = None
    skip: Annotated[
        Optional[bool], Field(description="Do not run any drains", title="skip")
    ] = None


class DeployImageSpecPrompt(Enum):
    AfterPreChecks = "AfterPreChecks"
    AfterPostChecks = "AfterPostChecks"


class DeployImageSpecTranch(BaseModel):
    name: Annotated[Optional[str], Field(title="name")] = None
    nodeSelector: Annotated[Optional[List[str]], Field(title="nodeSelector")] = None


class DeployImageSpec(BaseModel):
    """
    DeployImageSpec defines the desired state of DeployImage
    """

    canaries: Annotated[Optional[List[str]], Field(title="canaries")] = None
    checks: Annotated[Optional[DeployImageSpecChecks], Field(title="checks")] = None
    drains: Annotated[Optional[DeployImageSpecDrains], Field(title="drains")] = None
    nodeProfile: Annotated[Optional[str], Field(title="nodeProfile")] = None
    nodeSelector: Annotated[Optional[List[str]], Field(title="nodeSelector")] = None
    nodes: Annotated[Optional[List[str]], Field(title="nodes")] = None
    prompt: Annotated[
        Optional[Union[List[str], DeployImageSpecPrompt]], Field(title="prompt")
    ] = None
    tranches: Annotated[
        Optional[List[DeployImageSpecTranch]], Field(title="tranches")
    ] = None
    type: Annotated[Literal["node", "nodeselector", "tranche"], Field(title="type")]
    version: Annotated[Optional[str], Field(title="version")] = None


class DeployImageStatus(BaseModel):
    """
    DeployImageStatus defines the observed state of DeployImage
    """

    id: Annotated[Optional[int], Field(description="Id", title="ID")] = None
    result: Annotated[
        Optional[str], Field(description="Aggregate result of the Flow", title="Result")
    ] = None


class DeployImageDeletedResourceEntry(BaseModel):
    commitTime: Optional[str] = None
    hash: Optional[str] = None
    name: Optional[str] = None
    namespace: Optional[str] = None
    transactionId: Optional[int] = None


class DeployImageDeletedResources(RootModel[List[DeployImageDeletedResourceEntry]]):
    root: List[DeployImageDeletedResourceEntry]


class DeployImageMetadata(BaseModel):
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


class DeployImage(BaseModel):
    """
    DeployImage is the Schema for the deployimages API
    """

    apiVersion: str
    kind: str
    metadata: DeployImageMetadata
    spec: Annotated[
        DeployImageSpec,
        Field(
            description="DeployImageSpec defines the desired state of DeployImage",
            title="Specification",
        ),
    ]
    status: Annotated[
        Optional[DeployImageStatus],
        Field(
            description="DeployImageStatus defines the observed state of DeployImage",
            title="Status",
        ),
    ] = None


class DeployImageList(BaseModel):
    """
    DeployImageList is a list of deployimages
    """

    apiVersion: str
    items: Optional[List[DeployImage]] = None
    kind: str
