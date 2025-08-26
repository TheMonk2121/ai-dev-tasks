#!/usr/bin/env python3
"""
Performance dashboard for workflow monitoring.
Provides real-time visualization of performance metrics using NiceGUI.
"""

import asyncio
import logging
from typing import Any, Dict, List

try:
    from nicegui import ui

    NICEGUI_AVAILABLE = True
except ImportError:
    NICEGUI_AVAILABLE = False

    # Mock UI components for testing
    class MockUIComponent:
        """Mock UI component that handles method calls gracefully"""

        def __init__(self, *args, **kwargs):
            self._children = []
            self._attributes = {}
            self._data = {}

        def classes(self, *args, **kwargs):
            """Mock classes method"""
            return self

        def __getattr__(self, name):
            """Handle any other method calls"""
            return lambda *args, **kwargs: self

        def __call__(self, *args, **kwargs):
            """Handle component instantiation"""
            return self

        def __enter__(self):
            """Context manager support"""
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Context manager support"""
            pass

        def __setattr__(self, name, value):
            """Handle attribute assignments"""
            if name.startswith("_"):
                super().__setattr__(name, value)
            else:
                self._data[name] = value

        def __getattribute__(self, name):
            """Handle attribute access"""
            if name.startswith("_"):
                return super().__getattribute__(name)
            elif name in ["text", "rows", "value"]:
                return self._data.get(name, None)
            else:
                return super().__getattribute__(name)

        def clear(self):
            """Mock clear method"""
            self._children.clear()

        def set_value(self, value):
            """Mock set_value method"""
            self._data["value"] = value

        def open(self):
            """Mock open method"""
            pass

        def close(self):
            """Mock close method"""
            pass

    class MockUI:
        """Mock UI module for testing when NiceGUI is not available"""

        def __getattr__(self, name):
            """Return mock components for any UI method"""
            return MockUIComponent

        def run(self, *args, **kwargs):
            """Mock run method"""
            pass

        def notify(self, message: str, type: str = "info"):
            """Mock notify method"""
            pass

    ui = MockUI()

from .performance_collector import get_collection_stats

try:
    from .performance_storage import get_performance_trends, get_recent_workflows
except ImportError:
    # Mock storage functions for testing
    async def get_recent_workflows(limit: int = 50):
        return []

    async def get_performance_trends(days: int = 30):
        return []


logger = logging.getLogger(__name__)


class PerformanceDashboard:
    """Real-time performance dashboard for workflow monitoring"""

    def __init__(self, storage_enabled: bool = True):
        self.storage_enabled = storage_enabled
        self.dashboard_data = {
            "current_workflow": None,
            "recent_workflows": [],
            "performance_trends": [],
            "alerts": [],
            "stats": {},
        }
        self.update_interval = 5.0  # seconds
        self.is_running = False

    async def start_dashboard(self, port: int = 8080):
        """Start the performance dashboard"""
        if not NICEGUI_AVAILABLE:
            logger.warning("NiceGUI not available, dashboard will run in mock mode")

        self.is_running = True

        # Create dashboard UI
        self._create_dashboard_ui()

        # Start background updates
        asyncio.create_task(self._background_updates())

        # Start NiceGUI
        ui.run(port=port, title="Workflow Performance Dashboard")

        logger.info(f"Performance dashboard started on port {port}")

    def _create_dashboard_ui(self):
        """Create the dashboard user interface"""
        if not NICEGUI_AVAILABLE:
            logger.warning("Creating mock dashboard UI - NiceGUI not available")
            return

        # Header
        with ui.header().classes("bg-blue-500 text-white"):
            ui.label("🚀 Workflow Performance Dashboard").classes("text-h4")
            ui.space()
            ui.button("🔄 Refresh", on_click=self._refresh_data).classes("bg-blue-600")
            ui.button("⚙️ Settings", on_click=self._show_settings).classes("bg-blue-600")

        # Main content
        with ui.column().classes("w-full p-4"):

            # Current workflow status
            with ui.card().classes("w-full mb-4"):
                ui.label("📊 Current Workflow Status").classes("text-h6 mb-2")
                self.current_workflow_card = ui.column()

            # Performance metrics
            with ui.row().classes("w-full gap-4"):
                # Recent workflows
                with ui.card().classes("flex-1"):
                    ui.label("📈 Recent Workflows").classes("text-h6 mb-2")
                    self.recent_workflows_table = ui.table(
                        columns=[
                            {"name": "workflow_id", "label": "Workflow ID", "field": "workflow_id"},
                            {"name": "backlog_item", "label": "Backlog Item", "field": "backlog_item_id"},
                            {"name": "duration", "label": "Duration (ms)", "field": "total_duration_ms"},
                            {"name": "score", "label": "Score", "field": "performance_score"},
                            {"name": "status", "label": "Status", "field": "success"},
                        ],
                        rows=[],
                        pagination={"rowsPerPage": 10},
                    ).classes("w-full")

                # Performance trends
                with ui.card().classes("flex-1"):
                    ui.label("📊 Performance Trends").classes("text-h6 mb-2")
                    # Use plotly chart instead of ui.chart which doesn't exist
                    self.trends_chart = self._create_plotly_chart(
                        title="Workflow Performance Trends", chart_type="line"
                    ).classes("w-full h-64")

            # Collection points breakdown
            with ui.card().classes("w-full mb-4"):
                ui.label("🔍 Collection Points Breakdown").classes("text-h6 mb-2")
                self.collection_points_chart = self._create_plotly_chart(
                    title="Collection Point Performance", chart_type="bar"
                ).classes("w-full h-64")

            # Performance alerts
            with ui.card().classes("w-full"):
                ui.label("⚠️ Performance Alerts").classes("text-h6 mb-2")
                self.alerts_list = ui.list().classes("w-full")

    def _create_plotly_chart(self, title: str, chart_type: str = "line"):
        """Create a plotly chart component"""
        try:
            # Try to import plotly, but don't fail if not available
            import plotly.graph_objects as go  # type: ignore

            # Create a simple plotly figure
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[], y=[], mode="lines", name="Data"))
            fig.update_layout(title=title, height=300)

            # Return a div that will contain the plotly chart
            chart_div = ui.html(
                f"""
                <div id="chart-{id(fig)}" style="width:100%; height:300px;">
                    <script>
                        Plotly.newPlot('chart-{id(fig)}', {fig.to_json()});
                    </script>
                </div>
                """
            )
            return chart_div

        except (ImportError, ModuleNotFoundError):
            # Fallback to simple div if plotly not available
            fallback_html = (
                f'<div style="width:100%; height:300px; border:1px solid #ccc; '
                f'display:flex; align-items:center; justify-content:center;">'
                f"{title} Chart (Plotly not available)</div>"
            )
            return ui.html(fallback_html)

    async def _background_updates(self):
        """Background task for updating dashboard data"""
        while self.is_running:
            try:
                await self._update_dashboard_data()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in background updates: {e}")
                await asyncio.sleep(self.update_interval)

    async def _update_dashboard_data(self):
        """Update dashboard data from performance collectors"""
        try:
            # Get current workflow stats
            current_stats = get_collection_stats()
            self.dashboard_data["stats"] = current_stats

            # Update current workflow card
            await self._update_current_workflow_card(current_stats)

            # Get recent workflows if storage is enabled
            if self.storage_enabled:
                recent_workflows = await get_recent_workflows(limit=20)
                self.dashboard_data["recent_workflows"] = recent_workflows
                await self._update_recent_workflows_table(recent_workflows)

                # Get performance trends
                trends = await get_performance_trends(days=7)
                self.dashboard_data["performance_trends"] = trends
                await self._update_trends_chart(trends)

        except Exception as e:
            logger.error(f"Error updating dashboard data: {e}")

    async def _update_current_workflow_card(self, stats: Dict[str, Any]):
        """Update current workflow status card"""
        if not hasattr(self, "current_workflow_card") or not NICEGUI_AVAILABLE:
            return

        # Clear existing content
        if hasattr(self.current_workflow_card, "clear") and self.current_workflow_card is not None:
            self.current_workflow_card.clear()

        if stats.get("active"):
            # Active workflow
            if self.current_workflow_card is not None:
                with self.current_workflow_card:
                    ui.label(f"🔄 Active Workflow: {stats.get('workflow_id', 'Unknown')}").classes(
                        "text-h6 text-blue-600"
                    )
                    ui.label(f"Collection Points: {stats.get('collection_points', 0)}").classes("text-body2")
                    ui.label(f"Error Count: {stats.get('error_count', 0)}").classes("text-body2")
                    ui.label(f"Duration: {stats.get('total_duration_ms', 0):.1f}ms").classes("text-body2")

                    # Progress indicator
                    progress = ui.linear_progress().classes("w-full mt-2")
                    if hasattr(progress, "set_value") and progress is not None:
                        progress.set_value(0.5)  # Placeholder
        else:
            # No active workflow
            if self.current_workflow_card is not None:
                with self.current_workflow_card:
                    ui.label("⏸️ No Active Workflow").classes("text-h6 text-gray-600")
                    ui.label("Waiting for workflow to start...").classes("text-body2 text-gray-500")

    async def _update_recent_workflows_table(self, workflows: List[Dict[str, Any]]):
        """Update recent workflows table"""
        if not hasattr(self, "recent_workflows_table") or not NICEGUI_AVAILABLE:
            return

        # Prepare table data
        table_data = []
        for workflow in workflows:
            table_data.append(
                {
                    "workflow_id": workflow.get("workflow_id", "N/A")[:8] + "...",
                    "backlog_item": workflow.get("backlog_item_id", "N/A"),
                    "total_duration_ms": f"{workflow.get('total_duration_ms', 0):.1f}",
                    "performance_score": f"{workflow.get('performance_score', 0):.1f}",
                    "success": "✅" if workflow.get("success") else "❌",
                }
            )

        # Update table
        if hasattr(self.recent_workflows_table, "rows"):
            self.recent_workflows_table.rows = table_data

    async def _update_trends_chart(self, trends: List[Dict[str, Any]]):
        """Update performance trends chart"""
        if not hasattr(self, "trends_chart") or not trends or not NICEGUI_AVAILABLE:
            return

        # Prepare chart data
        dates = []
        durations = []

        for trend in trends[:10]:  # Last 10 data points
            date = trend.get("date", "")
            if date:
                dates.append(date)
                durations.append(trend.get("avg_duration_ms", 0))

        # Update chart - this would need to be implemented based on the chart library used
        logger.debug(f"Updating trends chart with {len(dates)} data points")

    async def _update_collection_points_chart(self, collection_points: List[Dict[str, Any]]):
        """Update collection points breakdown chart"""
        if not hasattr(self, "collection_points_chart") or not NICEGUI_AVAILABLE:
            return

        # Prepare chart data
        points = []
        durations = []

        for point in collection_points:
            point_name = point.get("collection_point", "").replace("_", " ").title()
            points.append(point_name)
            durations.append(point.get("avg_duration_ms", 0))

        # Update chart - this would need to be implemented based on the chart library used
        logger.debug(f"Updating collection points chart with {len(points)} data points")

    async def _refresh_data(self):
        """Manual refresh of dashboard data"""
        await self._update_dashboard_data()
        if NICEGUI_AVAILABLE:
            ui.notify("Dashboard data refreshed", type="positive")

    def _show_settings(self):
        """Show dashboard settings dialog"""
        if not NICEGUI_AVAILABLE:
            logger.warning("Settings dialog not available - NiceGUI not available")
            return

        with ui.dialog() as dialog, ui.card():
            ui.label("Dashboard Settings").classes("text-h6 mb-4")

            ui.label("Update Interval (seconds):")
            interval_input = ui.number(value=self.update_interval, min=1, max=60)

            ui.label("Storage Enabled:")
            storage_toggle = ui.switch(value=self.storage_enabled)

            with ui.row():
                ui.button(
                    "Save",
                    on_click=lambda: self._save_settings(
                        (
                            getattr(interval_input, "value", self.update_interval)
                            if interval_input is not None
                            else self.update_interval
                        ),
                        (
                            getattr(storage_toggle, "value", self.storage_enabled)
                            if storage_toggle is not None
                            else self.storage_enabled
                        ),
                        dialog,
                    ),
                )
                ui.button("Cancel", on_click=dialog.close if dialog is not None else lambda: None)

        if dialog is not None:
            dialog.open()

    def _save_settings(self, interval: float, storage_enabled: bool, dialog):
        """Save dashboard settings"""
        self.update_interval = interval
        self.storage_enabled = storage_enabled
        if hasattr(dialog, "close"):
            dialog.close()
        if NICEGUI_AVAILABLE:
            ui.notify("Settings saved", type="positive")

    def stop_dashboard(self):
        """Stop the performance dashboard"""
        self.is_running = False
        logger.info("Performance dashboard stopped")


class PerformanceWidget:
    """Embeddable performance widget for integration into other dashboards"""

    def __init__(self, container_id: str = "performance-widget"):
        self.container_id = container_id
        self.widget_data = {}

    def create_widget(self):
        """Create the performance widget"""
        if not NICEGUI_AVAILABLE:
            logger.warning("Creating mock performance widget - NiceGUI not available")
            return None

        with ui.card().classes("w-full") as widget:
            ui.label("📊 Workflow Performance").classes("text-h6 mb-2")

            # Performance summary
            with ui.row().classes("w-full gap-4"):
                with ui.column().classes("flex-1"):
                    ui.label("Active Workflows").classes("text-caption")
                    self.active_workflows_label = ui.label("0").classes("text-h4 text-blue-600")

                with ui.column().classes("flex-1"):
                    ui.label("Avg Duration").classes("text-caption")
                    self.avg_duration_label = ui.label("0ms").classes("text-h4 text-green-600")

                with ui.column().classes("flex-1"):
                    ui.label("Success Rate").classes("text-caption")
                    self.success_rate_label = ui.label("100%").classes("text-h4 text-orange-600")

            # Mini chart
            self.mini_chart = self._create_plotly_chart(title="", chart_type="line").classes("w-full h-24")

        return widget

    def _create_plotly_chart(self, title: str, chart_type: str = "line"):
        """Create a plotly chart component"""
        try:
            # Try to import plotly, but don't fail if not available
            import plotly.graph_objects as go  # type: ignore

            # Create a simple plotly figure
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[], y=[], mode="lines", name="Data"))
            fig.update_layout(title=title, height=100)

            # Return a div that will contain the plotly chart
            chart_div = ui.html(
                f"""
                <div id="mini-chart-{id(fig)}" style="width:100%; height:100px;">
                    <script>
                        Plotly.newPlot('mini-chart-{id(fig)}', {fig.to_json()});
                    </script>
                </div>
                """
            )
            return chart_div

        except (ImportError, ModuleNotFoundError):
            # Fallback to simple div if plotly not available
            fallback_html = (
                '<div style="width:100%; height:100px; border:1px solid #ccc; '
                'display:flex; align-items:center; justify-content:center;">Mini Chart</div>'
            )
            return ui.html(fallback_html)

    async def update_widget(self, performance_data: Dict[str, Any]):
        """Update widget with new performance data"""
        self.widget_data = performance_data

        # Update labels
        if hasattr(self, "active_workflows_label") and hasattr(self.active_workflows_label, "text"):
            self.active_workflows_label.text = str(performance_data.get("active_workflows", 0))

        if hasattr(self, "avg_duration_label") and hasattr(self.avg_duration_label, "text"):
            avg_duration = performance_data.get("avg_duration_ms", 0)
            self.avg_duration_label.text = f"{avg_duration:.1f}ms"

        if hasattr(self, "success_rate_label") and hasattr(self.success_rate_label, "text"):
            success_rate = performance_data.get("success_rate", 100)
            self.success_rate_label.text = f"{success_rate:.1f}%"

        # Update mini chart
        if hasattr(self, "mini_chart"):
            chart_data = performance_data.get("chart_data", [])
            # This would need to be implemented based on the chart library used
            logger.debug(f"Updating mini chart with {len(chart_data)} data points")


# Convenience functions for easy integration
async def start_performance_dashboard(port: int = 8080, storage_enabled: bool = True):
    """Start the performance dashboard"""
    dashboard = PerformanceDashboard(storage_enabled=storage_enabled)
    await dashboard.start_dashboard(port)
    return dashboard


def create_performance_widget(container_id: str = "performance-widget"):
    """Create an embeddable performance widget"""
    widget = PerformanceWidget(container_id)
    return widget.create_widget()


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Start Performance Dashboard")
    parser.add_argument("--port", type=int, default=8080, help="Dashboard port")
    parser.add_argument("--no-storage", action="store_true", help="Disable storage integration")

    args = parser.parse_args()

    # Start dashboard
    asyncio.run(start_performance_dashboard(port=args.port, storage_enabled=not args.no_storage))
