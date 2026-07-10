# WhatsApp B2B Order Flow — Developer Guide
**Version:** 2.1 | **Date:** 2026-06-24 | **Phase:** 1 — Order Flow Only | **Language:** Python (FastAPI)
**Based on:** PM Order Flow Prompt Doc + ConversIQ Proposal

---

## 1. Why We Are Building This

Right now, a salesman must open the B2B Salesman App (React), log in, select a customer, browse the catalog, and place an order manually. This is slow, especially on the field.

**Goal:** Let a salesman (or their customer directly) place an order entirely over WhatsApp — no app login required. They just chat, and the order lands in Magento automatically.

This document covers **Phase 1: Order Flow**. Future phases (voice commerce, image commerce) are outlined at the end but will be planned separately after Phase 1 is confirmed working.

---

## 2. Existing System — What You Need to Know

### 2.1 Backend — Magento 2.3.3 (sauronb2b)

Located at: `/var/www/html/sauronb2b`

The backend is Magento 2.3.3 with custom Hnak modules. Key module for this feature:

**`Hnak/Cashcollection`** — contains all the REST APIs that the salesman app already calls.

Key REST endpoints (all accept admin Bearer token in `Authorization` header):

| Method | URL | Purpose |
|--------|-----|---------|
| POST | `/V1/integration/admin/token` | Login — returns admin Bearer token |
| GET | `/V1/integration/admin/me` | Get logged-in admin info |
| POST | `/V1/integration/admin/customer` | List all customers assigned to this salesman |
| POST | `/V1/integration/admin/custmobile` | Get customer details by customer_id |
| POST | `/V1/integration/admin/setsalsmen` | Set salesman on cart / order |
| POST | `/V1/integration/admin/salsmenorder` | Get salesman's order list |

For placing orders, Magento's standard REST API is used:

| Method | URL | Purpose |
|--------|-----|---------|
| POST | `/V1/customers/{customerId}/carts` | Create cart for customer |
| POST | `/V1/carts/{cartId}/items` | Add product to cart |
| GET | `/V1/products?searchCriteria[...]` | Search products by name/SKU |
| PUT | `/V1/carts/{cartId}/order` | Place order from cart |
| GET | `/V1/customers/{customerId}` | Get customer details + default address |
| POST | `/V1/carts/{cartId}/shipping-information` | Set shipping/billing address |
| GET | `/V1/orders/{orderId}` | Get order details for confirmation |

> **Important:** The salesman app uses an **admin token** (not customer token) to call these APIs on behalf of the customer. The WhatsApp bot must do the same.

### 2.2 Frontend — B2B Salesman App (React)

Located at: `/var/www/html/b2b-salesman-app`

This is a React app. API config is in `/src/api/magento.js`. Environment vars:
- `REACT_APP_SALES_URL` — Magento base URL
- `REACT_APP_PRODUCT_LISTING_TOKEN` — token for product listing
- `REACT_APP_ORACLE_URL` — Oracle/ERP integration URL

The WhatsApp bot **replaces** the need for the salesman to use this app for ordering. The app still exists for other features (cash collection, reports, etc.).

### 2.3 Current Order Flow in the App (For Reference)

```
Salesman logs in -> selects customer -> browses catalog -> adds to cart -> checkout -> order confirmed
```

The WhatsApp bot replicates this same flow, but over chat — faster and with AI intelligence.

---

## 3. What to Build — System Architecture

```
Salesman / Customer (WhatsApp)
         |
         | (WhatsApp message — text)
         v
  WhatsApp Business API (Meta Cloud)
         |
         | (webhook POST)
         v
+--------------------------------------------+
|        WhatsApp Order Middleware            |  <-- NEW SERVICE TO BUILD
|        (Python / FastAPI)                   |
|                                            |
|  +------------------+  +----------------+  |
|  | Webhook Receiver |  | WA Message     |  |
|  | (verify + route) |  | Sender         |  |
|  +--------+---------+  +-------+--------+  |
|           |                     ^           |
|           v                     |           |
|  +--------+---------+           |           |
|  | AI Conversation  |           |           |
|  | Engine           +-----------+           |
|  | (intent + reply) |                       |
|  +--------+---------+                       |
|           |                                 |
|           v                                 |
|  +--------+----------+  +--------------+    |
|  | Session Manager   |  | Conversation |    |
|  | (Redis)           |  | Logger (DB)  |    |
|  +-------------------+  +--------------+    |
|           |                                 |
|           v                                 |
|  +--------+---------+  +--------------+     |
|  | Order Execution  |  | Recommend-   |     |
|  | Layer (Magento)  |  | ation Engine |     |
|  +------------------+  +--------------+     |
+--------------------------------------------+
         |
         | (REST API calls)
         v
   Magento 2.3.3 (sauronb2b)
```

