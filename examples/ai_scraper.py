"""Run an AI Scraper engine or retrieve an existing task through LangChain tools."""

import argparse
import json

from langchain_scrapeless import ScrapelessAIScraperResultTool, ScrapelessAIScraperTool
from langchain_scrapeless.tools.ai_scraper import ENGINE_SCHEMAS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("engine", choices=sorted(ENGINE_SCHEMAS))
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--input-json", help="Engine input JSON, including supported lifecycle options."
    )
    source.add_argument(
        "--task-id", help="Retrieve an existing task instead of submitting one."
    )
    parser.add_argument("--no-wait", action="store_true")
    args = parser.parse_args()
    if args.task_id:
        result = ScrapelessAIScraperResultTool().invoke(
            {
                "engine": args.engine,
                "task_id": args.task_id,
                "wait": not args.no_wait,
            }
        )
    else:
        actor_input = json.loads(args.input_json)
        if not isinstance(actor_input, dict):
            parser.error("--input-json must be a JSON object")
        result = ScrapelessAIScraperTool().invoke(
            {
                "engine": args.engine,
                "input": {
                    **actor_input,
                    "wait": not args.no_wait,
                    "output_format": "json",
                },
            }
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
