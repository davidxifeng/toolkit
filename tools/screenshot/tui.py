"""
Screenshot Organizer - TUI Interface
Beautiful terminal user interface using Textual.
"""

from pathlib import Path
from typing import Optional

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header, Footer, Button, Static, ProgressBar, 
    ListView, ListItem, Label, DirectoryTree, Input
)
from textual.reactive import reactive
from textual.worker import get_current_worker

from .organizer import ScreenshotOrganizer, OperationMode, OrganizeResult


class SettingsPanel(Container):
    """Settings panel for configuring organizer options"""
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Settings", classes="panel-title")
            yield Label("Source Directory:")
            yield Input(
                placeholder="~/Desktop", 
                id="source-input",
                value=str(Path.home() / "Desktop")
            )
            yield Label("Target Directory:")
            yield Input(
                placeholder="~/Screenshots", 
                id="target-input",
                value=str(Path.home() / "Desktop" / "Screenshots")
            )
            yield Label("Mode:")
            yield Horizontal(
                Button("Move", id="mode-move", variant="primary"),
                Button("Copy", id="mode-copy"),
                classes="mode-buttons"
            )


class FileListPanel(Container):
    """Panel showing files to be processed"""
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Files to Process", classes="panel-title")
            yield ListView(id="file-list")
            yield Static("0 files found", id="file-count")


class StatusPanel(Container):
    """Panel showing processing status"""
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Processing Status", classes="panel-title")
            yield ProgressBar(id="progress-bar")
            yield Static("Ready", id="status-text")
            yield Static("Files: 0/0", id="file-counter")


class ResultsPanel(Container):
    """Panel showing results summary"""
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Results Summary", classes="panel-title")
            yield Static("No operations performed yet", id="results-text")