### 3.1 Six Components to Build

| # | Component | Purpose |
|---|-----------|---------|
| 1 | **Webhook Receiver** | Receives incoming WhatsApp messages, verifies Meta signature, routes to conversation engine |
| 2 | **AI Conversation Engine** | Understands intent from salesman's message, manages flow steps, generates reply |
| 3 | **Session Manager** | Stores current step, selected customer, cart, partial inputs per WhatsApp number (Redis) |
| 4 | **Order Execution Layer** | Calls Magento APIs to create cart, add items, set address, place order |
| 5 | **Conversation Logger** | Records every message exchanged — what was said, what was understood, what action was taken. Full audit trail |
| 6 | **Recommendation Engine** | Suggests complementary products based on cart contents and customer's order history |

---

## 4. Data Model

Seven core entities that the system works with. Some exist in Magento already, some are new.

### 4.1 Entities

| Entity | Storage | Description |
|--------|---------|-------------|
| **Customer** | Magento DB (existing) | Name, phone, saved addresses, language preference, shopping history |
| **Conversation** | New DB table | Every WhatsApp exchange — message text, detected intent, action taken, timestamp. Audit trail |
| **Product** | Magento DB (existing) | Complete product catalog — name, SKU, price, stock, category, images |
| **Cart** | Redis (session) + Magento quote | In-progress order. Selected products, quantities, calculated totals |
| **Order** | Magento DB (existing) | Completed purchase — customer, products, total, payment method, status |
| **Payment** | Magento DB (existing) | Payment method, status. Phase 1: credit terms / COD only |
| **Recommendation** | New DB table | Which products were suggested, when, whether acted on — to improve suggestions over time |

### 4.2 Conversation Log Table (New)

```sql
CREATE TABLE whatsapp_conversation_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    wa_number VARCHAR(20) NOT NULL,
    direction ENUM('incoming', 'outgoing') NOT NULL,
    message_text TEXT,
    detected_intent VARCHAR(50),
    action_taken VARCHAR(100),
    session_step VARCHAR(50),
    customer_id INT NULL,
    magento_order_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_wa_number (wa_number),
    INDEX idx_created_at (created_at),
    INDEX idx_customer_id (customer_id)
);
```

### 4.3 Recommendation Log Table (New)

```sql
CREATE TABLE whatsapp_recommendation_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    wa_number VARCHAR(20) NOT NULL,
    customer_id INT NOT NULL,
    recommended_sku VARCHAR(255) NOT NULL,
    recommendation_type ENUM('cross_sell', 'reorder', 'popular', 'category') NOT NULL,
    was_accepted TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customer_id (customer_id),
    INDEX idx_sku (recommended_sku)
);
```

### 4.4 Salesman Mapping Table (New)

```sql
CREATE TABLE whatsapp_salesman_map (
    id INT AUTO_INCREMENT PRIMARY KEY,
    wa_number VARCHAR(20) NOT NULL UNIQUE,
    admin_id INT NOT NULL,
    admin_username VARCHAR(100) NOT NULL,
    language_preference VARCHAR(10) DEFAULT 'en',
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_wa_number (wa_number)
);
```

> **Note:** Admin passwords should NOT be stored in this table. Use a separate secrets/env configuration or encrypted vault.

---

## 5. Salesman Authentication

The salesman must be identified from their WhatsApp number.

### Phase 1 Approach: Pre-mapped phone numbers

Store mapping in `whatsapp_salesman_map` table. When a message arrives from a known number, the middleware auto-authenticates with Magento:

**Login API call:**
```
POST /V1/integration/admin/token
Content-Type: application/json

{
  "username": "salesman01",
  "password": "xxxxx"
}

Response: "eyJhbGciOiJIUzI1NiJ9..."  (Bearer token, valid ~4 hours)
```

Cache the token in Redis session. Re-login automatically when it expires.

**Unknown numbers** get a polite rejection:
> "This number is not registered for ordering. Please contact your manager to get access."

---

## 6. Multi-Language Support

The AI must detect language from the salesman's first message and respond in the same language throughout the session.

**Supported languages (Phase 1):**
- English
- Arabic

**How it works:**
1. First message arrives → AI detects language
2. Language is saved in session (`language: "ar"`)
3. All subsequent replies are in that language
4. If language switches mid-conversation, AI follows the switch

