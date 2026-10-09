"""Create/refresh the local synthetic demo dataset and print a concise summary."""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bri.reporting import kpis, to_frame
from bri.seed import seed
from bri.storage import Repository


def main() -> None:
    repository = Repository(PROJECT_ROOT / "data" / "business_requests.db")
    repository.initialize()
    created = seed(repository)
    summary = kpis(to_frame(repository.report_rows()))
    print(f"Synthetic seed complete: {created} new request(s).")
    print(f"Stored synthetic requests: {summary['requests']}")
    print(f"Review rate: {summary['review_rate']:.1%}")
    print(f"Correction rate: {summary['correction_rate']:.1%}")


if __name__ == "__main__":
    main()
