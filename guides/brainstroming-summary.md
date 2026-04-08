# Project Specification: Hazmat Co-Pilot

## Goal
Learn LlamaIndex and its applicability with Google ADK for an AI-Driven Chemical Safety Agent.

## Application Overview (The "Why")
Safety Data Sheets (SDS) are technical, multi-page documents required for every hazardous chemical. While they contain life-saving information, they are often difficult to navigate quickly—especially during emergencies or for non-technical workers on the warehouse floor.

This application aims to transform complex SDS PDFs into actionable intelligence for diverse stakeholders. By combining the data retrieval power of **LlamaIndex** with the advanced reasoning and persona-adaptation capabilities of the **Google ADK (Gemini)**, the system serves both:
- **Operations:** Providing simple, urgent handling and PPE instructions to frontline workers.
- **Compliance:** Providing precise, cited regulatory data to auditors and managers.

## Scope & Scenario
- **Scenario:** Daily Operations (Workplace Safety) combined with Regulatory Compliance.
- **Personas:**
    - **Worker:** Needs simple, actionable PPE and handling instructions.
    - **Compliance Officer:** Needs precise regulatory mapping and audit details.

## MVP Roadmap

### MVP1: Core Personas (Focused Learning)
We will focus on two contrasting personas to test both the simplification and precision capabilities of the system.

1.  **The Frontline Worker ("Keep it Simple")**
    *   **Focus:** Immediate, non-technical instructions for safe handling and PPE.
    *   **Learning Goal:** Test Gemini's ability to summarize dense technical text into simple instructions and LlamaIndex's ability to retrieve specific practical sections (e.g., Section 8).
    *   **Key Guardrail:** Ensure critical warnings are never omitted.

2.  **The Compliance Officer ("Precise & Cited")**
    *   **Focus:** Verify regulatory compliance and storage limits.
    *   **Learning Goal:** Test LlamaIndex's ability to handle complex queries across sections and Gemini's ability to cite sources precisely rather than generalizing.
    *   **Key Guardrail:** Ensure the model admits when it doesn't know rather than hallucinating regulations.

### MVP2: Future Scopes
- **Emergency Responders:** (High stress, extreme low latency, zero tolerance for error).
- **Supply Chain / Researchers:** (Complex multi-document comparison and compound behavior).

## Technical Strategy

### 1. Data Ingestion & Retrieval (LlamaIndex)
- **Section-Aware Chunking:** Parse SDS PDFs based on the 16 standard sections (e.g., Section 8 for PPE, Section 15 for Regulatory).
- **Metadata Tagging:** Enrich chunks with tags like `chemical_id`, `section_id`, `persona_affinity`, etc.
- **Router Query Engine:** Route queries to specific indices or query engines based on the user's role and intent.

### 2. Agent Logic (Google ADK)
- **Persona Management:** Use system prompts to adapt the response tone and depth (simple/bold for workers, detailed/cited for compliance).
- **Function Calling:** Connect to external regulatory APIs for real-time compliance checks if the SDS is out of date.

## Deep Dive: Metadata Strategy

To ensure precise retrieval, we will use LlamaIndex to enrich text chunks with the following metadata schema:

| Metadata Key | Example Value | Purpose |
| :--- | :--- | :--- |
| `chemical_id` | `acetone` | Scopes queries to a specific chemical. |
| `section_id` | `8` | Identifies the SDS section (1-16). |
| `persona_affinity` | `workplace` / `regulatory` | Directs the engine to persona-specific content. |
| `hazard_type` | `flammable`, `corrosive` | Enables emergency or hazard-specific filtering. |
| `information_density` | `high` / `low` | Distinguishes between technical jargon and summaries. |
| `hazard_pictograms` | `["flame", "exclamation_mark"]` | Identifies visual hazard symbols (Extracted via text fallback for MVP1). |

**Usage:**
- **Pre-Filtering:** Filter chunks by `persona_affinity` based on the user's role.
- **Routing:** Direct questions about rules to "Regulatory" chunks and questions about handling to "Workplace" chunks.

*Note on Pictograms for MVP1:* We decided to use **Approach B (Text Fallback)** to extract the names of the pictograms from Section 2 text, rather than complex image extraction.

## Deep Dive: Agent Architecture (Google ADK)

For the interaction layer, we decided to use a **Multi-Agent "Specialist" Team** pattern in the Google ADK.

### Agents
1.  **Workplace Safety Agent:**
    *   *Role:* Safety assistant for frontline workers.
    *   *Tone:* Simple, direct, action-oriented.
    *   *Data Focus:* Section 8 (PPE) and handling procedures.
