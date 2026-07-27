# Cost Breakdown: Flutter + Supabase Architecture

### Stage 1: The Pilot Phase
As the application rolls out in Naxos and the rent-a-car fleet begins running routes, our operating costs will be exactly **$0 per month**. 

Supabase offers a generous Free tier that easily covers early-stage MVPs:
*   **Database:** 500 MB of Postgres storage (with the necessary PostGIS extensions supported).
*   **Users:** Up to 50,000 Monthly Active Users (MAUs).
*   **Bandwidth:** 5 GB of database egress per month.
*   **The only catch:** Free projects automatically pause after one week of inactivity. As long as the team or the fleet drivers are actively using the app and querying the database at least once every 7 days, this will not be an issue.

### Stage 2: Production & Scaling
Once the application proves successful and we begin scaling traffic, we will need to upgrade to the **Pro Plan at $25 per month**. 

This tier introduces production-grade safety nets and significantly higher limits:
*   **Database Expansion:** Increases storage to 8 GB.
*   **User Scaling:** Supports up to 100,000 MAUs.
*   **Bandwidth Increase:** Jumps to 250 GB of egress.
*   **Data Security:** Includes automated daily backups with a 7-day retention period, which is absolutely critical once you are dealing with live production data.

### App Store Registration
While the database costs are completely covered, we will need to account for the standard developer fees required to distribute the compiled Flutter application to the public:
*   **Google Play Store (Android):** A one-time registration fee of **$25**.
*   **Apple App Store (iOS):** An annual subscription fee of **$99/year**.
