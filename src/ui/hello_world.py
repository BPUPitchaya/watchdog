import flet as ft


def main(page: ft.Page):
    """Basic Hello World Flet application for Watchdog."""
    page.title = "Watchdog - Network Security Monitor"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLUE_GREY_50

    # Main title
    title = ft.Text(
        "Hello, Watchdog!",
        size=40,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_GREY_800
    )

    # Subtitle
    subtitle = ft.Text(
        "Network Intrusion Detection System",
        size=20,
        color=ft.Colors.BLUE_GREY_600
    )

    # Status indicator
    status = ft.Text(
        "Status: Ready",
        size=16,
        color=ft.Colors.GREEN_600
    )

    # Container for main content
    content = ft.Column(
        [
            title,
            subtitle,
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            status
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )

    # Add content to page
    page.add(content)


if __name__ == "__main__":
    ft.run(target=main)
