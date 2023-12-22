#!/usr/bin/env python3

from typing import Dict, List, Mapping, Sequence, Union

_ImmutableJsonValue = Union[
    None,
    bool,
    int,
    float,
    str,
    Sequence["_ImmutableJsonValue"],
    Mapping[str, "_ImmutableJsonValue"],
]
ImmutableJsonArray = Sequence[_ImmutableJsonValue]
ImmutableJsonObject = Mapping[str, _ImmutableJsonValue]

_MutableJsonValue = Union[
    None,
    bool,
    int,
    float,
    str,
    List["_MutableJsonValue"],
    Dict[str, "_MutableJsonValue"],
]
MutableJsonArray = List[_MutableJsonValue]
MutableJsonObject = Dict[str, _MutableJsonValue]


def as_json_array(value: ImmutableJsonArray) -> MutableJsonArray:
    # pyre-ignore[7]
    return value


def as_json_object(value: ImmutableJsonObject) -> MutableJsonObject:
    # pyre-ignore[7]
    return value
