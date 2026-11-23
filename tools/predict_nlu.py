"""Evaluate a single notice from stdin with the deployed Relay model."""
import argparse
import json
import sys

from relay_intake import valid_date
from relay_interpretation import interpret
from relay_nlu import FIELDS, NoticeModel


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-date", default="")
    parser.add_argument("--member", action="append", default=[])
    parser.add_argument("--model")
    args = parser.parse_args()
    if args.source_date and not valid_date(args.source_date):
        parser.error("--source-date requires YYYY-MM-DD")
    text = sys.stdin.read(12001)
    if not text.strip() or len(text) > 12000:
        parser.error("Provide a notice of 1 to 12000 characters on stdin")
    model = NoticeModel(args.model) if args.model else NoticeModel()
    values, evidence = interpret(text, args.member, args.source_date, model)
    prediction = evidence.pop("_model", None)
    print(json.dumps({"plan":{field:values.get(field) for field in FIELDS},
                      "interpretation":prediction, "evidence":evidence}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