**Implementation:** The AI system prompt includes language detection instructions. For rule-based fallback, use a simple keyword-detection map for common triggers in each language.

---

## 7. Conversation Flow — The 9-Step Journey

This is the core of the system. Each step maps to what the salesman types and how the bot responds.

### Flow Summary

```
01 Salesman sends message
02 AI understands intent
03 AI asks smart questions (one at a time)
04 AI shows matching products
05 AI builds the cart
06 AI suggests recommendations
07 AI confirms delivery details
08 AI processes payment / confirms terms
09 Order confirmed — order ID + ETA sent
```

### Step 1: Salesman Sends First Message

Bot checks if their WhatsApp number is registered. If yes, auto-authenticates and greets.

```
Salesman: "Hi" / "Need to place order" / "اريد طلب"

Bot: "Hi Ahmed! Which customer are you ordering for?
     1. Al Noor Trading
     2. Gulf Supplies LLC
     3. Riyadh Mart
     4. ...
     Reply with a number or type the customer name."
```

**Behind the scenes:**
- Look up WA number in `whatsapp_salesman_map`
- Get/refresh Magento admin token
- Call `POST /V1/integration/admin/customer` with `admin_id` to get customer list
- Detect language, save to session
- Log conversation: direction=incoming, intent=greeting

### Step 2: Customer Selection

```
Salesman: "1"

Bot: "Got it — Al Noor Trading selected.
     What would you like to order?
     Type a product name, SKU, or category."
```

**Behind the scenes:**
- Call `POST /V1/integration/admin/custmobile` to load full customer details
- Save customer's default shipping/billing address to session
- Set session step to `awaiting_product`

### Step 3: Product Search (Smart Questions)

The AI asks clarifying questions **one at a time** — never two questions in one message.

```
Salesman: "mineral water"

Bot: "Which brand do you prefer?
     1. Masafi
     2. Al Ain
     3. Aquafina
     4. Any brand"
```

```
Salesman: "1"

Bot: "Masafi — what size?
     1. 500ml (12 pack)
     2. 500ml (24 pack)
     3. 1.5L (6 pack)
     4. 5 Gallon"
```

**Behind the scenes:**
- Call Magento product search API:
```
GET /V1/products?searchCriteria[filter_groups][0][filters][0][field]=name
    &searchCriteria[filter_groups][0][filters][0][value]=%mineral water%
    &searchCriteria[filter_groups][0][filters][0][condition_type]=like
    &searchCriteria[pageSize]=10
    &fields=items[id,sku,name,price,extension_attributes[stock_item[qty]],custom_attributes]
```
- If multiple brands/variants found, ask to narrow down ONE question at a time
- If search is clear enough (e.g., salesman typed exact SKU), skip clarification and go to quantity

### Step 4: Show Matching Products

After narrowing down, show the specific products with price and stock:

```
Bot: "Here are your options:
     1. Masafi 500ml (12 pack) — AED 18.00 | In Stock
     2. Masafi 500ml (24 pack) — AED 34.00 | In Stock

     Reply with item number to select."
```

**Important rules:**
- Always show as numbered list (so salesman can reply with just a number)
- Show: product name, pack size, unit price, stock status
- Maximum 5 results per message
- If product is **out of stock**, don't hide it — mark it as "Out of Stock" and suggest alternatives (see Section 10)

### Step 5: Quantity + Add to Cart

```
Salesman: "1"

Bot: "Masafi 500ml (12 pack) selected. How many cartons?"

Salesman: "50"

Bot: "Added to cart:
     Masafi 500ml 12pk x 50 = AED 900.00

     Anything else to add? (Type product name, or 'done' to confirm)"
```

**Behind the scenes:**
- Validate quantity > 0
- Check stock availability (`extension_attributes.stock_item.qty`)
- If qty exceeds stock, inform: "Only 30 available. Want to order 30 instead?"
- Add to session cart array
- Set step to `awaiting_product` (loop back for multi-item)

### Step 6: Smart Recommendations

After adding an item, check if there are related products to suggest:

```
Bot: "Added to cart:
     Masafi 500ml 12pk x 50 = AED 900.00

     Customers who order Masafi water also order:
     - Masafi Cups (50 pack) — AED 12.00
     Want to add? Reply YES or type another product."
```

**Recommendation logic (Phase 1 — simple):**
1. **Cross-sell from category:** If product is in "Beverages", suggest top-selling item from same category that's NOT already in cart
2. **Reorder from history:** Check customer's last 5 orders in Magento. If they usually order Product X with Product Y, and X is in cart but Y isn't, suggest Y
3. **Popular items:** If no cross-sell match, suggest top 3 best-sellers

