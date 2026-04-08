# Agent Pattern Analysis for Hazmat Co-Pilot

Based on the analysis of the `Repeatable Patterns` and the below outlines the agent pattern for the Hazmat Co-Pilot use case.

## Pattern Used: A Hybrid of **Information Synthesis Agent** and **Specialist/Router Orchestration**

The Hazmat Co-Pilot fits best as an **Information Synthesis Agent** that operates within a **multi-agent "Specialist" team** (a form of workflow orchestration).

---

## Why this pattern fits the Hazmat Co-Pilot use case:

### 1. Why **Information Synthesis Agent**?
*   **Core Goal:** The document defines this pattern as being for when "your primary goal is information retrieval, analysis, and synthesis without modifying any data." This perfectly matches our goal of reading dense, multi-page SDS PDFs and synthesizing the information for users.
*   **Read-Only "Talk to Your Data":** The pattern allows users to converse with their data. Frontline workers and compliance officers are asking questions against a fixed knowledge base (the SDS database) without changing it.
*   **Persona Adaptation:** This pattern supports consolidating massive, disparate collections of documents that a single user cannot easily reason over, which is exactly the case with 16-section technical SDS files.

### 2. Why add **Specialist/Router Orchestration**?
*   While the PDF describes the "Information Synthesis Agent" as potentially monolithic, it also notes that it can be a **multi-agent system** that orchestrates specialized agents.
*   In our `brainstorming_summary.md`, we explicitly decided to use a **Multi-Agent "Specialist" Team** pattern:
    *   **Workplace Safety Agent:** Specialized in Section 8 (PPE) and simple, direct tone for workers.
    *   **Regulatory Advisor Agent:** Specialized in Section 15 (Regulatory) and formal, cited tone for compliance officers.
*   This requires a routing mechanism (a "Router Agent" or high-level orchestrator) to detect the user's role and intent and dispatch the query to the correct specialist. This aligns with the concepts in the **Hierarchical Workflow Automation** section of the PDF, which mentions using a "Router Agent" to manage tool/agent choice.

## Summary of the Hazmat Co-Pilot Pattern:
*   **Goal:** Information Synthesis (RAG over SDS PDFs).
*   **Architecture:** Multi-agent team with a Router and Specialists (Workplace vs. Regulatory).
*   **Operations:** Read-only retrieval and persona-based synthesis.

This approach ensures that the system is modular, scalable, and can handle the contrasting needs of simplicity for workers and precision for compliance auditors.
