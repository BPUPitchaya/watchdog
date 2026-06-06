import flet as ft
from flet import border
import sys

def tnc_view(page: ft.Page):
    # The Markdown string containing the T&C text
    tc_text = """
### WatchDog AI – End User License Agreement 

**Please read these terms carefully before using WatchDog AI.** By clicking "I Agree" or continuing to use this software, you agree to be bound by these Terms and Conditions.

**1. Acknowledgment of MVP Status**
WatchDog AI is provided as a Minimum Viable Product (MVP) and diagnostic tool. While the system utilizes machine learning to detect network anomalies and automate defenses, it is not a guarantee of absolute cybersecurity. The developers (Pitchaya and Thae) provide this software "as is" and without warranties of any kind. 

**2. Authorized Use & Legal Compliance**
WatchDog AI utilizes active packet-sniffing technology. By using this software, you explicitly warrant that:
* You are the owner, or have explicit authorization from the owner, of the network and hardware being monitored.
* You will not use this application to intercept, monitor, or capture data on networks or devices you do not have legal permission to audit.
* Your use of this software complies with all applicable local and national cybersecurity legislation, including the New Zealand Computer Act. 

**3. Data Privacy and Edge Processing**
WatchDog AI is built on an "Uncompromising Data Sovereignty" architecture. We respect your privacy. 
* **Zero Cloud Transmission:** All network packet ingestion, machine learning threat analysis, and Explainable AI (XAI) log generation occur entirely on your local hardware (Edge computing).
* No network telemetry, packet data, or system logs are ever transmitted to external servers, third-party APIs, or the developers. This localized processing aligns with the standards set by the New Zealand Privacy Act 2020.

**4. Automated Mitigation & System Modifications**
WatchDog AI includes an automated firewall mitigation feature that may actively alter your operating system’s IP blocking rules to stop perceived threats. 
* You acknowledge that automated mitigation carries the risk of "false positives," which may temporarily block legitimate business traffic or services. 
* While fail-safes are built-in, you are solely responsible for reviewing the AI Assistant's logs and managing your firewall rules.

**5. Limitation of Liability**
To the maximum extent permitted by law, the developers shall not be held liable for any direct, indirect, incidental, or consequential damages resulting from the use or inability to use this software. This includes, but is not limited to, data loss, business interruption, successful cyberattacks, or network outages caused by automated firewall modifications.

**6. Governing Law**
These terms shall be governed by and construed in accordance with the laws of New Zealand.
"""

    def accept_clicked(e):
        # INSTEAD of clearing controls, route to the dashboard!
        page.go("/dashboard")

    def decline_clicked(e):
        # Exits the application if the user declines the terms
        sys.exit()

    tc_markdown = ft.Markdown(
        value=tc_text,
        selectable=True,
        extension_set="gitHubWeb",
    )

    tc_container = ft.Container(
        content=ft.Column(
            controls=[tc_markdown],
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        padding=20,
        border=border.all(1, ft.Colors.OUTLINE),
        border_radius=10,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST, 
    )

    action_buttons = ft.Row(
        controls=[
            ft.ElevatedButton(
                text="Decline & Exit", 
                color=ft.Colors.ERROR, 
                on_click=decline_clicked
            ),
            ft.ElevatedButton(
                text="I Agree", 
                bgcolor=ft.Colors.PRIMARY, 
                color=ft.Colors.ON_PRIMARY, 
                on_click=accept_clicked
            ),
        ],
        alignment=ft.MainAxisAlignment.END,
    )

    # Return a View object containing the layout for the router
    return ft.View(
        route="/tnc",
        controls=[
            ft.Text("WatchDog AI Setup", size=28, weight=ft.FontWeight.BOLD),
            tc_container,
            action_buttons
        ],
        padding=30,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER
    )