**How to get order history:**
```
GET /V1/orders?searchCriteria[filter_groups][0][filters][0][field]=customer_id
    &searchCriteria[filter_groups][0][filters][0][value]={customerId}
    &searchCriteria[sortOrders][0][field]=created_at
    &searchCriteria[sortOrders][0][direction]=DESC
    &searchCriteria[pageSize]=5
```

Log every recommendation made in `whatsapp_recommendation_log` with `was_accepted` flag.

### Step 7: Multi-Item Cart Building

Bot loops Steps 3–6 until salesman says "done" / "confirm" / "that's all" / "khalas" (خلص).

After each item added, show running cart:
```
Bot: "Current cart for Al Noor Trading:
     1. Masafi 500ml 12pk x 50 = AED 900.00
     2. Pepsi 330ml 24pk x 20 = AED 480.00
     ---
     Total: AED 1,380.00

     Add more or type 'done' to place order."
```

**Cart format rule:** Always show as `[Product Name] x [Qty] = [Price]. Total: [Amount]`

### Step 8: Delivery + Payment Confirmation

When salesman says "done":

```
Bot: "Order Summary for Al Noor Trading:

     1. Masafi 500ml 12pk x 50 = AED 900.00
     2. Pepsi 330ml 24pk x 20 = AED 480.00
     ---
     Total: AED 1,380.00

     Delivery to: Industrial Area 2, Sharjah (saved address)
     Payment: Credit terms (as per account)
     Estimated delivery: 24-48 hours

     Reply YES to confirm or EDIT to modify."
```

**Behind the scenes:**
- Load customer's default address from session (fetched in Step 2)
- Payment method: use customer's default payment method from Magento
- If customer has no saved address, ask for it before confirming

**Edit flow:**
```
Salesman: "EDIT"
Bot: "What would you like to change?
     1. Change quantity of an item
     2. Remove an item
     3. Add more items
     4. Change delivery address"
```

### Step 9: Place Order in Magento + Confirmation

When salesman replies "YES":

1. Create cart: `POST /V1/customers/{customerId}/carts` → get `cartId`
2. Add each item: `POST /V1/carts/{cartId}/items`
3. Set shipping info: `POST /V1/carts/{cartId}/shipping-information`
4. Set salesman: `POST /V1/integration/admin/setsalsmen`
5. Place order: `PUT /V1/carts/{cartId}/order` → get `orderId`

```
Bot: "Order placed successfully!

     Order ID: #100045678
     Customer: Al Noor Trading
     Items: 2 products
     Total: AED 1,380.00
     Delivery: 24-48 hours

     The order is now in Magento and will be processed."
```

**On failure:** If any Magento API call fails, send:
> "Order could not be placed due to a system error. Please try again or use the salesman app. Error: [brief reason]"

---

## 8. AI Conversation Engine

### 8.1 Intent Detection

The AI must understand what the salesman means, not just what they typed. Two approaches:

**Approach A — Rule-based (simpler, faster):**

| Salesman Input | Detected Intent |
|---------------|----------------|
| "hi" / "hello" / "order" / greeting in any language | `greeting` |
| "done" / "confirm" / "that's all" / "khalas" (خلص) | `confirm_cart` |
| "yes" / "na'am" (نعم) / "ok" | `affirm` |
| "no" / "la" (لا) / "cancel" | `deny` / `cancel` |
| A number (1, 2, 3...) | `select_option` |
| "edit" / "change" / "modify" | `edit_cart` |
| "remove [item]" / "delete" | `remove_item` |
| A number + unit ("50 cartons", "100 boxes") | `set_quantity` |
| Any other text | `search_product` |

**Approach B — AI-powered (recommended):**

Use Claude API to understand natural language. The AI handles ambiguous inputs like:
- "same thing but bigger size" → understands context from previous selection
- "actually make that 100" → updates quantity of last added item
- "add the wipes too" → understands from recommendation context

### 8.2 AI System Prompt

