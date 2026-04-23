"""Main application entry point for VR Stock Ticker Scanner."""

from __future__ import annotations

import sys
import time
from typing import Optional

# Add project root to path
sys.path.insert(0, '.')

from src.ticker import Ticker
from src.data_source import MockDataSource
from src.ticker_display import TickerBoard
from src.navigation import VRNavigator
from src.vr_scene import VRScene
from src.vr_renderer import VRRenderer


class VRStockTickerApp:
    """Main application class for VR Stock Ticker Scanner."""

    def __init__(self):
        """Initialize the application."""
        self.scene: Optional[VRScene] = None
        self.renderer: Optional[VRRenderer] = None
        self.is_running: bool = False
        self._tickers_to_add: list = []

    def initialize(self) -> None:
        """Initialize the VR application."""
        # Create VR scene
        self.scene = VRScene()

        # Create navigator
        self.scene.navigator = VRNavigator()

        # Create initial board
        initial_board = TickerBoard()
        self.scene.navigator.add_board(initial_board, "Main Board")

        # Create renderer
        self.renderer = VRRenderer(self.scene)

        # Add sample tickers
        sample_tickers = [
            Ticker(symbol='AAPL', name='Apple Inc', price=150.0, open_price=148.0),
            Ticker(symbol='GOOGL', name='Alphabet Inc', price=2800.0, open_price=2790.0),
            Ticker(symbol='MSFT', name='Microsoft Corp', price=300.0, open_price=295.0),
            Ticker(symbol='AMZN', name='Amazon.com Inc', price=3300.0, open_price=3280.0),
            Ticker(symbol='TSLA', name='Tesla Inc', price=700.0, open_price=690.0),
        ]

        for ticker in sample_tickers:
            self.scene.add_ticker(ticker)

        # Start data source
        self.scene.data_source = MockDataSource()
        self.scene.data_source.start()

    def start(self) -> None:
        """Start the application."""
        if not self.scene or not self.renderer:
            raise RuntimeError("Application not initialized")

        self.is_running = True
        self.scene.start()
        self.renderer.start_rendering()

    def stop(self) -> None:
        """Stop the application."""
        self.is_running = False
        if self.scene:
            self.scene.stop()
        if self.renderer:
            self.renderer.stop_rendering()

    def run_frame(self) -> dict:
        """Run a single frame of the application."""
        if not self.is_running:
            return {}

        # Get render objects
        render_objects = self.renderer.render_frame()

        # Get scene status
        scene_status = self.scene.get_status()

        return {
            "render_objects": render_objects,
            "scene_status": scene_status,
            "renderer_status": self.renderer.get_status(),
        }

    def get_status(self) -> dict:
        """Get application status."""
        return {
            "is_running": self.is_running,
            "scene_status": self.scene.get_status() if self.scene else None,
            "renderer_status": self.renderer.get_status() if self.renderer else None,
        }

    def to_dict(self) -> dict:
        """Convert application to dictionary."""
        return {
            "is_running": self.is_running,
            "scene": self.scene.to_dict() if self.scene else None,
            "renderer": self.renderer.to_dict() if self.renderer else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> VRStockTickerApp:
        """Create application from dictionary."""
        app = cls()
        app.is_running = data.get("is_running", False)
        if data.get("scene"):
            app.scene = VRScene.from_dict(data["scene"])
        if data.get("renderer"):
            app.renderer = VRRenderer.from_dict(data["renderer"], app.scene)
        return app


def main():
    """Main entry point."""
    app = VRStockTickerApp()
    app.initialize()
    app.start()

    try:
        # Run for 10 seconds
        start_time = time.time()
        while time.time() - start_time < 10:
            frame = app.run_frame()
            if frame:
                print(f"Frame rendered: {len(frame['render_objects'])} objects")
                print(f"Scene status: {frame['scene_status']}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        app.stop()


if __name__ == "__main__":
    main()
