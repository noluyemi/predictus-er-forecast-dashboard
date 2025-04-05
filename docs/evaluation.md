**Evaluation & Use Case: ER Forecast + Flu Overlay**

**Purpose**
This dashboard allows public health professionals, hospital administrators, and policy leaders to visualize projected ER visit volumes alongside flu season severity, giving them early insight for staffing, triage, and resource planning.

**Why Overlay Flu Data?**
Seasonal influenza is a key driver of ER spikes. By integrating CDC ILINet data (average % of outpatient visits for flu-like illness), we:

- Reveal patterns that mirror or diverge from flu season
- Help decision-makers determine if upcoming surges are flu-related or possibly due to other emerging threats
- Promote equity-driven planning in regions with under-resourced ER systems

**Technical Notes:**
- Forecasts are generated using Prophet (Meta) on public CDC/HHS datasets
- Flu data is sourced from CDC FluView (ILINet) and mapped by year
- Dual-axis plots present ER forecasts (left axis) and flu trends (right axis)

**Example Insight**
In the Midwest, the 2023 ER surge forecast closely aligns with a 5% flu trend spike — indicating a likely seasonal overload.
In contrast, the South region’s forecast for 2025 shows an uptick not explained by flu, suggesting a need to investigate non-flu drivers (e.g., heat, mobility, RSV, or environmental alerts).

**Limitations:**
- ILINet data is national (not state-specific in this version)
- Flu data currently available only up to 2023
- Future versions will integrate weather anomalies, Google mobility trends, and capacity APIs
