import os
from django.core.management.base import BaseCommand
from django.conf import settings

from member.models import Role
from saskatoon.permissions import ALL_PERMISSIONS


class Cell:
    """Markdown table cell"""

    def __init__(self, content: str, width: int):
        self.content = content
        self.width = width

    def __str__(self) -> str:
        return self.content.ljust(self.width)


class Row:
    """Markdown table row"""

    def __init__(self, values: list[str], widths: list[int]):
        self.cells = [Cell(v, w) for v, w in zip(values, widths)]

    def __str__(self) -> str:
        return f"| {' | '.join(str(cell) for cell in self.cells)} |"


class Headers(Row):
    """Markdown table header row"""

    def __init__(self, cells: list[Cell]):
        self.cells = cells

    @property
    def widths(self) -> list[int]:
        return [cell.width for cell in self.cells]


class Table:
    """Markdown table"""

    def __init__(self, headers: Headers):
        self.headers: Headers = headers
        self.rows: list[Row] = []

    def add_row(self, values: list[str]) -> None:
        self.rows.append(Row(values, self.headers.widths))

    def render(self, title: str) -> str:
        separator = Row(["-" * w for w in self.headers.widths], self.headers.widths)
        lines = [
            f"## {title}\n",
            str(self.headers),
            str(separator),
        ] + [str(row) for row in self.rows]
        return "\n".join(lines)


class Command(BaseCommand):
    help = "Export permissions as markdown tables to doc/permissions.md"

    def handle(self, *args, **options):
        roles = list(Role)
        actions = ["add", "change", "view", "delete"]
        action_col_width = max(len(a) for a in actions)

        output = "# Permissions\n\n"
        output += "> This file is auto-generated. Do not edit it directly.\n"
        output += "> Edit `PERMISSIONS` dict in each app's `permissions.py` file,\n"
        output += "> then run `make permissions` to regenerate.\n\n"

        for app_label, models in ALL_PERMISSIONS.items():
            table = Table(Headers(
                [Cell("model", max(len(m) for m in models)),
                 Cell("action", action_col_width)]
                + [Cell(r, len(r)) for r in roles]
            ))

            for model_name, model_actions in models.items():
                for i, action in enumerate(actions):
                    granted_roles = model_actions.get(action, set())
                    display_name = model_name if i == 0 else ""
                    table.add_row([display_name, action] + [
                        "x" if r in granted_roles else "" for r in roles
                    ])

            output += table.render(app_label) + "\n\n"

        output_path = os.path.join(settings.BASE_DIR, "..", "doc", "permissions.md")
        with open(output_path, "w") as f:
            f.write(output)

        self.stdout.write(self.style.SUCCESS(f"Exported permissions to {output_path}"))

        # Dump output to stdout
        # self.stdout.write(output)
