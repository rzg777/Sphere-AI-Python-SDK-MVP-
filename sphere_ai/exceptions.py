"""Custom exceptions for the Sphere AI SDK."""


class SphereError(Exception):
    """Base exception for all Sphere AI SDK errors."""
    pass


class SphereSecurityViolation(SphereError):
    """Raised when a security policy violation occurs."""
    pass


class SpherePolicyError(SphereError):
    """Raised when there's an error in policy configuration or evaluation."""
    pass


class SphereConfigurationError(SphereError):
    """Raised when there's an error in SDK configuration."""
    pass


class SphereValidationError(SphereError):
    """Raised when input validation fails."""
    pass


class SphereLoggingError(SphereError):
    """Raised when there's an error in audit logging."""
    pass