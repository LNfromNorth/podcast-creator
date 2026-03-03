"""
Tests for language resolution utility
"""
import pytest

from podcast_creator.language import resolve_language_name


class TestResolveLanguageName:
    """Tests for resolve_language_name()"""

    def test_iso_639_1_code(self):
        """Test resolving standard ISO 639-1 codes"""
        assert resolve_language_name("pt") == "Portuguese"
        assert resolve_language_name("en") == "English"
        assert resolve_language_name("fr") == "French"
        assert resolve_language_name("de") == "German"
        assert resolve_language_name("ja") == "Japanese"

    def test_bcp47_code(self):
        """Test resolving BCP 47 codes (takes language part before dash)"""
        assert resolve_language_name("pt-BR") == "Portuguese"
        assert resolve_language_name("en-US") == "English"
        assert resolve_language_name("zh-CN") == "Chinese"
        assert resolve_language_name("es-MX") == "Spanish"

    def test_case_insensitive(self):
        """Test that codes are case-insensitive"""
        assert resolve_language_name("PT") == "Portuguese"
        assert resolve_language_name("En") == "English"
        assert resolve_language_name("PT-br") == "Portuguese"

    def test_compound_names_semicolon(self):
        """Test handling of compound names with semicolons (e.g., 'Spanish; Castilian')"""
        assert resolve_language_name("es") == "Spanish"

    def test_iso_639_3_code(self):
        """Test fallback to ISO 639-3 (alpha_3) codes"""
        assert resolve_language_name("por") == "Portuguese"
        assert resolve_language_name("eng") == "English"

    def test_invalid_code_raises(self):
        """Test that invalid codes raise ValueError"""
        with pytest.raises(ValueError, match="Invalid language code"):
            resolve_language_name("xx")

        with pytest.raises(ValueError, match="Invalid language code"):
            resolve_language_name("zzz")

    def test_empty_string_raises(self):
        """Test that empty string raises ValueError"""
        with pytest.raises(ValueError, match="cannot be empty"):
            resolve_language_name("")

        with pytest.raises(ValueError, match="cannot be empty"):
            resolve_language_name("   ")

    def test_whitespace_trimmed(self):
        """Test that whitespace is trimmed from input"""
        assert resolve_language_name(" pt ") == "Portuguese"
        assert resolve_language_name(" en-US ") == "English"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
