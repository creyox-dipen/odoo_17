17.0.0.0 (Date: 7th July, 2026)
--------------------------------
- Migrated module from version 18.

17.0.0.1 (Date: 14th July, 2026)
--------------------------------
- Real-time dynamic payment fee calculation badge in checkout UI based on selected payment method and card brand (Visa, Mastercard, etc.).
- Integrated client-side Stripe Elements change listener to detect card brand dynamically.
- Implemented backend API endpoint to fetch card brand from token for saved payment methods.
- Fixed international fee calculation by checking Sales Order shipping/delivery address country instead of billing partner country.
- Resolved transaction retry issues by unlinking previous payment fee lines and adjusting the transaction amount post-creation to prevent surcharge amount inflation.
- Fixed concurrent order confirmation crash ("partner cannot follow twice") by wrapping follower record insertion in a database savepoint.