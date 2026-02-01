# Copyright 2026 James G Willmore
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import inspect
import logging
import os
import sys

import structlog
from structlog.stdlib import ProcessorFormatter
from structlog.types import EventDict, Processor

LEVEL_COLORS = {
    "DEBUG": "\033[36m",  # Cyan
    "INFO": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",  # Red
    "CRITICAL": "\033[41m\033[37m",  # White on Red background
}
TIMESTAMP_COLOR = "\033[38;5;87m"
FILENAME_COLOR = "\033[38;5;74m"
FUNC_COLOR = "\033[38;5;68m"
LINENO_COLOR = "\033[38;5;67m"
EXTRAS_COLOR = "\033[38;5;245m"
RESET = "\033[0m"


class LoggingConfig:
    """Configuration for structlog logging."""
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern to ensure single logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the logging configuration."""
        if not self._initialized:
            self.init_config()

    def init_config(self, log_level: int = logging.INFO) -> None:
        """Initializes the structlog configuration with console and file handlers."""
        # 1. Define shared processors (add timestamps, log level names, etc.)
        shared_processors = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso", utc=False),
            structlog.processors.EventRenamer("message"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            self.add_callsite_info,
        ]

        # 2. Configure the console handler (pretty output for humans)
        console_renderer = self.custom_console_renderer(colors=True)
        console_formatter = ProcessorFormatter(
            processor=console_renderer,
            foreign_pre_chain=shared_processors,
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)

        # 3. Configure the file handler (JSON output for log analyzers)
        json_renderer = structlog.processors.JSONRenderer(sort_keys=True)
        json_formatter = ProcessorFormatter(
            processor=json_renderer,
            foreign_pre_chain=shared_processors,
        )
        cwd = os.getcwd()
        logs_dir = os.path.join(cwd, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        file_handler = logging.FileHandler(os.path.join(logs_dir, "app.log"), mode="a")
        file_handler.setFormatter(json_formatter)

        # 4. Set up the standard library logger
        # This captures logs from both structlog and other libraries
        root_logger = logging.getLogger()
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        root_logger.setLevel(log_level)  # Set desired log level

        # 5. Configure structlog to use the standard library for output
        structlog.configure(
            processors=[
                *shared_processors,
                ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        self._initialized = True
        self.logger = structlog.get_logger()
        self.logger.debug("Logging is configured.")

    def custom_console_renderer(self, colors: bool = True) -> Processor:
        """
        Custom console renderer for structlog.
        Args:
            colors (bool): Whether to use colors in the output.
        Returns:
            Processor: A structlog processor function.
        """

        def renderer(_, __, event_dict: EventDict) -> str:
            # Required fields
            timestamp = event_dict.pop("timestamp", "")
            level = event_dict.pop("level", "").upper()
            event = event_dict.pop("message", "")
            filename = event_dict.pop("filename", "unknown")
            func = event_dict.pop("func_name", "unknown")
            lineno = event_dict.pop("lineno", "?")

            # Format extended parameters
            extras = " ".join(f"{key}={value}" for key, value in event_dict.items())

            level_color = LEVEL_COLORS.get(level, "") if colors else ""
            ts_color = TIMESTAMP_COLOR if colors else ""
            fname_color = FILENAME_COLOR if colors else ""
            func_color = FUNC_COLOR if colors else ""
            line_color = LINENO_COLOR if colors else ""
            extras_color = EXTRAS_COLOR if colors else ""
            reset = RESET if colors else ""

            return (
                f"{ts_color}{timestamp}{reset} "
                f"[{level_color}{level}{reset}] "
                f"[{fname_color}{filename}{reset}] "
                f"[{func_color}{func}{reset}] "
                f"[{line_color}{lineno}{reset}] "
                f"{event} - {extras_color}{extras}{reset}"
            )

        return renderer

    def add_callsite_info(self, _, __, event_dict: EventDict) -> EventDict:
        """
        Inspect the call stack to find the originating caller info.
        Args:
            _ : Unused.
            __ : Unused.
            event_dict (EventDict): The event dictionary to update.
        Returns:
            EventDict: The updated event dictionary with callsite info.
        """
        frame = inspect.currentframe()
        if frame:
            outer_frames = inspect.getouterframes(frame)
            # Find the first non-logging/structlog frame
            for record in outer_frames:
                if (
                    "site-packages" not in record.filename
                    and "logging" not in record.filename
                ):
                    event_dict["filename"] = os.path.basename(record.filename)
                    event_dict["func_name"] = record.function
                    event_dict["lineno"] = record.lineno
                    break
        return event_dict

    def get_logger(self) -> structlog.stdlib.BoundLogger:
        """
        Returns the configured structlog logger.
        Returns:
            BoundLogger: The structlog logger instance.
        """
        if not self._initialized:
            self.init_config()
        return self.logger
