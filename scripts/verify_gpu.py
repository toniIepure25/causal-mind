from __future__ import annotations

import sys


def main() -> int:
    import torch

    print(f"torch: {torch.__version__}")
    print(f"cuda available: {torch.cuda.is_available()}")
    if not torch.cuda.is_available():
        print("FAIL: cuda not available")
        return 1
    print(f"device: {torch.cuda.get_device_name(0)}")
    x = torch.randn(1024, 1024, device="cuda", dtype=torch.bfloat16)
    y = (x @ x).sum().item()
    print(f"bf16 matmul ok: {y != 0}")
    print(f"sdpa available: {torch.backends.cuda.sdp_is_available()}")
    print("GPU-OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
