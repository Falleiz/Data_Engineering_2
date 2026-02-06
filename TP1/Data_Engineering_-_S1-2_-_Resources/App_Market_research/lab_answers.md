# Lab 1 Answers: AI Note-Taking Apps Market Analysis

**Authors**: BELEMCOABGA Rosteim Falleiz, MENDY Vincent

---

## 1. Which applications appear to perform best or worst according to user reviews?

![Best vs Worst Apps](../../../assets/dashboard_q1.png)

Based on our analysis of the `app_level_kpis.csv` dataset (filtered for apps with significant volume):

*   **Best Performing**: Apps like **"iMemo AI Note Taker"** and **"Freenotes"** consistently achieve high ratings (**~4.7/5.0**).
*   **Worst Performing**: Apps such as **"Wave AI Note Taker"** and **"OtterAI"** show significantly lower satisfaction scores (**< 3.5/5.0**).

*Note: The distinction is clear, with top-tier apps maintaining near-perfect scores while lower-tier apps struggle with user satisfaction despite having visibility.*

## 2. Are user ratings improving or declining over time?

![User Ratings Trends](../../../assets/dashboard_q2.png)

Analyzing the temporal trends in `daily_metrics.csv`:

*   **Observation**: The global average rating has remained **remarkably stable** around **4.0 - 4.3** over the analyzed period.
*   **Conclusion**: There is no significant decline in user satisfaction despite the market growing in volume. This suggests that the leading apps are successfully maintaining their quality standards as they scale.

## 3. Are there noticeable differences in review volume between applications?

![Review Volume Distribution](../../../assets/dashboard_q3.png)

*   **Observation**: Yes, the difference is extreme. The market follows a "Power Law" (Long Tail) distribution.
*   **Details**: A very small number of applications (e.g., **Microsoft OneNote**, **Notion**) capture the vast majority of user reviews (thousands), while dozens of other apps have fewer than 100 reviews.
*   **Implication**: The market is highly concentrated among a few dominant players.

---

## Dashboard Summary

![Market Overview](../../../assets/dashboard_overview.png)

*As displayed in the Streamlit Dashboard:*

The analysis shows a **highly concentrated market** where a small number of top applications dominate in review volume. Despite the growth in volume, the overall **user rating trend remains stable**, indicating that the leading apps are maintaining quality as they scale compared to lower-rated competitors.
