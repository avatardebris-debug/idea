"""VR Stock Ticker — Entry point for running the application."""

from __future__ import annotations

import sys
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Main entry point for the VR Stock Ticker application."""
    logger.info("Starting VR Stock Ticker...")

    try:
        # Import here to avoid circular imports
        from src.vr_scene import VRScene
        from src.vr_renderer import VRRenderer
        from src.ticker import Ticker
        from src.data_source import MockDataSource

        # Create scene
        scene = VRScene()
        scene.start()

        # Create renderer
        renderer = VRRenderer(scene)
        renderer.start_rendering()

        # Add some sample tickers
        sample_tickers = [
            Ticker(symbol="AAPL", name="Apple Inc.", price=178.72, change=2.34, change_percent=1.33),
            Ticker(symbol="GOOGL", name="Alphabet Inc.", price=141.80, change=-0.92, change_percent=-0.65),
            Ticker(symbol="MSFT", name="Microsoft Corp.", price=378.91, change=4.56, change_percent=1.22),
            Ticker(symbol="AMZN", name="Amazon.com Inc.", price=178.25, change=-1.23, change_percent=-0.69),
            Ticker(symbol="TSLA", name="Tesla Inc.", price=248.42, change=5.67, change_percent=2.33),
        ]

        for ticker in sample_tickers:
            scene.add_ticker(ticker)

        logger.info(f"Added {len(sample_tickers)} tickers to the scene")

        # Main loop
        frame_count = 0
        start_time = time.time()
        max_frames = 300  # Run for about 5 seconds at 60 FPS

        while scene.is_running and frame_count < max_frames:
            # Render frame
            render_objects = renderer.render_frame()

            # Update scene
            scene.update_tickers()

            frame_count += 1

            # Print status every 60 frames
            if frame_count % 60 == 0:
                fps = renderer.get_fps()
                status = scene.get_status()
                logger.info(
                    f"Frame {frame_count} | FPS: {fps:.1f} | "
                    f"Tickers: {status['ticker_count']} | "
                    f"Board: {status['current_board']}"
                )

            # Simulate frame time
            time.sleep(1.0 / scene.frame_rate)

        # Cleanup
        scene.stop()
        renderer.stop_rendering()

        elapsed = time.time() - start_time
        logger.info(
            f"VR Stock Ticker stopped. "
            f"Ran for {elapsed:.1f}s, {frame_count} frames, "
            f"avg FPS: {frame_count / elapsed:.1f}"
        )

        return 0

    except KeyboardInterrupt:
        logger.info("VR Stock Ticker interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"VR Stock Ticker error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
