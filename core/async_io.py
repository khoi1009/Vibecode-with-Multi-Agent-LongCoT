"""
Async I/O Module for VibeCode

Provides non-blocking file operations with concurrency control.
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor
import os


class AsyncFileReader:
    """Async file reading with concurrency control."""

    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self._executor = ThreadPoolExecutor(max_workers=max_concurrent)

    async def read_file(self, path: Path) -> str:
        """Read single file asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            lambda: self._read_file_safe(path)
        )

    def _read_file_safe(self, path: Path) -> str:
        """Safely read file with error handling."""
        try:
            return path.read_text(encoding='utf-8', errors='ignore')
        except (IOError, OSError, UnicodeDecodeError) as e:
            return f"Error reading {path}: {e}"

    async def read_files(self, paths: List[Path]) -> Dict[Path, str]:
        """Read multiple files in parallel with semaphore control."""
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def read_with_limit(path: Path) -> tuple:
            async with semaphore:
                try:
                    content = await self.read_file(path)
                    return (path, content)
                except Exception as e:
                    return (path, f"Error: {e}")

        if not paths:
            return {}

        tasks = [read_with_limit(p) for p in paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        result_dict = {}
        for result in results:
            if isinstance(result, tuple) and len(result) == 2:
                path, content = result
                result_dict[path] = content
            elif isinstance(result, Exception):
                # Handle unexpected exceptions
                pass

        return result_dict

    async def scan_directory(
        self,
        directory: Path,
        pattern: str = "**/*.py",
        processor: Callable[[Path, str], Any] = None,
        max_files: int = 1000
    ) -> List[Any]:
        """Scan directory and optionally process files."""
        if not directory.exists() or not directory.is_dir():
            return []

        try:
            files = list(directory.glob(pattern))[:max_files]
        except (IOError, OSError):
            return []

        if not files:
            return []

        contents = await self.read_files(files)

        if processor:
            return [processor(path, content) for path, content in contents.items()]
        return list(contents.values())

    def shutdown(self):
        """Shutdown the executor."""
        self._executor.shutdown(wait=True)


def run_async(coro):
    """Helper to run async code from synchronous context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coro)


async def read_files_async(paths: List[Path]) -> Dict[Path, str]:
    """Async file reading convenience function."""
    reader = AsyncFileReader()
    try:
        return await reader.read_files(paths)
    finally:
        reader.shutdown()


def read_files_parallel(paths: List[Path]) -> Dict[Path, str]:
    """Synchronous wrapper for async file reading."""
    if not paths:
        return {}
    return run_async(read_files_async(paths))


async def scan_directory_async(
    directory: Path,
    pattern: str = "**/*.py",
    max_files: int = 1000
) -> List[Path]:
    """Async directory scanning returning paths."""
    reader = AsyncFileReader()
    try:
        return await reader.scan_directory(
            directory, pattern,
            processor=lambda p, c: p,
            max_files=max_files
        )
    finally:
        reader.shutdown()


class ParallelProcessor:
    """Process files in parallel with configurable workers."""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def process(
        self,
        items: List[Any],
        processor: Callable[[Any], Any],
        description: str = "Processing"
    ) -> List[Any]:
        """Process items in parallel."""
        from concurrent.futures import as_completed

        futures = {self._executor.submit(processor, item): item for item in items}
        results = []

        for future in as_completed(futures):
            try:
                result = future.result(timeout=30)
                results.append(result)
            except Exception as e:
                results.append(f"Error: {e}")

        return results

    def shutdown(self):
        """Shutdown the executor."""
        self._executor.shutdown(wait=True)
