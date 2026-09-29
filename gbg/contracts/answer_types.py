"""답 형식 명세(worldgen answer_types)를 닫힌 슬롯으로 바꾸고, 값이 명세를 따르는지 검사한다.

명세: {"type": "integer" | "boolean" | "enum" (values) | "string" (format) | "array" (items, ordered) |
       "tuple" (items, names), "nullable": bool, "note": str}
"""
from pydantic import JsonValue

from .schemas import Slot

_SCALAR = {"integer": "int", "boolean": "bool", "string": "id"}


def slot_from_spec(name: str, spec: dict) -> Slot:
    t, nullable = spec["type"], bool(spec.get("nullable", False))
    if t == "enum":
        return Slot(name=name, type="enum", options=list(spec["values"]), nullable=nullable, note=spec.get("note"))
    if t == "array":
        return Slot(name=name, type="list" if spec.get("ordered", True) else "set", nullable=nullable,
                    items=spec.get("items"), note=spec.get("note"))
    if t in _SCALAR:
        return Slot(name=name, type=_SCALAR[t], nullable=nullable, format=spec.get("format"), note=spec.get("note"))
    raise ValueError(f"{name}: 알 수 없는 답 형식 '{t}'")


def check_value(spec: dict, v: JsonValue) -> bool:
    """원소 형식 명세를 재귀적으로 검사한다. True와 1은 다르다."""
    if v is None:
        return bool(spec.get("nullable", False))
    t = spec["type"]
    if t == "integer":
        return isinstance(v, int) and not isinstance(v, bool)
    if t == "boolean":
        return isinstance(v, bool)
    if t == "string":
        return isinstance(v, str)
    if t == "enum":
        return any(type(o) is type(v) and o == v for o in spec["values"])
    if t == "array":
        if not isinstance(v, list):
            return False
        return "items" not in spec or all(check_value(spec["items"], x) for x in v)
    if t == "tuple":
        its = spec["items"]
        return isinstance(v, list) and len(v) == len(its) and all(check_value(s, x) for s, x in zip(its, v))
    raise ValueError(f"알 수 없는 형식 '{t}'")


def json_schema(spec: dict) -> dict:
    """에이전트 도구 인자용 JSON Schema."""
    t = spec["type"]
    if t == "enum":
        out = {"enum": list(spec["values"])}
    elif t == "array":
        out = {"type": "array", **({"items": json_schema(spec["items"])} if "items" in spec else {})}
    elif t == "tuple":
        out = {"type": "array", "prefixItems": [json_schema(s) for s in spec["items"]],
               "minItems": len(spec["items"]), "maxItems": len(spec["items"])}
    else:
        out = {"type": t}
    if spec.get("note"):
        out["description"] = spec["note"]
    return {"anyOf": [out, {"type": "null"}]} if spec.get("nullable") else out
