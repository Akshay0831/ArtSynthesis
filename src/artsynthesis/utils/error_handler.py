import sys
from typing import Optional
from pathlib import Path


class ErrorContext:
    def __init__(self, message: str, source: str, severity: int = 2):
        self.message = message
        self.source = source
        self.severity = severity


class ErrorHandler:
    @staticmethod
    def ReportException(exception: Exception, source: str, severity: int = 2) -> None:
        message = f"[{source}] {type(exception).__name__}: {str(exception)}"
        if severity >= 3:
            print(f"FATAL: {message}", file=sys.stderr)
        elif severity == 2:
            print(f"ERROR: {message}", file=sys.stderr)
        else:
            print(f"WARNING: {message}", file=sys.stderr)
    
    @staticmethod
    def LogWarning(message: str) -> None:
        print(f"WARNING: {message}", file=sys.stderr)
    
    @staticmethod
    def LogError(message: str) -> None:
        print(f"ERROR: {message}", file=sys.stderr)
    
    @staticmethod
    def LogFatal(message: str) -> None:
        print(f"FATAL: {message}", file=sys.stderr)
        sys.exit(1)
