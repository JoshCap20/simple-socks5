import logging
import threading
import unittest
from unittest.mock import patch

from src.config import ProxyConfiguration
from src.logger import get_logger, configure_logger, _logger_lock


class TestLoggerThreadSafety(unittest.TestCase):
    def test_logger_lock_exists(self):
        """A threading.Lock should exist for thread-safe logger access."""
        self.assertIsInstance(_logger_lock, type(threading.Lock()))

    def test_get_logger_returns_same_instance(self):
        """Repeated calls with the same name return the same logger."""
        logger1 = get_logger("test_same")
        logger2 = get_logger("test_same")
        self.assertIs(logger1, logger2)

    def test_get_logger_concurrent_access(self):
        """Concurrent get_logger calls with the same name should not raise."""
        errors = []
        results = []

        def worker(name):
            try:
                logger = get_logger(name)
                results.append(logger)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=("concurrent_test",)) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)
        # All threads should get the same logger instance
        self.assertTrue(all(r is results[0] for r in results))

    def test_configure_logger_does_not_duplicate_handlers(self):
        """Calling configure_logger twice should not add duplicate handlers."""

        class FreshConfig(ProxyConfiguration):
            pass

        FreshConfig.initialize("localhost", 1080, "debug")

        with patch("src.logger.ProxyConfiguration", FreshConfig):
            logger = logging.getLogger("test_no_dup_handlers")
            logger.handlers.clear()
            configure_logger(logger)
            count_after_first = len(logger.handlers)
            configure_logger(logger)
            count_after_second = len(logger.handlers)
            self.assertEqual(count_after_first, count_after_second)


if __name__ == "__main__":
    unittest.main()