class ScreenshotOrganizerApp(App):
    """Main TUI application"""
    
    CSS = """
    .panel-title {
        background: $primary;
        color: $text;
        text-align: center;
        text-style: bold;
        padding: 1;
    }
    
    .mode-buttons {
        height: 3;
        margin: 1;
    }
    
    #main-container {
        layout: grid;
        grid-size: 2 3;
        grid-gutter: 1;
        margin: 1;
    }
    
    #controls {
        column-span: 2;
        height: 4;
        layout: horizontal;
        align: center middle;
    }
    
    #controls Button {
        margin: 0 1;
    }
    
    FileListPanel {
        row-span: 2;
    }
    
    ListView {
        height: 1fr;
        border: solid $primary;
    }
    
    ProgressBar {
        margin: 1 0;
    }
    
    Input {
        margin: 0 0 1 0;
    }
    """
    
    TITLE = "Screenshot Organizer"
    
    # Reactive attributes
    current_mode = reactive(OperationMode.OPTIMIZE_MOVE)
    source_dir = reactive(Path.home() / "Desktop")
    target_dir = reactive(Path.home() / "Desktop" / "Screenshots")
    files_found = reactive(0)
    is_processing = reactive(False)

    def __init__(self):
        super().__init__()
        self.organizer: Optional[ScreenshotOrganizer] = None
        self.current_files = []
        self.keep_original = False
        
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Container(id="main-container"):
            yield FileListPanel()
            yield SettingsPanel()
            yield StatusPanel()
            yield ResultsPanel()
            
        with Container(id="controls"):
            yield Button("Scan Files", id="scan-btn", variant="primary")
            yield Button("Preview", id="preview-btn")
            yield Button("Start", id="start-btn", variant="success")
            yield Button("Exit", id="exit-btn", variant="error")
            
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the app"""
        self.refresh_organizer()
        self.scan_files()
    
    def refresh_organizer(self) -> None:
        """Refresh the organizer with current settings"""
        self.organizer = ScreenshotOrganizer(
            source_dir=self.source_dir,
            target_dir=self.target_dir,
            mode=self.current_mode
        )
        
        def progress_callback(current: int, total: int, filename: str):
            progress_bar = self.query_one("#progress-bar", ProgressBar)
            status_text = self.query_one("#status-text", Static)
            file_counter = self.query_one("#file-counter", Static)
            
            progress_bar.update(progress=current / total * 100)
            status_text.update(f"Processing: {Path(filename).name}")
            file_counter.update(f"Files: {current}/{total}")
            
        self.organizer.set_progress_callback(progress_callback)
    
    def scan_files(self) -> None:
        """Scan for screenshot files"""
        if not self.organizer:
            return
            
        files = self.organizer.find_screenshot_files()
        self.current_files = files
        self.files_found = len(files)
        
        # Update file list
        file_list = self.query_one("#file-list", ListView)
        file_count = self.query_one("#file-count", Static)
        
        file_list.clear()
        for file_path in files:
            file_list.append(ListItem(Label(file_path.name)))
            
        file_count.update(f"{len(files)} files found")
    
    @on(Button.Pressed, "#scan-btn")
    def on_scan_pressed(self) -> None:
        """Handle scan button press"""
        self.scan_files()
    
    @on(Button.Pressed, "#preview-btn")
    def on_preview_pressed(self) -> None:
        """Handle preview button press"""
        if self.is_processing or not self.organizer:
            return
            
        self.run_worker(self.preview_organization, exclusive=True)
    
    @on(Button.Pressed, "#start-btn")
    def on_start_pressed(self) -> None:
        """Handle start button press"""
        if self.is_processing or not self.organizer:
            return
            
        self.run_worker(self.organize_files, exclusive=True)
    
    @on(Button.Pressed, "#exit-btn")
    def on_exit_pressed(self) -> None:
        """Handle exit button press"""
        self.exit()
    
    @on(Button.Pressed, "#mode-move")
    def on_mode_move_pressed(self) -> None:
        """Switch to move mode"""
        self.current_mode = OperationMode.MOVE
        move_btn = self.query_one("#mode-move", Button)
        copy_btn = self.query_one("#mode-copy", Button)
        move_btn.variant = "primary"
        copy_btn.variant = "default"
        self.refresh_organizer()
    
    @on(Button.Pressed, "#mode-copy")
    def on_mode_copy_pressed(self) -> None:
        """Switch to keep original mode"""
        self.current_mode = OperationMode.OPTIMIZE_MOVE
        self.keep_original = True
        move_btn = self.query_one("#mode-move", Button)
        copy_btn = self.query_one("#mode-copy", Button)
        move_btn.variant = "default"
        copy_btn.variant = "primary"
        self.refresh_organizer()
    
    @on(Input.Changed, "#source-input")
    def on_source_changed(self, event: Input.Changed) -> None:
        """Handle source directory change"""
        try:
            self.source_dir = Path(event.value).expanduser()
            self.refresh_organizer()
        except Exception:
            pass  # Invalid path, ignore
    
    @on(Input.Changed, "#target-input")
    def on_target_changed(self, event: Input.Changed) -> None:
        """Handle target directory change"""
        try:
            self.target_dir = Path(event.value).expanduser()
            self.refresh_organizer()
        except Exception:
            pass  # Invalid path, ignore
    
    async def preview_organization(self) -> None:
        """Preview organization (worker)"""
        self.is_processing = True
        
        status_text = self.query_one("#status-text", Static)
        status_text.update("Previewing...")
        
        try:
            result = self.organizer.organize_files(preview_only=True)
            self.update_results(result, preview=True)
            
        except Exception as e:
            status_text.update(f"Error: {str(e)}")
            
        finally:
            self.is_processing = False
            progress_bar = self.query_one("#progress-bar", ProgressBar)
            progress_bar.update(progress=0)
    
    async def organize_files(self) -> None:
        """Organize files (worker)"""
        self.is_processing = True
        
        try:
            result = self.organizer.organize_files(preview_only=False)
            self.update_results(result, preview=False)
            
            # Refresh file list after organizing
            self.scan_files()
            
        except Exception as e:
            status_text = self.query_one("#status-text", Static)
            status_text.update(f"Error: {str(e)}")
            
        finally:
            self.is_processing = False
            progress_bar = self.query_one("#progress-bar", ProgressBar)
            status_text = self.query_one("#status-text", Static)
            progress_bar.update(progress=100)
            status_text.update("Completed")
    
    def update_results(self, result: OrganizeResult, preview: bool = False) -> None:
        """Update results panel"""
        results_text = self.query_one("#results-text", Static)
        
        mode_text = "PREVIEW" if preview else ("OPTIMIZED" if hasattr(self, 'keep_original') and self.keep_original else "OPTIMIZED & MOVED")
        
        summary = []
        summary.append(f"Total files: {result.total_files}")
        summary.append(f"Processed: {result.processed_files}")
        
        if result.failed_files > 0:
            summary.append(f"Failed: {result.failed_files}")
        
        if result.created_folders:
            summary.append(f"\nFolders {'would be created' if preview else 'created'}:")
            for folder in sorted(result.created_folders):
                rel_path = folder.relative_to(self.target_dir)
                summary.append(f"  📁 {rel_path}")
        
        if result.failed_files > 0:
            summary.append(f"\nErrors:")
            for res in result.results:
                if not res.success and res.error_message:
                    summary.append(f"  ❌ {res.source_path.name}: {res.error_message}")
        
        results_text.update(f"{mode_text} Results:\n\n" + "\n".join(summary))


# Alias for backward compatibility
ScreenshotTUI = ScreenshotOrganizerApp


def main():
    """Run the TUI application"""
    app = ScreenshotOrganizerApp()
    app.run()


if __name__ == "__main__":
    main()