#!/usr/bin/env python3
"""Test Azure AI Foundry Agent Service connection."""

import os
os.environ["AZURE_FOUNDRY_CONNECTION_STRING"] = ""

# Try multiple connection approaches
print("=== Approach 1: AIProjectClient with connection string ===")
try:
    from azure.ai.projects import AIProjectClient
    from azure.core.credentials import AzureKeyCredential

    # Try with the hub endpoint
    endpoint = "https://cbe-test-hub.services.ai.azure.com"
    api_key = "REDACTED_FOUNDRY_KEY"

    client = AIProjectClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(api_key),
    )
    print(f"  Client created: {client}")

    # Try to list agents
    agents = client.agents.list_agents()
    print(f"  Agents: {agents}")
except Exception as e:
    print(f"  Error: {e}")

print("\n=== Approach 2: Direct REST with API key header ===")
try:
    import urllib.request
    import json

    # Create an agent via REST
    endpoint = "https://cbe-test-hub.services.ai.azure.com/api/projects/cbe-test-project/assistants"
    api_version = "2025-05-15-preview"

    data = json.dumps({
        "model": "gpt-4o",
        "name": "cbe-test-agent",
        "instructions": "You are a test agent.",
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{endpoint}?api-version={api_version}",
        data=data,
        headers={
            "Content-Type": "application/json",
            "api-key": api_key,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        print(f"  Agent created: {json.dumps(result, indent=2)}")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8") if e.fp else ""
    print(f"  HTTP Error {e.code}: {body[:500]}")
except Exception as e:
    print(f"  Error: {e}")

print("\n=== Approach 3: Azure OpenAI Assistants API ===")
try:
    from openai import AzureOpenAI

    # Try via the Azure OpenAI endpoint (assistants API)
    oai_client = AzureOpenAI(
        azure_endpoint="https://posit-mmrwl8q8-eastus2.cognitiveservices.azure.com",
        api_key="REDACTED_AZURE_OPENAI_KEY",
        api_version="2025-01-01-preview",
    )

    # Create assistant
    assistant = oai_client.beta.assistants.create(
        model="gpt-4o",
        name="cbe-test-agent",
        instructions="You are a test agent. Reply with 'hello'.",
    )
    print(f"  Assistant created: {assistant.id}")
    print(f"  Model: {assistant.model}")

    # Create thread
    thread = oai_client.beta.threads.create()
    print(f"  Thread created: {thread.id}")

    # Send message
    message = oai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hello!",
    )
    print(f"  Message sent")

    # Run
    run = oai_client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    print(f"  Run status: {run.status}")

    if run.status == "completed":
        messages = oai_client.beta.threads.messages.list(thread_id=thread.id)
        for m in messages.data:
            if m.role == "assistant":
                print(f"  Response: {m.content[0].text.value}")
                break

    # Cleanup
    oai_client.beta.assistants.delete(assistant.id)
    print(f"  Assistant deleted")

except Exception as e:
    print(f"  Error: {type(e).__name__}: {e}")
