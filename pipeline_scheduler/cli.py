import argparse
import sys

from pipeline_scheduler.loader import RetryPlanLoaderError, load_retry_plan
from pipeline_scheduler.queue import get_queue_summary
from pipeline_scheduler.report import write_schedule_json
from pipeline_scheduler.scheduler import build_retry_schedule


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pipeline-scheduler",
        description="Create retry schedules from retry plans.",
    )

    subparsers = parser.add_subparsers(dest="command")

    schedule_parser = subparsers.add_parser(
        "schedule",
        help="Build a retry schedule from a retry plan.",
    )
    schedule_parser.add_argument(
        "retry_plan",
        help="Path to retry_plan.json.",
    )
    schedule_parser.add_argument(
        "--generated-at",
        default=None,
        help="Override schedule generated_at timestamp.",
    )
    schedule_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show scheduled retry tasks.",
    )
    schedule_parser.add_argument(
        "--json",
        action="store_true",
        help="Write retry schedule as JSON.",
    )
    schedule_parser.add_argument(
        "--output",
        default="outputs/schedule.json",
        help="Output path for JSON schedule report.",
    )

    return parser


def run_schedule(args: argparse.Namespace) -> int:
    try:
        retry_plan = load_retry_plan(args.retry_plan)
        schedule = build_retry_schedule(
            retry_plan,
            generated_at=args.generated_at,
        )
        summary = get_queue_summary(schedule)

        if args.json:
            output_path = write_schedule_json(schedule, args.output)
            print(f"JSON schedule written: {output_path}")
            return 0
    except (RetryPlanLoaderError, ValueError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print("Pipeline Scheduler")
    print("==================")
    print(f"Pipeline ID: {schedule.pipeline_id}")
    print(f"Status: {schedule.status}")
    print(f"Generated At: {schedule.generated_at}")
    print()
    print("Queue Summary")
    print("-------------")
    print(f"Total Tasks: {summary['total_tasks']}")
    print(f"Queued Tasks: {summary['queued_tasks']}")
    print(f"First Run At: {summary['first_run_at']}")
    print(f"Last Run At: {summary['last_run_at']}")

    if args.verbose:
        print()
        print("Scheduled Tasks")
        print("---------------")
        for task in schedule.tasks:
            print(
                f"- {task.node_id} | {task.node_name} | "
                f"attempt={task.next_attempt} | "
                f"delay={task.delay_seconds} | "
                f"run_at={task.run_at} | "
                f"status={task.status}"
            )

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "schedule":
        return run_schedule(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
