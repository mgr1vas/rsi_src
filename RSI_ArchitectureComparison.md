# Architectural Review: Deployment Options for RoadSafetyInsights

This document outlines the two primary deployment paths for the RoadSafetyInsights platform, breaking down the operational requirements, scalability, and cost estimates as the project transitions from the Naxos pilot phase to a nationwide rollout across Greece.

---

## Option 1: Serverless Architecture (Vercel + Supabase)

This approach leverages managed cloud services, separating the frontend hosting (Vercel) from the database and backend logic (Supabase).

### Architecture Overview
*   **Frontend & API Edge:** Vercel handles the web application, providing a global CDN and automatic SSL.
*   **Database & Auth:** Supabase provides a managed PostgreSQL database with PostGIS extensions out-of-the-box, alongside built-in user authentication.

### Operational Reality
*   **Zero-Maintenance:** No operating system updates, firewall configurations, or manual database backups required.
*   **Continuous Scraping Limitation:** Serverless functions have execution timeouts (10–60 seconds). Running long, continuous Python scraping loops across hundreds of regional Greek news sites is challenging and expensive in a pure serverless environment. 
*   **Development Speed:** Extremely fast iteration. The provided Supabase SDKs integrate smoothly with both the web application and the Flutter mobile app.

### Cost Scenarios (Usage-Based)
*   **Low Load (Naxos Pilot):** ~$0 – $20 / month (Free tiers mostly cover pilot usage).
*   **Medium Load (Regional Expansion):** ~$45 – $65 / month.
*   **High Load (Nationwide Greece):** ~$100 – $220+ / month (Costs scale with active users, bandwidth, and database storage).

---

## Option 2: Dedicated Server / Cloud VPS

This approach consolidates the entire stack onto a single Virtual Private Server (VPS) via providers like Hetzner, DigitalOcean, or a localized Ubuntu Server environment.

### Architecture Overview
*   **Containerized Stack:** The platform runs via `docker-compose`, orchestrating an Nginx reverse proxy, the FastAPI backend, and a PostgreSQL/PostGIS database container.
*   **Background Workers:** Python scrapers run as continuous, unlimited background daemons, freely extracting data and pushing it into the database.

### Operational Reality
*   **System Administration:** Requires active infrastructure management. Administrative access must be secured, ideally routing SSH traffic exclusively through a Tailscale VPN. Public-facing ports require mitigation strategies like Fail2ban to prevent brute-force attacks.
*   **Infrastructure Monitoring:** Requires dedicated oversight. Spikes in CPU or memory during heavy nationwide scraping loops can be tracked using a lightweight agent like Netdata.
*   **DevSecOps Integration:** Pairs perfectly with automated CI/CD pipelines. Upon passing Bandit (SAST) and OWASP ZAP (DAST) scans, GitHub Actions can automatically deploy the latest containers to the server.

### Cost Scenarios (Flat-Rate)
*   **Low Load (Naxos Pilot):** ~$5 – $8 / month (2 vCPU, 4GB RAM).
*   **Medium Load (Regional Expansion):** ~$15 – $25 / month (4 vCPU, 8GB RAM).
*   **High Load (Nationwide Greece):** ~$60 – $120 / month (8+ Dedicated Cores, 32GB+ RAM, NVMe storage for heavy PostGIS queries).

---

## Strategic Summary

*   Choose **Vercel + Supabase** to optimize for development speed, zero server maintenance, and seamless Flutter integration, accepting higher costs at scale and potential workarounds for data scraping.
*   Choose a **Dedicated Server** to optimize for predictable flat-rate costs, absolute control over security protocols, and ideal environments for continuous 24/7 Python scrapers, accepting the responsibility of system administration.
