# RoadSafetyInsights (RSI) - Database Architecture & Progress

## 1. Architectural Decision: Supabase vs. Firebase

When evaluating the backend infrastructure for the RSI platform, we analyzed both Firebase and Supabase. Here is the comparative breakdown that led to our decision:

### Firebase (Google)
* Firebase uses a NoSQL document model (Firestore) where data is stored as JSON-like documents.
* Firebase provides a fully managed ecosystem that is highly optimized for mobile-first applications and offline synchronization.
* Firebase pricing is usage-based, charging primarily for document reads, writes, and bandwidth.
* Firebase lacks native support for complex SQL joins, which often forces developers to denormalize data across collections.
* Firebase is proprietary Google infrastructure, meaning there is no option to self-host the database.

### Supabase (Open-Source)
* Supabase is an open-source platform built directly on a PostgreSQL relational database.
* Supabase handles relational data natively, supporting proper tables, foreign keys, and complex SQL joins.
* Supabase pricing is generally based on predictable compute and storage tiers rather than per-request billing.
* Supabase allows developers to inspect the code and self-host the entire stack, providing a clear exit strategy from vendor lock-in.
* Supabase supports standard PostgreSQL extensions, including PostGIS for advanced geospatial queries.

### The Verdict for RSI
For a platform like Road Safety Insights, **geospatial querying is a core requirement.** Because Supabase supports PostGIS, it allows us to perform complex radius searches and map intersections natively at the database level. Firebase would require us to pull massive amounts of data to the client to filter locations manually or rely on third-party workarounds. Furthermore, as our data structure relies heavily on relational analytics (e.g., cross-referencing severity, jurisdiction, and user reports), Supabase's SQL foundation is the clear technical choice.

---

## 2. Current Progress: Supabase Implementation

To prepare the backend for the `data.gov.gr` integration, we have successfully established and verified a secure connection between our Python ETL (Extract, Transform, Load) script and the Supabase PostgreSQL database. 

### Milestones Achieved Today:
* **Project Configuration:** Initialized the Supabase environment and secured project credentials using local `.env` variables.
* **Schema Initialization:** Used the Supabase SQL Editor to provision a `Testing` table equipped with an auto-generating `id` (primary key) and a `created_at` timestamp.
* **Schema Evolution & Cache Management:** Dynamically appended a `message` (text) column via the Table Editor. We successfully identified and resolved a schema cache latency issue (`Error PGRST204`) by forcing a manual reload of the Data API schema.
* **Security & Authentication (RLS):** Encountered and analyzed default Row-Level Security (RLS) protections (`Error 42501`) when attempting unauthorized writes from the client script.
* **Secure Backend Pipeline Implementation:** Instead of disabling security (RLS) on the database, we properly architected our Python script to use the Supabase `service_role` secret key. This securely bypasses public RLS policies for backend administrative tasks, allowing our script to successfully inject data into the system without compromising public-facing security.

### Next Steps:
With the backend connection tested, secured, and communicating properly with the database, the pipeline is ready to ingest and filter the Naxos/Cyclades traffic accident CSV data from the `data.gov.gr` API directly into our production tables.