```
ROLE
You are a B2B WhatsApp order assistant for Sauron B2B (Hnak).
You help salesmen place orders for their customers via WhatsApp chat.

CONTEXT
You will receive the current session state as JSON (selected customer,
cart contents, current step). Use this context to understand what the
salesman is referring to.

BEHAVIOR
- One question at a time. NEVER ask two things in one message.
- Always present choices as numbered lists (1. 2. 3.) for easy reply.
- Keep replies under 100 words. Break long info into follow-ups.
- Cart format: [Product Name] x [Qty] = [Price]. Total: [Amount]
- Use confirmation emojis ONLY on order success.

LANGUAGE
Detect the salesman's language from their first message.
Support: English, Arabic.
Respond in the same language throughout the session.
If they switch language mid-conversation, follow the switch.

MEMORY
Remember within this session: selected products, quantities, preferred
brand, delivery preference, and payment mode.

LIMITS
- Do NOT discuss pricing policies, discounts, or credit limits unless asked.
- Do NOT make commitments outside the product catalog.
- If the query is outside your scope, reply: "I can help with placing orders.
  For other queries, please contact your manager."

SMART QUESTIONS
When the salesman asks for a product vaguely (e.g., "water"), ask clarifying
questions ONE AT A TIME:
1. First ask brand preference
2. Then ask size/variant
3. Then show matching products
If the request is specific enough, skip clarification.

RECOMMENDATIONS
After adding each item to cart, check if there are related products to suggest.
Only suggest ONE recommendation at a time. Keep it natural:
"Customers who order [X] also order [Y] — want to add?"

OUTPUT FORMAT
Always reply with JSON:
{
  "intent": "greeting|select_option|search_product|set_quantity|confirm_cart|affirm|deny|edit_cart|remove_item|unknown",
  "value": "<extracted value if any>",
  "language": "en|ar",
  "reply": "<message to send to salesman via WhatsApp>"
}
```

---

## 9. Response Format Rules

These rules ensure clean, readable WhatsApp messages:

| Rule | Instruction |
|------|-------------|
| **One question at a time** | Never ask multiple questions in a single message. Wait for the reply before proceeding. |
| **Short replies** | Keep each response under 150 words. Break long info into follow-up messages if needed. |
| **Numbered options** | Always list choices as 1., 2., 3. so salesman can reply with just a number. |
| **Cart summary format** | Show as: `[Product Name] x [Qty] = [Price]`. End with `Total: [Amount]` |
| **Order confirmation** | End with Order ID, Delivery ETA on separate lines. |
| **Escalation trigger** | If salesman uses words like "complaint", "problem", "wrong order" — reply: "Connecting you to support..." and flag for human agent. |

---

## 10. Out of Stock Handling

Before adding to cart, check `extension_attributes.stock_item.qty` from the product search response.

**If qty = 0:**
```
Bot: "Masafi 500ml (12 pack) is currently out of stock.

     Similar available products:
     1. Al Ain 500ml (12 pack) — AED 16.00 | In Stock
     2. Aquafina 500ml (12 pack) — AED 17.00 | In Stock

     Which would you prefer?"
```

**Logic:**
1. Do not add out-of-stock product to cart
2. Search for products in the same category with stock > 0
3. Offer top 2-3 alternatives as numbered list
4. Log the out-of-stock event (useful for inventory analytics)

**If qty < requested amount:**
```
Bot: "Only 30 cartons of Masafi 500ml available (you requested 50).
     Want to order 30 instead? (YES/NO)"
```

---

## 11. Reorder Flow

When a salesman says "same as last time", "repeat order", "reorder", "نفس الطلب السابق" (same as previous order):

1. Fetch customer's last confirmed order from Magento
2. Display it as a summary
3. Ask for confirmation

```
Salesman: "Same as last order for Al Noor"

Bot: "Last order for Al Noor Trading (#100045123, 15 June):
     1. Masafi 500ml 12pk x 50 = AED 900.00
     2. Pepsi 330ml 24pk x 20 = AED 480.00
     Total: AED 1,380.00

     Shall I place the same order? Reply YES to confirm or NO to modify."
```

**API call to get last order:**
```
GET /V1/orders?searchCriteria[filter_groups][0][filters][0][field]=customer_id
    &searchCriteria[filter_groups][0][filters][0][value]={customerId}
    &searchCriteria[sortOrders][0][field]=created_at
    &searchCriteria[sortOrders][0][direction]=DESC
    &searchCriteria[pageSize]=1
```

---

## 12. Session State Structure

Store in Redis (key = `wa_session:{phone_number}`, TTL = 30 minutes):

