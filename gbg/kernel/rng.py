"""이름 붙은 난수 흐름. 전역 random과 벽시계 시간은 쓰지 않는다.

stream(*name)은 호출할 때마다 (시드, 이름)으로 새 흐름을 만든다. 라운드를 넘어 이어지는 난수 상태가 없으므로
재개한 런도 같은 난수를 본다. 같은 흐름을 두 번 쓰지 않도록 이름에 날·라운드·작업을 넣는다.
"""
import hashlib
import random


class NamedRNG:
    def __init__(self, seed: int):
        self.seed = seed

    def stream(self, *name) -> random.Random:
        key = "|".join(str(x) for x in (self.seed, *name))
        return random.Random(int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big"))
