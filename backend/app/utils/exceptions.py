class CoverageAgentError(Exception):
    """Base exception for the coverage evaluation agent."""


class UnsupportedFileTypeError(CoverageAgentError):
    """Raised when the uploaded file type is not supported."""


class FileMissingError(CoverageAgentError):
    """Raised when a required file is missing."""


class ExcelColumnMissingError(CoverageAgentError):
    """Raised when required Excel columns cannot be resolved."""


class LLMInvalidJSONError(CoverageAgentError):
    """Raised when the LLM response cannot be parsed as valid JSON."""


class ChunkProcessingError(CoverageAgentError):
    """Raised when chunked document processing fails."""


class ScannedPdfNotSupportedError(CoverageAgentError):
    """Raised when a PDF looks like a scanned image without extractable text."""