```json
{
  "wa_number": "+971501234567",
  "admin_id": 75,
  "magento_token": "eyJhbGci...",
  "token_expires_at": "2026-06-24T14:30:00Z",
  "language": "en",
  "step": "awaiting_product",
  "selected_customer": {
    "customer_id": "9990000000003083",
    "name": "Al Noor Trading",
    "magento_id": 1042,
    "default_address": {
      "street": ["Industrial Area 2"],
      "city": "Sharjah",
      "region": "Sharjah",
      "postcode": "00000",
      "country_id": "AE",
      "telephone": "+971501234567"
    }
  },
  "cart": [
    {
      "sku": "MASAFI-500-12PK",
      "name": "Masafi 500ml 12pk",
      "qty": 50,
      "unit_price": 18.00,
      "line_total": 900.00,
      "product_id": 1234,
      "category_id": 15
    }
  ],
  "cart_total": 900.00,
  "last_search_results": [],
  "last_recommendation": null,
  "last_activity": "2026-06-24T13:55:00Z"
}
```

**Step enum:**
```
awaiting_customer -> awaiting_product -> awaiting_brand -> awaiting_variant ->
awaiting_selection -> awaiting_qty -> awaiting_product (loop) -> 
awaiting_confirmation -> order_placed
```

Session expires after **30 minutes** of inactivity. On expiry, salesman needs to start fresh.

---

## 13. Magento API — Order Placement Code

Complete sequence for placing an order programmatically:

```python
import httpx
import os

BASE = os.getenv("MAGENTO_URL")

async def place_order(session: dict, admin_token: str) -> int:
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }
    customer = session["selected_customer"]
    customer_id = customer["magento_id"]
    address = customer["default_address"]
    name_parts = customer["name"].split(" ", 1)
    firstname = name_parts[0]
    lastname = name_parts[1] if len(name_parts) > 1 else "-"

    async with httpx.AsyncClient(timeout=30) as client:
        # Step 1: Create empty cart for customer
        resp = await client.post(f"{BASE}/V1/customers/{customer_id}/carts", headers=headers)
        resp.raise_for_status()
        cart_id = resp.json()

        # Step 2: Add each item to cart
        for item in session["cart"]:
            resp = await client.post(
                f"{BASE}/V1/carts/{cart_id}/items",
                headers=headers,
                json={
                    "cartItem": {
                        "quote_id": cart_id,
                        "sku": item["sku"],
                        "qty": item["qty"],
                    }
                },
            )
            if resp.status_code != 200:
                err = resp.json()
                raise Exception(f"Failed to add {item['sku']}: {err.get('message', 'Unknown error')}")

        # Step 3: Set shipping + billing address
        addr_payload = {
            "region": address["region"],
            "country_id": address["country_id"],
            "street": address["street"],
            "telephone": address["telephone"],
            "postcode": address["postcode"],
            "city": address["city"],
            "firstname": firstname,
            "lastname": lastname,
        }
        await client.post(
            f"{BASE}/V1/carts/{cart_id}/shipping-information",
            headers=headers,
            json={
                "addressInformation": {
                    "shipping_address": addr_payload,
                    "billing_address": addr_payload,
                    "shipping_carrier_code": "freeshipping",
                    "shipping_method_code": "freeshipping",
                }
            },
        )

        # Step 4: Set salesman on order
        await client.post(
            f"{BASE}/V1/integration/admin/setsalsmen",
            headers=headers,
            json={"admin_id": session["admin_id"], "quote_id": cart_id},
        )

        # Step 5: Place order
        resp = await client.put(
            f"{BASE}/V1/carts/{cart_id}/order",
            headers=headers,
            json={"paymentMethod": {"method": "checkmo"}},
        )
        resp.raise_for_status()
        order_id = resp.json()

    return order_id
```

---

## 14. File / Folder Structure

Create a new project separate from the Magento codebase:

```
whatsapp-order-bot/
├── app/
│   ├── main.py                 # Entry point — FastAPI app, mounts routes
│   ├── webhook.py              # WhatsApp webhook receiver + signature verification
│   ├── conversation.py         # Step machine — routes intent to action
│   ├── ai.py                   # Claude API calls for intent parsing + reply generation
│   ├── magento.py              # All Magento REST API calls (httpx async)
│   ├── whatsapp.py             # Send messages via WhatsApp Business API
│   ├── session.py              # Redis session read/write/expire
│   ├── auth.py                 # Salesman WA number -> Magento token mapping
│   ├── recommendation.py       # Cross-sell / reorder suggestion logic
│   ├── logger.py               # Conversation logging to DB
│   └── language.py             # Language detection helpers
├── db/
│   ├── migrations/
│   │   ├── 001_conversation_log.sql
│   │   ├── 002_recommendation_log.sql
│   │   └── 003_salesman_map.sql
│   └── seed/
│       └── salesman_seed.sql   # Initial salesman phone number mappings
├── tests/
│   ├── test_conversation.py    # Test flow step transitions
│   ├── test_magento.py         # Test Magento API calls (mock)
│   └── test_webhook.py         # Test webhook verification
├── .env.example                # Template for environment variables
├── requirements.txt            # Python dependencies
└── README.md
```

