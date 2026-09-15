"""Simple microbenchmarks — not marketing claims."""

from __future__ import annotations

import time

from workloom import configure, job


def main() -> None:
    configure(backend="eager")

    @job
    def nop(x: int) -> int:
        return x

    n = 5000
    start = time.perf_counter()
    for i in range(n):
        nop.dispatch(i).result()
    elapsed = time.perf_counter() - start
    print(f"{n} eager dispatches in {elapsed:.3f}s ({n / elapsed:.0f} jobs/s)")


if __name__ == "__main__":
    main()
