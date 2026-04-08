# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import google.auth
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.db import get_db_connection_string
from app.prompts import WORKER_AGENT_INSTRUCTIONS, COMPLIANCE_AGENT_INSTRUCTIONS, SUPERVISOR_INSTRUCTIONS
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.postgres import PGVectorStore

_, cred_project_id = google.auth.default()
if not os.environ.get("GOOGLE_CLOUD_PROJECT") and cred_project_id:
    os.environ["GOOGLE_CLOUD_PROJECT"] = cred_project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# Initialize Vector Store
connection_string = get_db_connection_string().strip()
async_connection_string = connection_string.replace("postgresql://", "postgresql+asyncpg://")

vector_store = PGVectorStore(
    connection_string=connection_string,
    async_connection_string=async_connection_string,
    table_name="sds_vectors_3072",
    embed_dim=3072,
)

from llama_index.core.base.embeddings.base import BaseEmbedding
from google import genai

class CustomGeminiEmbedding(BaseEmbedding):
    def _get_query_embedding(self, query: str) -> list[float]:
        client = genai.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT"))
        response = client.models.embed_content(
            model="gemini-embedding-001", contents=query
        )
        return response.embeddings[0].values

    def _get_text_embedding(self, text: str) -> list[float]:
        return self._get_query_embedding(text)

    async def _aget_query_embedding(self, query: str) -> list[float]:
        client = genai.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT"))
        response = await client.aio.models.embed_content(
            model="gemini-embedding-001", contents=query
        )
        return response.embeddings[0].values

    async def _aget_text_embedding(self, text: str) -> list[float]:
        return await self._aget_query_embedding(text)

index = VectorStoreIndex.from_vector_store(
    vector_store,
    embed_model=CustomGeminiEmbedding()
)
retriever = index.as_retriever(similarity_top_k=5)

def query_sds(query: str) -> str:
    """Queries the Safety Data Sheets (SDS) vector store for relevant information.
    
    Args:
        query: The search query or question about chemical safety.
        
    Returns:
        The retrieved information or answer from the SDS documents.
    """
    retrieved_nodes = retriever.retrieve(query)
    context = "\n\n".join([node.node.get_content() for node in retrieved_nodes])
    return context

# Define sub-agents
worker_agent = Agent(
    name="workplace_safety_agent",
    instruction=WORKER_AGENT_INSTRUCTIONS,
    description="Specialist for on-site worker safety, protective equipment (PPE), first aid, and emergency response.",
    tools=[query_sds],
    model=Gemini(
        model="gemini-3-flash-preview",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
)

compliance_agent = Agent(
    name="regulatory_advisor_agent",
    instruction=COMPLIANCE_AGENT_INSTRUCTIONS,
    description="Specialist for SDS regulations, legal compliance, hazard classifications, and formal documentation.",
    tools=[query_sds],
    model=Gemini(
        model="gemini-3-flash-preview",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
)

# Define root agent (Supervisor)
root_agent = Agent(
    name="safety_supervisor",
    instruction=SUPERVISOR_INSTRUCTIONS,
    sub_agents=[worker_agent, compliance_agent],
    model=Gemini(
        model="gemini-3-flash-preview",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
)

app = App(
    root_agent=root_agent,
    name="app",
)