---

## 15. Environment Variables

```env
# App
PORT=3000
NODE_ENV=production

# Magento
MAGENTO_URL=https://b2b.yourdomain.com
MAGENTO_ADMIN_TOKEN=           # fallback static token (optional)

# WhatsApp Business API (Meta)
WA_PHONE_NUMBER_ID=1234567890
WA_ACCESS_TOKEN=EAAxxxxxx
WA_VERIFY_TOKEN=my_webhook_secret_token

# Redis
REDIS_URL=redis://127.0.0.1:6379

# Database (for conversation/recommendation logs)
DB_HOST=127.0.0.1
DB_NAME=whatsapp_bot
DB_USER=bot_user
DB_PASS=xxxxx

# AI
ANTHROPIC_API_KEY=sk-ant-xxxx

# Session
SESSION_TTL_SECONDS=1800

# Delivery
DEFAULT_DELIVERY_SLA=24-48 hours
```

### Python Dependencies (`requirements.txt`)

```
fastapi==0.111.0
uvicorn==0.30.1
httpx==0.27.0
redis==5.0.7
anthropic==0.30.0
aiomysql==0.2.0
python-dotenv==1.0.1
pydantic==2.7.4
```

Run with: `uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload`

---

## 16. WhatsApp Business API Setup

### 16.1 Initial Setup
1. Create a Meta Developer account at developers.facebook.com
2. Create a new App → select "Business" type
3. Add WhatsApp product to the app
4. Get a **Phone Number ID** and **Permanent Access Token**
5. Register your **Webhook URL** (e.g., `https://bot.yourdomain.com/webhook`)
6. Subscribe to the `messages` webhook event

### 16.2 Sending a Message
```
POST https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json

{
  "messaging_product": "whatsapp",
  "to": "971501234567",
  "type": "text",
  "text": {
    "body": "Hi Ahmed! Which customer are you ordering for?\n\n1. Al Noor Trading\n2. Gulf Supplies LLC\n3. Riyadh Mart"
  }
}
```

### 16.3 Receiving a Webhook
```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
    "changes": [{
      "value": {
        "messaging_product": "whatsapp",
        "metadata": {
          "display_phone_number": "971XXXXXXXXX",
          "phone_number_id": "PHONE_NUMBER_ID"
        },
        "messages": [{
          "from": "971501234567",
          "id": "wamid.XXXX",
          "timestamp": "1718534400",
          "text": {
            "body": "1"
          },
          "type": "text"
        }]
      },
      "field": "messages"
    }]
  }]
}
```

### 16.4 Webhook Signature Verification
Every incoming webhook has a `X-Hub-Signature-256` header. Verify it:

