"""
Unit tests for the canonical JSON formatter.
"""

import json

import pytest
from munajjam.models import Ayah, AlignmentResult
from munajjam.formatting import format_result, format_results


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_result(sample_ayahs):
    """A single AlignmentResult built from the shared sample_ayahs fixture."""
    return AlignmentResult(
        ayah=sample_ayahs[0],
        start_time=5.6789,
        end_time=9.1234,
        transcribed_text="بسم الله الرحمن الرحيم",
        similarity_score=0.9567,
        overlap_detected=False,
    )


@pytest.fixture
def sample_result_with_overlap(sample_ayahs):
    """An AlignmentResult with overlap_detected=True."""
    return AlignmentResult(
        ayah=sample_ayahs[1],
        start_time=10.0,
        end_time=14.0,
        transcribed_text="الحمد لله رب العالمين",
        similarity_score=0.72,
        overlap_detected=True,
    )


# ---------------------------------------------------------------------------
# format_result tests
# ---------------------------------------------------------------------------

CANONICAL_KEYS = {
    "ayah_number",
    "surah_id",
    "start_time",
    "end_time",
    "duration",
    "transcribed_text",
    "reference_text",
    "similarity_score",
    "is_high_confidence",
    "overlap_detected",
}


class TestFormatResult:
    """Tests for format_result()."""

    def test_format_result_keys(self, sample_result):
        """Output dict has exactly the 10 canonical keys."""
        out = format_result(sample_result)
        assert set(out.keys()) == CANONICAL_KEYS

    def test_format_result_values(self, sample_result):
        """Values match the source AlignmentResult fields."""
        out = format_result(sample_result)
        assert out["ayah_number"] == sample_result.ayah.ayah_number
        assert out["surah_id"] == sample_result.ayah.surah_id
        assert out["transcribed_text"] == sample_result.transcribed_text
        assert out["reference_text"] == sample_result.ayah.text
        assert out["is_high_confidence"] == sample_result.is_high_confidence
        assert out["overlap_detected"] == sample_result.overlap_detected

    def test_format_result_default_precision(self, sample_result):
        """Default precision=3 rounds floats to 3 decimal places."""
        out = format_result(sample_result)
        assert out["start_time"] == round(5.6789, 3)
        assert out["end_time"] == round(9.1234, 3)
        assert out["duration"] == round(9.1234 - 5.6789, 3)
        assert out["similarity_score"] == round(0.9567, 3)

    def test_format_result_custom_precision(self, sample_result):
        """Custom precision param rounds correctly."""
        out2 = format_result(sample_result, precision=2)
        assert out2["start_time"] == round(5.6789, 2)
        assert out2["similarity_score"] == round(0.9567, 2)

        # Build a result with >5 decimal places so precision=5 actually rounds
        precise_result = AlignmentResult(
            ayah=sample_result.ayah,
            start_time=5.678901234,
            end_time=9.123456789,
            transcribed_text=sample_result.transcribed_text,
            similarity_score=0.956789012,
            overlap_detected=False,
        )
        out5 = format_result(precise_result, precision=5)
        assert out5["start_time"] == round(5.678901234, 5)
        assert out5["similarity_score"] == round(0.956789012, 5)

    def test_format_result_overlap_true(self, sample_result_with_overlap):
        """overlap_detected: True propagates correctly."""
        out = format_result(sample_result_with_overlap)
        assert out["overlap_detected"] is True

    def test_format_result_json_serializable(self, sample_result):
        """json.dumps() succeeds on the output (no unserializable types)."""
        out = format_result(sample_result)
        serialized = json.dumps(out, ensure_ascii=False)
        assert isinstance(serialized, str)
        assert len(serialized) > 0


# ---------------------------------------------------------------------------
# format_results tests
# ---------------------------------------------------------------------------

class TestFormatResults:
    """Tests for format_results()."""

    def test_format_results_structure(self, sample_result, sample_result_with_overlap):
        """Wrapper dict has 'ayahs' list with correct length."""
        out = format_results([sample_result, sample_result_with_overlap])
        assert "ayahs" in out
        assert isinstance(out["ayahs"], list)
        assert len(out["ayahs"]) == 2

    def test_format_results_with_metadata(self, sample_result):
        """surah_id and reciter present when passed."""
        out = format_results([sample_result], surah_id=1, reciter="Test Reciter")
        assert out["surah_id"] == 1
        assert out["reciter"] == "Test Reciter"

    def test_format_results_without_metadata(self, sample_result):
        """surah_id and reciter keys absent when omitted."""
        out = format_results([sample_result])
        assert "surah_id" not in out
        assert "reciter" not in out

    def test_format_results_empty_list(self):
        """Returns {'ayahs': []}, no crash."""
        out = format_results([])
        assert out == {"ayahs": []}
