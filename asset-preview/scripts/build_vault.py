#!/usr/bin/env python3
"""자산 시드 JSON을 AES-GCM으로 암호화해 data/vault.enc.json 을 만든다.

키(32바이트 난수, base64url)는 표준출력으로만 보여준다. 이 키는 URL 조각(#k=…)에만 쓰이며
서버로 전송되지 않는다.

사용:
    python scripts/build_vault.py seed.json            # 새 키 생성
    python scripts/build_vault.py seed.json --key KEY  # 기존 키 유지
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import secrets
import sys

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ITERATIONS = 200000


def b64(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")


def new_key() -> str:
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("ascii").rstrip("=")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("seed")
    ap.add_argument("--key")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    with open(args.seed, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    key = args.key or new_key()
    salt = secrets.token_bytes(16)
    iv = secrets.token_bytes(12)

    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERATIONS)
    aes_key = kdf.derive(key.encode("utf-8"))
    plaintext = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ct = AESGCM(aes_key).encrypt(iv, plaintext, b"assetq-vault-v1")

    vault = {
        "format": "asset-quest-vault",
        "v": 1,
        "alg": "AES-GCM-256",
        "kdf": {"name": "PBKDF2-SHA256", "iterations": ITERATIONS, "salt": b64(salt)},
        "iv": b64(iv),
        "ciphertext": b64(ct),
        "note": "암호문만 공개됩니다. 키는 URL 조각(#k=…)으로만 전달되며 서버에 남지 않습니다.",
    }

    out = args.out or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "vault.enc.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(vault, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print("wrote", out)
    print("KEY:", key)
    print("URL: https://seouna7.github.io/Asset-dashboard/#k=" + key)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