```python
import hmac
import hashlib

def verify_webhook(body: bytes, signature: str, app_secret: str) -> bool:
    expected = "sha256=" + hmac.new(
        app_secret.encode(), body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

---

## 17. Security Checklist

- [ ] Verify every webhook request using Meta's `X-Hub-Signature-256` header
- [ ] Never store admin passwords in DB — use encrypted env vars or secrets manager
- [ ] Admin token cached in Redis, auto-refresh on expiry (Magento tokens expire in ~4 hours)
- [ ] Rate-limit incoming messages per number (max 10 requests/minute)
- [ ] Log all orders placed with WA number + Magento order ID for audit
- [ ] Sanitize all user input before passing to Magento APIs (prevent injection)
- [ ] HTTPS only for webhook endpoint
- [ ] Redis protected with password and not exposed to public network

---

## 18. Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Webhook Server | Python (FastAPI) | Async-native, fast, auto-docs via Swagger |
| Session Storage | Redis | Fast, supports TTL for auto-expiry |
| AI Engine | Claude API (claude-sonnet-4-6) | Multi-language, good at structured output |
| WhatsApp API | WhatsApp Business Cloud API (Meta) | Official, reliable, free tier available |
| Conversation DB | MySQL (same as Magento DB) | Keeps all data in one place |
| Product Search | Magento REST API (existing) | No new catalog system needed |
| Order Placement | Magento REST API (existing) | Orders go directly into Magento |
| Hosting | Same server or separate VPS | Start on same server, move if traffic grows |

---

## 19. Implementation Roadmap

Phase 1 milestone-based delivery plan:

| Week | Deliverable | Outcome |
|------|-------------|---------|
| **Week 1** | Project setup, WhatsApp Business API connected, webhook receiving messages | Bot can receive and reply to messages |
| **Week 2** | Salesman authentication, customer selection, Magento token management | Salesman identified, customer list loaded |
| **Week 3** | Product search, smart questions, AI conversation engine | Products found and displayed in chat |
| **Week 4** | Cart building, multi-item flow, quantity validation, stock check | Full cart accumulated over conversation |
| **Week 5** | Order placement, address confirmation, Magento order creation | Orders landing in Magento |
| **Week 6** | Recommendation engine, reorder flow, conversation logging | Intelligence layer active |
| **Week 7** | Multi-language testing, error handling, edge cases | English + Arabic working |
| **Week 8** | Load testing, security hardening, production deployment | Live with real salesmen |

**Phase 1 success criteria:**
- Orders placed via WhatsApp appear in Magento within 60 seconds
- Average order time under 90 seconds (vs 8-12 minutes in app)
- Both languages (English + Arabic) working
- Zero data loss (every conversation logged)

---

## 20. Phase 1 Scope — What is IN and OUT

### IN SCOPE (build now)
- Salesman identification by WhatsApp number (pre-mapped)
- Customer selection from salesman's assigned list
- Product search by name, SKU, or category
- Smart clarifying questions (brand, variant, size — one at a time)
- Multi-item cart building with running totals
- Stock validation before adding to cart
- Out-of-stock alternatives
- Basic cross-sell recommendations
- Reorder flow ("same as last time")
- Delivery address confirmation (from saved address)
- Order placement in Magento with salesman attribution
- Multi-language support (English, Arabic)
- Conversation logging (full audit trail)
- Recommendation logging (track acceptance rate)
- Cart editing (change qty, remove item)

### OUT OF SCOPE (Phase 2+)
- Cash collection via WhatsApp
- Credit limit check before ordering
- Voice note ordering (Phase 2)
- Image/photo ordering (Phase 3)
- Customer self-ordering (without salesman)
- OTP-based salesman authentication
- Payment link generation (UPI/card)
- Order status tracking via WhatsApp
- Delivery notifications
- Admin analytics dashboard
- Barcode / receipt scanning

---

## 21. Future Phases Overview

### Phase 2: Voice Commerce (Months 6-9 after Phase 1 launch)
- Salesman sends voice note instead of typing
- Speech-to-text converts to order intent
- Multilingual speech recognition (Arabic, English)
- AI responds with text (or optional voice response)

### Phase 3: Image Commerce (Months 10-14)
- Salesman sends product photo → AI identifies product
- Barcode scanning via camera for instant reorders
- Receipt photo → AI extracts items for reorder

---

## 22. Testing Checklist

Before going live:
- [ ] Webhook receives messages and replies correctly
- [ ] Webhook signature verification blocks invalid requests
- [ ] Salesman number lookup works for registered numbers
- [ ] Unknown number gets polite rejection
- [ ] Customer list loads from Magento for the salesman
- [ ] Product search returns relevant results
- [ ] Smart questions narrow down correctly (brand -> size -> show)
- [ ] Out-of-stock products show alternatives
- [ ] Stock quantity check prevents over-ordering
- [ ] Multi-item cart accumulates correctly
- [ ] Cart edit (change qty, remove item) works
- [ ] Reorder flow retrieves and confirms last order
- [ ] Recommendations appear and log correctly
- [ ] Order is created in Magento with correct customer + salesman + address
- [ ] Order ID is sent back to salesman via WhatsApp
- [ ] Session expires after 30 minutes of inactivity
- [ ] English and Arabic detected and responded correctly
- [ ] Conversation log captures every exchange
- [ ] Error scenarios handled gracefully (API down, invalid input)
- [ ] 10+ concurrent sessions work without conflict

---

## 23. Key Contacts / References

- **Magento codebase:** `/var/www/html/sauronb2b`
- **Salesman app (React):** `/var/www/html/b2b-salesman-app`
- **Existing salesman APIs:** `app/code/Hnak/Cashcollection/etc/webapi.xml`
- **Existing API models:** `app/code/Hnak/Cashcollection/Model/OrecalApi.php`
- **Salesman app API config:** `/var/www/html/b2b-salesman-app/src/api/magento.js`
- **Task folder:** `/var/www/html/sauronb2b/task/`
- **Previous version of this doc:** `task/whatsapp-order-flow.md` (v1)

For any Magento-specific questions, refer to the existing salesman app's API calls in `/var/www/html/b2b-salesman-app/src/` — those show exactly how the existing APIs are used.
