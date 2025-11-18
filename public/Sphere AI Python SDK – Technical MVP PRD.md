# **Sphere AI Python SDK – Technical MVP PRD**

Version: 1.0 (Final Engineering Scope)  
Status: Ready for Development  
Focus: LLM Interception, Agentic Security, Governance as Code

## **1\. Overview & Core Philosophy**

**Sphere AI** is a lightweight Python SDK designed to intercept, inspect, and govern interactions between developers and Large Language Models (LLMs).

Unlike generic policy engines, Sphere is **opinionated about AI Security**. It specifically targets the **OpenAI API standard** to solve two critical problems:

1. **Agentic Security:** Preventing AI agents from executing dangerous tools (e.g., delete\_database) by inspecting the tool\_calls JSON payload.  
2. **Automated Compliance:** generating structured audit logs tagged with ISO 42001 controls automatically.

**Architecture Strategy:**

* **Client-Side Interceptor:** Wraps the openai client locally.  
* **Governance as Code:** Policies are defined in sphere.yaml (Git-controlled).  
* **No-SaaS Dependency:** No external API calls for decision making. Zero latency penalty from network hops.

## **2\. User Stories (The "GitOps" Workflow)**

### **Story 1: The Frictionless Wrap (Developer)**

* **As a** Python Developer,  
* **I want to** integrate Sphere by wrapping my existing OpenAI client with SphereClient(base\_client),  
* **So that** I don't have to rewrite my entire application logic or manually decorate every function.

### **Story 2: Blocking Dangerous Tools (Security Engineer)**

* **As a** Security Engineer,  
* **I want to** define a "Block List" of sensitive tool names (e.g., drop\_table, send\_email) in a sphere.yaml file,  
* **So that** if an LLM tries to call these tools, the SDK intercepts the JSON response and raises a PolicyViolationError *before* the code executes.

### **Story 3: One-Click Audit (GRC Lead)**

* **As a** Compliance Officer,  
* **I want** the SDK to output logs to stdout in NDJSON format with a specific field compliance\_tag="ISO\_42001\_A.7",  
* **So that** I can ingest them into Splunk and prove we are monitoring AI usage without manual tagging.

## **3\. Functional Requirements & Logic**

### **3.1 Core Architecture: The OpenAI Interceptor**

**Requirement:** Implement a Proxy/Wrapper pattern around the standard openai.OpenAI client.

**Technical Spec:**

* The SDK must expose a class SphereClient.  
* It must intercept the .chat.completions.create() method.  
* It must allow streaming responses (handle stream=True by inspecting chunks or enforcing pre-flight only).

**Pseudo-Code Reference:**

\# sphere/wrappers/openai.py

class SphereClient:  
    def \_\_init\_\_(self, client, policy\_path="sphere.yaml"):  
        self.\_client \= client  
        self.engine \= PolicyEngine(policy\_path)

    def create(self, \*\*kwargs):  
        \# 1\. Pre-Flight: Scan Prompts  
        self.engine.validate\_input(kwargs.get('messages'))  
          
        \# 2\. Execution: Call LLM  
        response \= self.\_client.chat.completions.create(\*\*kwargs)  
          
        \# 3\. Post-Flight: Agentic Security Check  
        self.engine.validate\_tool\_calls(response)  
          
        \# 4\. Logging  
        self.logger.emit(kwargs, response)  
          
        return response

### **3.2 Policy Engine: Agentic Security Logic**

**Requirement:** The engine must parse the specific JSON structure of OpenAI Tool Calls.

**Technical Spec:**

* **Input:** The response object from OpenAI.  
* **Logic:** Iterate through response.choices\[0\].message.tool\_calls.  
* **Validation:** Check if function.name exists in the blocked\_tools list defined in sphere.yaml.  
* **Action:** If blocked, raise SphereSecurityException or overwrite the response message to "Tool execution denied by policy".

### **3.3 Governance as Code: YAML Schema**

**Requirement:** A strict schema for local policy definition.

**Schema Definition (sphere.yaml):**

version: "1.0"  
compliance\_standard: "ISO\_42001"

security\_rules:  
  \# Rule 1: Tool Blocking (Agentic)  
  \- id: "block\_destructive\_tools"  
    type: "tool\_filter"  
    action: "block"  
    blocked\_tools: \["delete\_user", "drop\_db", "execute\_shell"\]  
    compliance\_tag: "ISO\_42001\_A.9.4"

  \# Rule 2: PII Protection (Text)  
  \- id: "mask\_credit\_cards"  
    type: "regex\_mask"  
    pattern: "\\\\b(?:\\\\d\[ \-\]\*?){13,16}\\\\b"  
    action: "redact"  
    compliance\_tag: "GDPR\_Art\_32"

### **3.4 Audit Logging: Structured Output**

**Requirement:** Emit logs to Standard Output (stdout) in NDJSON format.

**JSON Log Structure:**

{  
  "timestamp": "2025-11-18T10:00:00Z",  
  "level": "AUDIT",  
  "source": "sphere\_sdk",  
  "model": "gpt-4-turbo",  
  "interaction\_id": "req\_123abc",  
  "policy\_decision": "BLOCKED",  
  "violation": {  
    "rule\_id": "block\_destructive\_tools",  
    "trigger": "delete\_user",  
    "type": "tool\_call"  
  },  
  "compliance": {  
    "standard": "ISO\_42001",  
    "control\_id": "A.9.4"  
  },  
  "cost\_metric": {  
    "prompt\_tokens": 50,  
    "completion\_tokens": 10  
  }  
}

## **4\. "Marketplace" Implementation (The Library Approach)**

**Requirement:** Do not build an API. Build a Python Module.

* **Implementation:** Pre-packaged policies should be shippable as a Python package.  
* **Usage:**  
  from sphere.policies import hipaa\_pack, owasp\_top\_10

  \# Load into the client  
  client \= SphereClient(openai\_client, policies=\[hipaa\_pack, owasp\_top\_10\])

* **Deliverable:** A folder sphere/policies/ containing curated YAMLs or Python Dicts.

## **5\. Success Metrics (Technical MVP)**

1. **Integration Time:** Developer can wrap a client and block a tool in **\< 5 minutes**.  
2. **Latency Budget:** The overhead of the SphereClient logic (Pre/Post checks) must be **\< 20ms** (excluding LLM inference time).  
3. **Accuracy:** 100% success rate in blocking a simulated tool\_call named "delete\_db" in unit tests.  
4. **Standards:** The output log must pass a JSON Linter and contain the compliance\_tag.

## **6\. Milestones (3 Weeks)**

* **Week 1:** **The Interceptor.** Build SphereClient wrapper for OpenAI. Get "Hello World" working (Pass-through).  
* **Week 2:** **The Brain.** Implement PolicyEngine to parse YAML and block specific tool\_calls (Agentic Security).  
* **Week 3:** **The Logger & Polish.** Implement the NDJSON logger with ISO tags and ship the pip package.