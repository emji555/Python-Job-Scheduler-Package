"""Data pipeline example using chain()."""

from workloom import chain, configure, job

configure(backend="eager")


@job
def import_data() -> list[int]:
    return [1, 2, 3]


@job
def validate_data(rows: list[int]) -> list[int]:
    return [r for r in rows if r > 0]


@job
def calculate_statistics(rows: list[int]) -> dict[str, float]:
    return {"count": float(len(rows)), "sum": float(sum(rows))}


@job
def generate_report(stats: dict[str, float]) -> str:
    return f"count={stats['count']} sum={stats['sum']}"


if __name__ == "__main__":
    handle = chain(import_data, validate_data, calculate_statistics, generate_report).dispatch()
    print(handle.result() if handle else None)
