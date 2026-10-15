# Week 3 Lab Report: Prompting Techniques

- **Student:** omertarikcandirIsu
- **Model:** `llama3.1:8b` via Ollama

This report summarizes four prompting techniques applied to a customer-support assistant. Each starter script was run with its built-in checks.

## Results at a Glance

| Technique | Result |
| --- | --- |
| Few-shot classification | 4/4 cases passed |
| Refund eligibility | 3/3 cases passed |
| Tool calling | Tool call and order ID check passed |
| Retrieval-augmented generation | 3/3 cases passed |

## 1. Few-Shot Classification

**Goal:** Classify a customer message into `billing`, `shipping`, `returns`, `technical`, or `other`.

**Final system prompt:**

```text
Classify each customer message into exactly one category: billing, shipping, returns, technical, or other.

Examples:
Message: My card was charged twice for order 4412.
Label: billing

Message: Where is my package? It has been two weeks.
Label: shipping

Message: I want to send these shoes back for a refund.
Label: returns

Message: The app crashes whenever I open my cart.
Label: technical

Choose the closest category. Use other only when none of the four specific categories fits.
Output only the lowercase category label, with no explanation or punctuation.
```

- **Sample:** `My card was charged twice for order 4412.` -> `billing`
- **Validation:** 4/4 built-in cases passed.
- **What I learned:** Labeled examples communicate both the category boundaries and the expected output format, making the result easier to grade.

## 2. Refund Eligibility

**Goal:** Apply every condition in the refund policy and return a clear `YES` or `NO` decision.

**Final system prompt:**

```text
Evaluate refund eligibility using every rule in the policy below.
Check whether the purchase is within 30 days, the item is unused and in original condition, and the item is not final sale. A refund is eligible only when all conditions pass.
Briefly state the result of each relevant check. End with exactly one final line: DECISION: YES or DECISION: NO. Do not put anything after that final line.
```

- **Sample:** `Bought 10 days ago, unused, not final sale.` -> `YES`
- **Validation:** 3/3 built-in cases passed.
- **What I learned:** Turning a policy into explicit checks helps the model account for multiple conditions; a fixed final line makes the decision straightforward to evaluate.

## 3. Tool Calling

**Goal:** Have the model request an order-status lookup instead of guessing.

**Final system prompt:**

```text
When a customer asks for an order's status, extract the order ID and call get_order_status before replying. Use the returned status in a brief, helpful response. Never invent or assume an order status. If the customer did not provide an order ID, ask them for it instead of calling the tool.
```

**Tool description:** `Look up the current status for a specific order. Use this whenever a customer asks about an order's status; do not guess.`

- **Sample input:** `Hi, can you check on order 4412 for me?`
- **Observed result:** The model called `get_order_status` with `order_id='4412'`; the local function returned `shipped, arriving Friday`.
- **Validation:** The built-in check verified the tool call and order ID.

**Implementation note:** The starter harness executes the local function but does not send its result back to the model for a follow-up response. The observed result is therefore the tool lookup, not a model-generated reply based on the lookup. I left the harness unchanged because the assignment limits edits to the TODO sections.

**What I learned:** A tool schema can guide the model to take the right action, but a complete tool-use workflow must also return the tool result to the model before it can produce a grounded response.

## 4. Retrieval-Augmented Generation

**Goal:** Answer from `data/help_center.txt` and decline questions that the available context cannot answer.

**Final system prompt:**

```text
Answer the customer's question using only the supplied help-center context. Do not add outside facts or guesses. If the context does not contain the answer, politely say exactly: I don't know based on the available information. Keep the answer concise and faithful to the context.
```

**Retriever:** The retriever scores one-line help-center chunks by meaningful word overlap with the question. It ignores common stop words, normalizes a few word variants, and omits chunks with no matching terms.

- **In-scope sample:** `Do you ship internationally?` -> `yes, we offer international shipping to most countries.`
- **Out-of-scope sample:** `What's your CEO's home address?` -> `i don't know based on the available information.`
- **Validation:** 3/3 built-in cases passed.
- **What I learned:** Retrieval provides relevant evidence, but an explicit refusal instruction is still needed when the retrieved context does not contain an answer.

## Closing Reflection

Across the four exercises, I learned that language models handle structured tasks more reliably when the expected labels, decision criteria, available actions, or evidence are made explicit. Examples constrain the output format, policy checks make decisions easier to evaluate, tools provide a way to take actions, and retrieval supplies supporting information. These techniques add useful scaffolding, but the surrounding program still needs to enforce the full interaction contract, as the tool-calling example demonstrated.