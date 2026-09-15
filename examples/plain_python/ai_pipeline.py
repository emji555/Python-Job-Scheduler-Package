"""AI-style pipeline example (illustrative only)."""

from package_name import chain, configure, job

configure(backend="eager")


@job
def preprocess_image(path: str) -> str:
    return f"tensor:{path}"


@job
def run_inference(tensor: str) -> dict[str, float]:
    return {"score": 0.97, "label": 1.0}


@job
def generate_report(result: dict[str, float]) -> str:
    return f"label={result['label']} score={result['score']}"


@job
def notify_clinician(report: str) -> str:
    return f"notified:{report}"


if __name__ == "__main__":
    handle = chain(
        preprocess_image.s("scan.png"),
        run_inference,
        generate_report,
        notify_clinician,
    ).dispatch()
    print(handle.result() if handle else None)