2.  **Regulatory Advisor Agent:**
    *   *Role:* Compliance advisor for auditors and managers.
    *   *Tone:* Formal, precise, highly cited.
    *   *Data Focus:* Section 15 (Regulatory) and storage rules.

### Workflow
We will use a **Guardrailed Retrieval Workflow**:
1.  **Query:** User role is detected.
2.  **Routing:** Query is sent to the specialist agent corresponding to the role.
3.  **LlamaIndex Call:** Agent queries LlamaIndex with persona-specific filters.
4.  **Synthesis & Guardrail:** Agent formats the answer and applies safety checks before output.

## Deep Dive: System Prompts (Google ADK)

### Agent 1: The Workplace Safety Agent
**System Instructions:**
1.  **Tone:** Direct, helpful, and action-oriented. Use simple, non-technical language.
2.  **Formatting:** Use bullet points for instructions. Avoid long paragraphs.
3.  **Content Focus:** Prioritize Personal Protective Equipment (PPE), first aid, and immediate safe handling procedures.
4.  **Translation:** Translate technical jargon into specific instructions (e.g., "impermeable gloves" -> "Nitrile gloves" if known).
5.  **Safety Rule:** Never omit or trivialize a lethal or severe hazard. Bold these warnings.
6.  **Pictograms:** List relevant Hazard Pictograms at the start (e.g., `[FLAME]`).

### Agent 2: The Regulatory Advisor Agent
**System Instructions:**
1.  **Tone:** Formal, precise, and objective. Do not simplify or summarize away technical details.
2.  **Formatting:** Use a report style. Cite sources for every claim.
3.  **Content Focus:** Prioritize regulatory classifications, exposure limits, and disposal rules.
4.  **Citation Rule:** You MUST cite the specific section of the SDS (e.g., *"According to Section 15..."*).
5.  **Honesty Rule:** If the specific answer is not in the text, state: *"This specific information is not available in the provided document sections."*

## Example Interactions

### Example 1: The Worker Scenario
*   **User:** Worker
*   **Query:** *"I need to clean up a small spill of Acetone. What gloves do I need?"*
*   **Agent Output:**
    > `[FLAME]` `[EXCLAMATION MARK]`
    >
    > Here is what you need to do:
    > - Use **Butyl Rubber** gloves. Do not use standard latex gloves.
    > - Work in a well-ventilated area or open a window.
    > - **Acetone is highly flammable.** Keep away from open flames or sparks.

### Example 2: The Compliance Scenario
*   **User:** Compliance Officer
*   **Query:** *"What are the OSHA exposure limits for Acetone, and are there any specific reporting requirements for a spill?"*
*   **Agent Output:**
    > **Regulatory Assessment for Acetone**
    >
    > **Exposure Limits:**
    > According to Section 8, the OSHA PEL (Permissible Exposure Limit) is 1000 ppm (2400 mg/m3) as an 8-hour TWA.
    >
    > **Spill Reporting:**
    > According to Section 15, this material contains no chemicals subject to the reporting requirements of SARA Title III, Section 302. However, local regulations may apply.

## Architecture Decisions (Scale & GCP Deployment)

### 1. Indexing Strategy: Vector Store Index (Primary)
- **Decision:** Use a **Vector Store Index** as the primary search mechanism, supported by a **Document Summary Index**.

### 2. Database: PostgreSQL with `pgvector` (Cloud SQL or AlloyDB)
- **Decision:** Use **Cloud SQL for PostgreSQL** (or AlloyDB) with the `pgvector` extension.

### 3. Embeddings: `gemini-embedding-001`
- **Decision:** Use **`gemini-embedding-001`** for generating text embeddings.

## Evaluation & Tracing (Observability)

To ensure the system produces accurate, safe, and persona-appropriate responses, we will implement the following strategies:

### 1. Evaluation: Google ADK `AgentEvaluator`
- **Decision:** Use the **AgentEvaluator** from the Google ADK.
- **Purpose:** To score and validate that agents adhere to their personas and produce accurate summaries without adding hallucinations.

### 2. Tracing: Arize AI (Phoenix)
- **Decision:** Use **Arize AI** for tracing both LlamaIndex and Google ADK.
- **Purpose:** To monitor retrieval quality and agent reasoning execution.
- **Reference Links:**
    - [Arize LlamaIndex Tracing](https://arize.com/docs/phoenix/integrations/python/llamaindex/llamaindex-tracing)
    - [Arize Google ADK Tracing](https://arize.com/docs/phoenix/integrations/python/google-adk/google-adk-tracing)

## Next Steps
- Analyze the structure of the sample SDS files (`Acetone.pdf`, `AR-13324 hydrochloride.pdf`).
- Set up a basic LlamaIndex pipeline to parse these files.
