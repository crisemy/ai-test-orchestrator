import os

# File paths
LOG_FILE = "logs/pipeline.log"
EXECUTION_LOG = "reports/execution_log.json"
BACKUP_DIR = "generated-tests/backups"
PRIORITY_CACHE = "reports/priorities.json"

# Cost constants
TOKEN_COST_PER_MILLION = float(os.getenv("TOKEN_COST_PER_MILLION", "0.90"))
MANUAL_TEST_COST = float(os.getenv("MANUAL_TEST_COST", "50.0"))
MAX_COST_THRESHOLD = float(os.getenv("MAX_COST_THRESHOLD", "0.50"))

# Rate limiting
RATE_LIMIT_MAX_PER_MINUTE = int(os.getenv("RATE_LIMIT_MAX_PER_MINUTE", "5"))

# Pipeline
MAX_PLAYWRIGHT_RETRIES = int(os.getenv("MAX_PLAYWRIGHT_RETRIES", "2"))
MAX_AI_ATTEMPTS = int(os.getenv("MAX_AI_ATTEMPTS", "3"))

# Default target URL for normalizer
TARGET_URL = os.getenv("TARGET_URL", "http://localhost:3000/playwright-ui-testing-lab.html")

# Test credentials
TEST_USERNAME = os.getenv("TEST_USERNAME", "tomsmith")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "SuperSecretPassword!")


class OrchestratorError(Exception):
    ...


class TestGenerationError(OrchestratorError):
    ...


class ValidationError(OrchestratorError):
    ...


class CancelledByUser(OrchestratorError):
    ...
