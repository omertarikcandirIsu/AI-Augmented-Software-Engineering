# Week 3 Writeup — Prompting Techniques

**Name:** omertarikcandirIsu
**Model:** `llama3.1:8b` via Ollama

## 1. K-shot classification

**Final prompt:**

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

**Sample:** “My card was charged twice for order 4412.” → `billing`
**Check:** 4/4 cases passed.
**What I learned:** A few labeled examples establish both the category boundaries and the exact output format, so the model returns a directly gradable label.

## 2. Refund eligibility

**Final prompt:**

```text
Evaluate refund eligibility using every rule in the policy below.
Check whether the purchase is within 30 days, the item is unused and in original condition, and the item is not final sale. A refund is eligible only when all conditions pass.
Briefly state the result of each relevant check. End with exactly one final line: DECISION: YES or DECISION: NO. Do not put anything after that final line.
```

**Sample:** “Bought 10 days ago, unused, not final sale.” → `YES`
**Check:** 3/3 cases passed.
**What I learned:** Breaking the policy into explicit checks helps the model apply multiple conditions, while a fixed final line makes the decision easy to grade.

## 3. Tool calling

**Final system prompt:**

```text
When a customer asks for an order's status, extract the order ID and call get_order_status before replying. Use the returned status in a brief, helpful response. Never invent or assume an order status. If the customer did not provide an order ID, ask them for it instead of calling the tool.
```

**Tool description:** “Look up the current status for a specific order. Use this whenever a customer asks about an order's status; do not guess.”
**Observed output:** For “Hi, can you check on order 4412 for me?”, the model called the tool with `order_id='4412'`. The starter's Python harness then called the local function and printed `shipped, arriving Friday`; it does not send that result back to the model for a follow-up response.
**Check:** Passed; the built-in check verifies the tool call and order ID, not a model-generated answer using the returned status. The starter only permits edits in TODO sections, so the harness was left unchanged.
**What I learned:** A tool schema can elicit the correct action, but a complete tool-use loop also needs the runtime to return the tool result to the model before expecting a grounded response.

## 4. Retrieval-augmented generation

**Final prompt:**

```text
Answer the customer's question using only the supplied help-center context. Do not add outside facts or guesses. If the context does not contain the answer, politely say exactly: I don't know based on the available information. Keep the answer concise and faithful to the context.
```

**Retriever:** Token overlap over the question and one-line help-center chunks, with common stop words and a few inflection variants normalized. Chunks with no shared meaningful terms are omitted.

**Sample:** “Do you ship internationally?” → “Yes, we offer international shipping to most countries.”
**Out-of-scope sample:** “What's your CEO's home address?” → “I don't know based on the available information.”
**Check:** 3/3 cases passed.
**What I learned:** Retrieval supplies relevant evidence, but an explicit refusal rule is still needed to prevent unsupported answers when retrieval returns no context.

## Closing reflection

Language models are good at these structured tasks when the input, allowed choices, and expected output are made explicit. Examples, a tool schema, and retrieved context each provide a different kind of scaffolding; they constrain format, actions, or evidence. The checks are useful because they reveal when a plausible-sounding answer still fails the required contract.