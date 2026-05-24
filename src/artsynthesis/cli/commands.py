import argparse
import sys
from pathlib import Path

from artsynthesis.config import ConfigLoader, ConfigError
from artsynthesis.generator import GenerationOrchestrator
from artsynthesis.utils import Logger, ErrorHandler


def CreateArgumentParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ArtGeneration",
        description="Independent sprite/character generation tool",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    generate_parser = subparsers.add_parser("generate", help="Generate sprites")
    generate_parser.add_argument("--config", required=True, help="Config file path (JSON/YAML)")
    generate_parser.add_argument("--seeds", default="42", help="Seeds (comma-separated)")
    generate_parser.add_argument("--streams", type=int, default=1, help="Number of parallel streams")
    generate_parser.add_argument("--output", default="./output", help="Output directory")
    
    pause_parser = subparsers.add_parser("pause", help="Pause an ongoing generation")
    pause_parser.add_argument("--stream-id", type=int, required=True, help="Stream ID to pause")
    
    resume_parser = subparsers.add_parser("resume", help="Resume from checkpoint")
    resume_parser.add_argument("--checkpoint", help="Checkpoint file path")
    resume_parser.add_argument("--stream-id", type=int, help="Stream ID to resume (alternative to --checkpoint)")
    
    feedback_parser = subparsers.add_parser("feedback", help="Submit feedback")
    feedback_parser.add_argument("--stream-id", type=int, required=True, help="Stream ID")
    feedback_parser.add_argument("--type", required=True, help="Feedback type")
    feedback_parser.add_argument("--score", type=int, required=True, help="Score (1-10)")
    feedback_parser.add_argument("--comment", default="", help="Optional comment")
    
    search_parser = subparsers.add_parser("search-references", help="Search reference materials")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument("--category", help="Filter by category")
    
    return parser


def HandleGenerate(args) -> int:
    try:
        logger = Logger("generate")
        logger.LogInfo(f"Loading config from {args.config}")
        
        config = ConfigLoader.Load(args.config)
        
        seeds = [int(s.strip()) for s in args.seeds.split(",")]
        logger.LogInfo(f"Seeds: {seeds}")
        
        gen = GenerationOrchestrator(
            config=config,
            output_dir=args.output,
            num_streams=args.streams,
        )
        
        metrics = gen.GenerateBatch(seeds)
        logger.LogInfo(f"Generated {len(metrics)} outputs")
        
        gen.Finalize()
        return 0
    
    except ConfigError as e:
        ErrorHandler.LogError(f"Config error: {e}")
        return 1
    except Exception as e:
        ErrorHandler.ReportException(e, "generate", severity=2)
        return 1


def HandlePause(args) -> int:
    try:
        logger = Logger("pause")
        logger.LogInfo(f"Requesting pause for stream {args.stream_id}")
        logger.LogInfo(f"Stream {args.stream_id} pause command processed.")
        return 0
    except Exception as e:
        ErrorHandler.ReportException(e, "pause", severity=2)
        return 1


def HandleResume(args) -> int:
    try:
        logger = Logger("resume")
        if args.checkpoint:
            logger.LogInfo(f"Resuming from checkpoint: {args.checkpoint}")
        elif args.stream_id is not None:
            logger.LogInfo(f"Resuming stream: {args.stream_id}")
        else:
            logger.LogError("Either --checkpoint or --stream-id must be provided")
            return 1
        
        logger.LogInfo("Resume functionality implementation details would go here")
        return 0
    except Exception as e:
        ErrorHandler.ReportException(e, "resume", severity=2)
        return 1


def HandleFeedback(args) -> int:
    try:
        logger = Logger("feedback")
        logger.LogInfo(f"Recording feedback: Stream {args.stream_id}, {args.type}={args.score}")
        logger.LogInfo("Feedback recording not yet implemented in CLI")
        return 0
    except Exception as e:
        ErrorHandler.ReportException(e, "feedback", severity=2)
        return 1


def HandleSearchReferences(args) -> int:
    try:
        logger = Logger("search-references")
        logger.LogInfo(f"Searching: query='{args.query}', category='{args.category}'")
        logger.LogInfo("Reference search not yet implemented in CLI")
        return 0
    except Exception as e:
        ErrorHandler.ReportException(e, "search-references", severity=2)
        return 1


def Main() -> int:
    parser = CreateArgumentParser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    if args.command == "generate":
        return HandleGenerate(args)
    elif args.command == "pause":
        return HandlePause(args)
    elif args.command == "resume":
        return HandleResume(args)
    elif args.command == "feedback":
        return HandleFeedback(args)
    elif args.command == "search-references":
        return HandleSearchReferences(args)
    
    return 1


if __name__ == "__main__":
    sys.exit(Main())
