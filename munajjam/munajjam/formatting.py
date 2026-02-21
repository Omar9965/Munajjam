"""
Canonical JSON formatting for alignment results.

Provides a single, consistent schema for serializing AlignmentResult
objects to JSON-ready dicts. All consumers should use these functions
instead of hand-rolling their own dict structures.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from munajjam.models import AlignmentResult


def format_result(result: AlignmentResult, precision: int = 3) -> dict:
    """Format a single AlignmentResult into the canonical dict.

    Args:
        result: The alignment result to format.
        precision: Number of decimal places for float rounding (default 3).

    Returns:
        A dict with the canonical schema::

            {
                "ayah_number": int,
                "surah_id": int,
                "start_time": float,
                "end_time": float,
                "duration": float,
                "transcribed_text": str,
                "reference_text": str,
                "similarity_score": float,
                "is_high_confidence": bool,
                "overlap_detected": bool,
            }
    """
    return {
        "ayah_number": result.ayah.ayah_number,
        "surah_id": result.ayah.surah_id,
        "start_time": round(result.start_time, precision),
        "end_time": round(result.end_time, precision),
        "duration": round(result.duration, precision),
        "transcribed_text": result.transcribed_text,
        "reference_text": result.ayah.text,
        "similarity_score": round(result.similarity_score, precision),
        "is_high_confidence": result.is_high_confidence,
        "overlap_detected": result.overlap_detected,
    }


def format_results(
    results: list[AlignmentResult],
    *,
    surah_id: int | None = None,
    reciter: str | None = None,
    precision: int = 3,
) -> dict:
    """Format a list of AlignmentResults into a canonical output dict.

    Args:
        results: List of alignment results to format.
        surah_id: Optional surah number to include in output.
        reciter: Optional reciter name to include in output.
        precision: Number of decimal places for float rounding (default 3).

    Returns:
        A dict with the canonical schema::

            {
                "surah_id": int,       # only if provided
                "reciter": str,        # only if provided
                "ayahs": [...]         # list of formatted results
            }
    """
    output: dict = {
        "ayahs": [format_result(r, precision) for r in results],
    }
    if surah_id is not None:
        output["surah_id"] = surah_id
    if reciter is not None:
        output["reciter"] = reciter
    return output
