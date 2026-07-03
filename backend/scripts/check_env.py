from __future__ import annotations

import os
import sys

REQUIRED = [
    "DATABASE_URL",
    "REDIS_URL",
    "JWT_SECRET_KEY",
    "DEFAULT_LLM_PROVIDER",
    "DEFAULT_EMBEDDING_PROVIDER",
]

PROVIDER_KEYS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
}


def main() -> int:
    errors: list[str] = []
    for name in REQUIRED:
        if not os.getenv(name):
            errors.append(f"{name} is required.")

    for provider_env in ("DEFAULT_LLM_PROVIDER", "DEFAULT_EMBEDDING_PROVIDER"):
        provider = (os.getenv(provider_env) or "mock").lower()
        key_name = PROVIDER_KEYS.get(provider)
        if key_name and not os.getenv(key_name):
            errors.append(f"{key_name} is required when {provider_env}={provider}.")

    if errors:
        print("[FAIL] Backend environment validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("[OK] Backend environment validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
