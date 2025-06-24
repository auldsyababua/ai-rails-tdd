#!/usr/bin/env python3
"""
Test Runner Service for AI Rails TDD
Executes generated tests against generated code and returns results
"""

import asyncio
import tempfile
import subprocess
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="AI Rails Test Runner")


class TestExecutionRequest(BaseModel):
    """Request to run tests against code"""

    test_code: str
    implementation_code: str
    language: str = "python"
    test_framework: str = "pytest"
    timeout: int = 30  # seconds


class TestResult(BaseModel):
    """Individual test result"""

    test_name: str
    passed: bool
    error_message: str = None
    duration: float = None


class TestExecutionResponse(BaseModel):
    """Response from test execution"""

    success: bool
    total_tests: int
    passed_tests: int
    failed_tests: int
    test_results: List[TestResult]
    coverage: float = None
    stdout: str
    stderr: str
    execution_time: float


def extract_test_results_from_pytest(output: str) -> Tuple[List[TestResult], int, int]:
    """Parse pytest output to extract individual test results"""
    test_results = []
    passed = 0
    failed = 0

    # Look for test result lines (PASSED/FAILED)
    lines = output.split("\n")
    for line in lines:
        if "::" in line and ("PASSED" in line or "FAILED" in line):
            parts = line.split("::")
            if len(parts) >= 2:
                test_name = parts[1].split()[0]
                if "PASSED" in line:
                    test_results.append(TestResult(test_name=test_name, passed=True))
                    passed += 1
                elif "FAILED" in line:
                    test_results.append(
                        TestResult(
                            test_name=test_name,
                            passed=False,
                            error_message="Test failed - check output for details",
                        )
                    )
                    failed += 1

    # If no individual results found, try to parse summary
    if not test_results:
        for line in lines:
            if "passed" in line and "failed" in line:
                # Parse summary line like "1 failed, 2 passed in 0.05s"
                import re

                passed_match = re.search(r"(\d+) passed", line)
                failed_match = re.search(r"(\d+) failed", line)
                if passed_match:
                    passed = int(passed_match.group(1))
                if failed_match:
                    failed = int(failed_match.group(1))
                break

    return test_results, passed, failed


async def run_python_tests(
    test_code: str, implementation_code: str, timeout: int
) -> TestExecutionResponse:
    """Execute Python tests using pytest"""
    start_time = asyncio.get_event_loop().time()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Write implementation file
        impl_file = Path(temp_dir) / "implementation.py"
        impl_file.write_text(implementation_code)

        # Write test file
        test_file = Path(temp_dir) / "test_implementation.py"

        # Ensure test imports from local implementation
        test_code_with_import = test_code
        if (
            "import implementation" not in test_code
            and "from implementation" not in test_code
        ):
            # Add import at the beginning if not present
            test_code_with_import = "from implementation import *\n\n" + test_code

        test_file.write_text(test_code_with_import)

        # Run pytest with coverage
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(test_file),
            "-v",  # verbose
            "--tb=short",  # short traceback
            f"--timeout={timeout}",  # timeout per test
            "--no-header",  # cleaner output
            "-p",
            "no:warnings",  # suppress warnings
            "--cov=implementation",  # coverage for implementation
            "--cov-report=term-missing",  # show missed lines
            "--cov-report=json",  # also output JSON for parsing
        ]

        try:
            # Run pytest
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=temp_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout + 5,  # Add buffer to subprocess timeout
            )

            stdout_str = stdout.decode("utf-8", errors="ignore")
            stderr_str = stderr.decode("utf-8", errors="ignore")

            # Extract test results
            test_results, passed, failed = extract_test_results_from_pytest(stdout_str)
            total_tests = passed + failed

            # Try to get coverage
            coverage = None
            coverage_file = Path(temp_dir) / "coverage.json"
            if coverage_file.exists():
                try:
                    with open(coverage_file) as f:
                        cov_data = json.load(f)
                        coverage = cov_data.get("totals", {}).get(
                            "percent_covered", None
                        )
                except:
                    pass

            # Parse coverage from output if JSON failed
            if coverage is None:
                for line in stdout_str.split("\n"):
                    if "TOTAL" in line and "%" in line:
                        parts = line.split()
                        for part in parts:
                            if part.endswith("%"):
                                try:
                                    coverage = float(part.rstrip("%"))
                                    break
                                except:
                                    pass

            execution_time = asyncio.get_event_loop().time() - start_time

            return TestExecutionResponse(
                success=process.returncode == 0,
                total_tests=total_tests,
                passed_tests=passed,
                failed_tests=failed,
                test_results=test_results,
                coverage=coverage,
                stdout=stdout_str,
                stderr=stderr_str,
                execution_time=execution_time,
            )

        except asyncio.TimeoutError:
            execution_time = asyncio.get_event_loop().time() - start_time
            return TestExecutionResponse(
                success=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                test_results=[],
                stdout="",
                stderr=f"Test execution timed out after {timeout} seconds",
                execution_time=execution_time,
            )
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return TestExecutionResponse(
                success=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                test_results=[],
                stdout="",
                stderr=f"Error running tests: {str(e)}",
                execution_time=execution_time,
            )


@app.post("/run-tests", response_model=TestExecutionResponse)
async def run_tests(request: TestExecutionRequest):
    """Execute tests against implementation code"""
    if request.language.lower() != "python":
        raise HTTPException(
            status_code=400,
            detail=f"Language '{request.language}' not supported yet. Only Python is currently supported.",
        )

    if request.test_framework.lower() != "pytest":
        raise HTTPException(
            status_code=400,
            detail=f"Test framework '{request.test_framework}' not supported. Only pytest is currently supported.",
        )

    # Run the tests
    result = await run_python_tests(
        request.test_code, request.implementation_code, request.timeout
    )

    return result


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Rails Test Runner",
        "pytest_available": True,
        "coverage_available": True,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI Rails Test Runner Service")
    parser.add_argument("--port", type=int, default=8001, help="Port to run on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    args = parser.parse_args()

    print(f"🧪 Starting AI Rails Test Runner on http://{args.host}:{args.port}")
    print("📝 Endpoints:")
    print(f"   - POST /run-tests - Execute tests against code")
    print(f"   - GET /health - Health check")

    uvicorn.run(app, host=args.host, port=args.port)
