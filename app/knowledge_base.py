"""The knowledge base Claude uses when drafting a suggested first response.

This is the file you should customize most. Add your organization's real
procedures, common fixes, and escalation rules. The better this is, the
smarter the triage feels.
"""

KNOWLEDGE_BASE = """
## Categories
- hardware: physical devices — laptops, monitors, printers, docks, peripherals
- software: application errors, installs, licenses, updates
- network: Wi-Fi, VPN, DNS, connectivity, slow internet
- access: password resets, account lockouts, permissions, new-hire provisioning
- security: phishing reports, suspicious activity, malware, lost devices
- other: anything that doesn't fit the above

## Priority rules
- P1 (critical): outage affecting multiple users, security incident, data loss risk
- P2 (high): one user fully blocked from working, deadline-impacting
- P3 (normal): degraded but workable, routine requests
- P4 (low): questions, cosmetic issues, nice-to-haves

## Common fixes
- VPN won't connect: restart the client, verify MFA token time sync, try wired connection
- Password reset: direct user to the self-service portal at reset.example.com; resets take effect within 5 minutes
- Printer offline: power-cycle the printer, check it's on the STAFF-PRINT network, reinstall the driver from the software center
- Slow laptop: check for pending Windows updates, restart, check disk space (>10% free required)
- Phishing email: do NOT click links; forward to security@example.com and delete
- Software install request: standard catalog apps are self-service in the software center; non-catalog apps need manager approval

## Escalation
- Security incidents (P1): notify the security team immediately, do not troubleshoot alone
- Hardware failures under warranty: log serial number, open vendor RMA
"""
