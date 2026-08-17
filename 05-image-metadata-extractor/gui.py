from __future__ import annotations

import os
import sys
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox

# Your existing project keeps its application modules in src/.
PROJECT_DIR = Path(__file__).resolve().parent
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from extractor import read_exif_tags  # noqa: E402
from gps_parser import get_gps_coordinates  # noqa: E402
from map_renderer import render_location  # noqa: E402
from scrubber import scrub_metadata  # noqa: E402


class MetadataScoutApp:
    """Focused terminal-inspired GUI for the existing metadata workflow."""

    COLORS = {
        "background": "#0E1117",
        "panel": "#161B22",
        "panel_alt": "#1C2430",
        "border": "#303A48",
        "text": "#E6EDF3",
        "muted": "#8B98A8",
        "violet": "#8B7CFF",
        "violet_dark": "#5146B8",
        "teal": "#2DD4BF",
        "amber": "#F2CC60",
        "red": "#F07178",
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Metadata Scout — Local Image Intelligence")
        self.root.geometry("1040x660")
        self.root.minsize(820, 560)
        self.root.configure(bg=self.COLORS["background"])

        self.current_image_path: str | None = None
        self.current_coordinates: tuple[float, float] | None = None

        self.file_var = tk.StringVar(value="No image selected")
        self.camera_var = tk.StringVar(value="—")
        self.timestamp_var = tk.StringVar(value="—")
        self.gps_var = tk.StringVar(value="NOT FOUND")
        self.location_var = tk.StringVar(value="No GPS coordinates loaded")
        self.status_var = tk.StringVar(value="READY")

        self._build_interface()

    def _build_interface(self) -> None:
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_workspace()
        self._build_status_bar()

    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg=self.COLORS["panel"], height=74)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        brand_mark = tk.Frame(header, bg=self.COLORS["violet"], width=40, height=40)
        brand_mark.grid(row=0, column=0, padx=(22, 12), pady=17)
        brand_mark.grid_propagate(False)
        tk.Label(
            brand_mark,
            text="M",
            bg=self.COLORS["violet"],
            fg=self.COLORS["background"],
            font=("JetBrains Mono", 18, "bold"),
        ).place(relx=0.5, rely=0.5, anchor="center")

        title_box = tk.Frame(header, bg=self.COLORS["panel"])
        title_box.grid(row=0, column=1, sticky="w")
        tk.Label(
            title_box,
            text="METADATA SCOUT",
            bg=self.COLORS["panel"],
            fg=self.COLORS["text"],
            font=("JetBrains Mono", 15, "bold"),
        ).pack(anchor="w")
        tk.Label(
            title_box,
            text="LOCAL IMAGE INTELLIGENCE",
            bg=self.COLORS["panel"],
            fg=self.COLORS["muted"],
            font=("JetBrains Mono", 8),
        ).pack(anchor="w", pady=(1, 0))

        tk.Label(
            header,
            text="OFFLINE-FIRST  [ READY ]",
            bg=self.COLORS["panel"],
            fg=self.COLORS["teal"],
            font=("JetBrains Mono", 9, "bold"),
        ).grid(row=0, column=2, padx=22)

    def _build_workspace(self) -> None:
        workspace = tk.Frame(self.root, bg=self.COLORS["background"])
        workspace.grid(row=1, column=0, sticky="nsew", padx=20, pady=(18, 16))
        workspace.grid_rowconfigure(1, weight=1)
        workspace.grid_columnconfigure(1, weight=1)

        tk.Label(
            workspace,
            text="IMAGE METADATA ANALYSIS",
            bg=self.COLORS["background"],
            fg=self.COLORS["text"],
            font=("JetBrains Mono", 15, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))
        tk.Label(
            workspace,
            text="Select an original image to inspect embedded EXIF and GPS information.",
            bg=self.COLORS["background"],
            fg=self.COLORS["muted"],
            font=("JetBrains Mono", 9),
        ).grid(row=0, column=1, sticky="e", pady=(0, 4))

        sidebar = tk.Frame(
            workspace,
            bg=self.COLORS["panel"],
            highlightthickness=1,
            highlightbackground=self.COLORS["border"],
            width=250,
        )
        sidebar.grid(row=1, column=0, sticky="nsew", padx=(0, 14), pady=(12, 0))
        sidebar.grid_propagate(False)

        tk.Label(
            sidebar,
            text="WORKFLOW",
            bg=self.COLORS["panel"],
            fg=self.COLORS["muted"],
            font=("JetBrains Mono", 9, "bold"),
        ).pack(anchor="w", padx=14, pady=(16, 12))

        self.browse_button = self._action_button(
            sidebar, "Browse image", self.browse_file, self.COLORS["violet"]
        )
        self.browse_button.pack(fill="x", padx=12, pady=4)

        self.map_button = self._action_button(
            sidebar, "Open GPS map", self.open_map, self.COLORS["teal"], state="disabled"
        )
        self.map_button.pack(fill="x", padx=12, pady=4)

        self.scrub_button = self._action_button(
            sidebar, "Save clean copy", self.scrub_current, self.COLORS["amber"], state="disabled"
        )
        self.scrub_button.pack(fill="x", padx=12, pady=4)

        tk.Frame(sidebar, bg=self.COLORS["border"], height=1).pack(fill="x", padx=14, pady=20)
        tk.Label(
            sidebar,
            text="SESSION NOTES",
            bg=self.COLORS["panel"],
            fg=self.COLORS["muted"],
            font=("JetBrains Mono", 9, "bold"),
        ).pack(anchor="w", padx=14, pady=(0, 8))
        tk.Label(
            sidebar,
            text="All analysis happens locally. GPS will only appear when the original image still contains location metadata.",
            bg=self.COLORS["panel"],
            fg=self.COLORS["muted"],
            justify="left",
            wraplength=210,
            font=("JetBrains Mono", 9),
        ).pack(anchor="w", padx=14)
        tk.Label(
            sidebar,
            text="JPG · JPEG · TIFF",
            bg=self.COLORS["panel"],
            fg=self.COLORS["muted"],
            font=("JetBrains Mono", 8),
        ).pack(anchor="w", padx=14, side="bottom", pady=14)

        main = tk.Frame(
            workspace,
            bg=self.COLORS["panel"],
            highlightthickness=1,
            highlightbackground=self.COLORS["border"],
        )
        main.grid(row=1, column=1, sticky="nsew", pady=(12, 0))
        main.grid_rowconfigure(4, weight=1)
        main.grid_columnconfigure(0, weight=1)

        file_frame = self._field_frame(main, "SELECTED FILE", self.file_var)
        file_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 14))

        metrics = tk.Frame(main, bg=self.COLORS["panel"])
        metrics.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 14))
        metrics.grid_columnconfigure(0, weight=1)
        metrics.grid_columnconfigure(1, weight=1)
        metrics.grid_columnconfigure(2, weight=1)
        self._metric_card(metrics, 0, "CAMERA", self.camera_var, self.COLORS["violet"])
        self._metric_card(metrics, 1, "CAPTURE TIME", self.timestamp_var, self.COLORS["amber"])
        self._metric_card(metrics, 2, "GPS STATUS", self.gps_var, self.COLORS["teal"])

        location_frame = self._field_frame(main, "LOCATION", self.location_var)
        location_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 14))

        tk.Label(
            main,
            text="EXTRACTED DETAILS",
            bg=self.COLORS["panel"],
            fg=self.COLORS["muted"],
            font=("JetBrains Mono", 9, "bold"),
        ).grid(row=3, column=0, sticky="w", padx=16, pady=(0, 7))

        details = tk.Frame(main, bg=self.COLORS["panel_alt"])
        details.grid(row=4, column=0, sticky="nsew", padx=16, pady=(0, 16))
        details.grid_rowconfigure(0, weight=1)
        details.grid_columnconfigure(0, weight=1)

        self.results_text = tk.Text(
            details,
            state="disabled",
            wrap="word",
            relief="flat",
            borderwidth=0,
            bg=self.COLORS["panel_alt"],
            fg=self.COLORS["text"],
            selectbackground=self.COLORS["violet_dark"],
            font=("JetBrains Mono", 9),
            padx=14,
            pady=14,
        )
        self.results_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = tk.Scrollbar(details, command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=8)
        self.results_text.configure(yscrollcommand=scrollbar.set)

    def _build_status_bar(self) -> None:
        bar = tk.Frame(self.root, bg=self.COLORS["panel_alt"], height=30)
        bar.grid(row=2, column=0, sticky="ew")
        bar.grid_propagate(False)
        tk.Label(
            bar,
            textvariable=self.status_var,
            bg=self.COLORS["panel_alt"],
            fg=self.COLORS["muted"],
            font=("JetBrains Mono", 8),
        ).pack(side="left", padx=20, pady=7)
        tk.Label(
            bar,
            text="LOCAL FILE  |  NO UPLOAD",
            bg=self.COLORS["panel_alt"],
            fg=self.COLORS["teal"],
            font=("JetBrains Mono", 8),
        ).pack(side="right", padx=20, pady=7)

    def _action_button(self, parent, text: str, command, color: str, state: str = "normal") -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            state=state,
            relief="flat",
            bd=0,
            anchor="w",
            padx=12,
            pady=10,
            bg=self.COLORS["panel_alt"],
            fg=color,
            activebackground=self.COLORS["border"],
            activeforeground=color,
            disabledforeground="#4D5868",
            font=("JetBrains Mono", 9, "bold"),
            cursor="hand2",
        )

    def _field_frame(self, parent, label: str, variable: tk.StringVar) -> tk.Frame:
        frame = tk.Frame(parent, bg=self.COLORS["panel_alt"], highlightthickness=1, highlightbackground=self.COLORS["border"])
        frame.grid_columnconfigure(1, weight=1)
        tk.Label(
            frame,
            text=label,
            bg=self.COLORS["panel_alt"],
            fg=self.COLORS["muted"],
            font=("JetBrains Mono", 8, "bold"),
        ).grid(row=0, column=0, padx=(12, 14), pady=11, sticky="w")
        tk.Label(
            frame,
            textvariable=variable,
            bg=self.COLORS["panel_alt"],
            fg=self.COLORS["text"],
            anchor="w",
            font=("JetBrains Mono", 9),
        ).grid(row=0, column=1, padx=(0, 12), pady=11, sticky="ew")
        return frame

    def _metric_card(self, parent, column: int, label: str, variable: tk.StringVar, accent: str) -> None:
        card = tk.Frame(parent, bg=self.COLORS["panel_alt"], highlightthickness=1, highlightbackground=self.COLORS["border"])
        card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 5, 5 if column < 2 else 0))
        tk.Label(card, text=label, bg=self.COLORS["panel_alt"], fg=self.COLORS["muted"], font=("JetBrains Mono", 8, "bold")).pack(anchor="w", padx=11, pady=(10, 4))
        tk.Label(card, textvariable=variable, bg=self.COLORS["panel_alt"], fg=accent, anchor="w", wraplength=150, font=("JetBrains Mono", 9, "bold")).pack(anchor="w", padx=11, pady=(0, 10))

    def browse_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Select a photo",
            filetypes=[("Images", "*.jpg *.jpeg *.tif *.tiff"), ("All files", "*.*")],
        )
        if path:
            self._analyze(path)

    def _analyze(self, path: str) -> None:
        self.current_image_path = path
        self.current_coordinates = None
        self.file_var.set(Path(path).name)
        self.camera_var.set("—")
        self.timestamp_var.set("—")
        self.gps_var.set("NOT FOUND")
        self.location_var.set("No GPS coordinates loaded")
        self.map_button.configure(state="disabled")
        self.scrub_button.configure(state="normal")
        self.status_var.set("READING EXIF...")

        try:
            tags = read_exif_tags(path)
        except Exception as exc:
            self._show_results(f"ERROR\n\nCould not read this file as an image.\n{exc}")
            self.status_var.set("ERROR")
            return

        make = tags.get("Image Make")
        model = tags.get("Image Model")
        camera = f"{make or ''} {model or ''}".strip()
        timestamp = tags.get("EXIF DateTimeOriginal") or tags.get("Image DateTime")
        coordinates = get_gps_coordinates(tags)

        self.camera_var.set(camera or "NOT RECORDED")
        self.timestamp_var.set(str(timestamp) if timestamp else "NOT RECORDED")
        self.current_coordinates = coordinates

        lines = [
            f"> FILE      {Path(path).name}",
            f"> CAMERA    {camera or 'not recorded'}",
            f"> CAPTURED  {timestamp or 'not recorded'}",
        ]
        if coordinates:
            latitude, longitude = coordinates
            coordinate_text = f"{latitude:.6f}, {longitude:.6f}"
            lines.append(f"> GPS       {coordinate_text}")
            self.gps_var.set("FOUND")
            self.location_var.set(f"GPS available  |  {coordinate_text}")
            self.map_button.configure(state="normal")
        else:
            lines.append("> GPS       not found in this image")

        lines.extend([
            "",
            "STATUS    metadata read completed",
            "SOURCE    local file; no upload performed",
        ])
        self._show_results("\n".join(lines))
        self.status_var.set("ANALYSIS COMPLETE")

    def _show_results(self, text: str) -> None:
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.configure(state="disabled")

    def open_map(self) -> None:
        if self.current_coordinates is None:
            messagebox.showinfo("No GPS data", "This image has no GPS coordinates to show.")
            return

        latitude, longitude = self.current_coordinates
        output_path = os.path.abspath("location_map.html")
        try:
            render_location(latitude, longitude, output_path)
            webbrowser.open(Path(output_path).resolve().as_uri())
            self.status_var.set("MAP OPENED IN BROWSER")
        except Exception as exc:
            messagebox.showerror("Map error", f"Could not create the map:\n\n{exc}")

    def scrub_current(self) -> None:
        if not self.current_image_path:
            messagebox.showinfo("No photo loaded", "Browse for a photo first.")
            return

        source = Path(self.current_image_path)
        save_path = filedialog.asksaveasfilename(
            title="Save clean copy as...",
            initialdir=str(source.parent),
            initialfile=f"{source.stem}_clean{source.suffix.lower()}",
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg *.jpeg"), ("TIFF", "*.tif *.tiff")],
        )
        if not save_path:
            return

        try:
            scrub_metadata(str(source), save_path)
            messagebox.showinfo("Done", f"Clean copy saved to:\n{save_path}")
            self.status_var.set("CLEAN COPY SAVED")
        except Exception as exc:
            messagebox.showerror("Scrub error", f"Could not scrub this image:\n\n{exc}")


def main() -> None:
    root = tk.Tk()
    MetadataScoutApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
