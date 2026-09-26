17.0.0.1(Date: 26th September,2026)
-----------------------------------
- Fixed multi-company webhook processing: ensure statement, lines, fee reversals, and payout internal transfers execute within the Stripe journal's company context.

17.0.0.0(Date: 4th August,2026)
-------------------------------
- Migrated from version 18
- Migrated and added all features of enterprise version.
- fees account selectable in payment provider.
- used partner's receivable account instead of hardcoded account in statement line.
- auto reconcile credit note for refund statement.