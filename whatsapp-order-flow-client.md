# WhatsApp B2B Ordering System
### Client Overview Document
**Version:** 1.0 | **Date:** 2026-06-24 | **Phase 1:** Order Flow

---

## 1. What Is This?

A WhatsApp-based ordering system that lets your **salesmen place orders for customers directly through WhatsApp** — no app login needed. The salesman simply chats, and the order is automatically created in your system.

**Before (Current):**
The salesman opens an app, logs in, searches for the customer, browses the catalog, adds items, and checks out. This takes **8-12 minutes per order**.

**After (With WhatsApp Bot):**
The salesman sends a WhatsApp message, selects the customer, tells the bot what to order, confirms, and done. This takes **60-90 seconds per order**.

---

## 2. How It Works — High Level

```
+------------------+          +------------------+          +------------------+
|                  |  message  |                  |   data    |                  |
|    Salesman      +---------->   WhatsApp Bot    +---------->   Your Backend   |
|   (WhatsApp)     |<----------+  (AI Assistant)  |<----------+   (Magento)     |
|                  |   reply   |                  |  response |                  |
+------------------+          +------------------+          +------------------+
```

**In simple terms:**
1. Salesman sends a WhatsApp message
2. Our AI bot understands what they need
3. Bot talks to your Magento system to find products, check stock, and place orders
4. Bot replies back to the salesman with results
5. Order appears in your Magento admin panel automatically

---

## 3. The Complete Order Flow

### Flow Diagram

```
    SALESMAN                         BOT                           MAGENTO
       |                              |                              |
       |   "Hi" / "Need to order"     |                              |
       +----------------------------->|                              |
       |                              |   Verify salesman number     |
       |                              +----------------------------->|
       |                              |   Load customer list         |
       |   "Which customer?"          |<-----------------------------+
       |<-----------------------------+                              |
       |                              |                              |
       |   "Al Noor Trading"          |                              |
       +----------------------------->|                              |
       |                              |   Load customer details      |
       |                              +----------------------------->|
       |   "What to order?"           |<-----------------------------+
       |<-----------------------------+                              |
       |                              |                              |
       |   "mineral water"            |                              |
       +----------------------------->|                              |
       |                              |   Search products            |
       |   "Which brand?"             |<-----------------------------+
       |<-----------------------------+                              |
       |                              |                              |
       |   "Masafi"                   |                              |
       +----------------------------->|                              |
       |                              |   Filter by brand            |
       |   "Which size?"              |<-----------------------------+
       |<-----------------------------+                              |
       |                              |                              |
       |   "500ml"                    |                              |
       +----------------------------->|                              |
       |   "Here are options:         |                              |
       |    1. Masafi 500ml 12pk      |                              |
       |    2. Masafi 500ml 24pk"     |                              |
       |<-----------------------------+                              |
       |                              |                              |
       |   "1"                        |                              |
       +----------------------------->|                              |
       |   "How many cartons?"        |                              |
       |<-----------------------------+                              |
       |                              |                              |
       |   "50"                       |                              |
       +----------------------------->|                              |
       |                              |   Check stock                |
       |   "Added! 50 x AED 18       |<-----------------------------+
       |    = AED 900.                |                              |
       |    Also popular: Masafi Cups |                              |
       |    Want to add?"             |                              |
       |<-----------------------------+                              |
       |                              |                              |
       |   "No. Done"                 |                              |
       +----------------------------->|                              |
       |   "Order Summary:            |                              |
       |    Masafi 500ml x 50         |                              |
       |    = AED 900                 |                              |
       |    Delivery: 24-48 hrs       |                              |
       |    Confirm? YES/NO"          |                              |
       |<-----------------------------+                              |
       |                              |                              |
       |   "YES"                      |                              |
       +----------------------------->|                              |
       |                              |   Create cart                |
       |                              +----------------------------->|
       |                              |   Add items                  |
       |                              +----------------------------->|
       |                              |   Set address                |
       |                              +----------------------------->|
       |                              |   Place order                |
       |                              +----------------------------->|
       |                              |   Order #100045678           |
       |   "Order placed!             |<-----------------------------+
       |    Order #100045678          |                              |
       |    Total: AED 900"           |                              |
       |<-----------------------------+                              |
       |                              |                              |
```

---

## 4. The 9 Steps — Explained

### Step-by-Step Breakdown

```
+--------+     +--------+     +--------+     +--------+     +--------+
| STEP 1 |---->| STEP 2 |---->| STEP 3 |---->| STEP 4 |---->| STEP 5 |
| Message|     |Identify|     | Smart  |     | Show   |     | Add to |
| Sent   |     |Customer|     |Question|     |Products|     | Cart   |
+--------+     +--------+     +--------+     +--------+     +--------+
                                                                 |
+--------+     +--------+     +--------+     +--------+          |
| STEP 9 |<----| STEP 8 |<----| STEP 7 |<----| STEP 6 |<--------+
| Order  |     |Confirm |     |Delivery|     |Suggest |
| Done!  |     | Order  |     |Details |     |More    |
+--------+     +--------+     +--------+     +--------+
```

| Step | What Happens | Who Does It |
|------|-------------|-------------|
| **1. Message Sent** | Salesman sends any message to the bot's WhatsApp number | Salesman |
| **2. Identify Customer** | Bot shows list of salesman's assigned customers. Salesman picks one by number | Bot + Salesman |
| **3. Smart Questions** | Salesman types what they want ("water"). Bot asks one question at a time — brand? size? | Bot |
| **4. Show Products** | Bot shows matching products with price and stock status as numbered list | Bot |
| **5. Add to Cart** | Salesman picks a product and enters quantity. Bot adds it and shows running total | Salesman + Bot |
| **6. Suggest More** | Bot recommends related products ("Customers also buy..."). Salesman can add or skip | Bot |
| **7. Delivery Details** | Bot confirms the saved delivery address and estimated delivery time | Bot |
| **8. Confirm Order** | Bot shows full order summary. Salesman replies YES to confirm or EDIT to change | Salesman |
| **9. Order Placed** | Order is created in Magento. Bot sends Order ID and confirmation | Bot + Magento |

---

## 5. Real Conversation Example

### Example 1: Standard Order (English)

```
Salesman: Hi

Bot:      Hi Ahmed! Which customer are you ordering for?
          1. Al Noor Trading
          2. Gulf Supplies LLC
          3. Riyadh Mart
          Reply with a number or customer name.

Salesman: 1

Bot:      Al Noor Trading selected.
          What would you like to order?

Salesman: mineral water

Bot:      Which brand do you prefer?
          1. Masafi
          2. Al Ain
          3. Aquafina
          4. Any brand

Salesman: 1

Bot:      Masafi — what size?
          1. 500ml (12 pack) — AED 18.00
          2. 500ml (24 pack) — AED 34.00
          3. 1.5L (6 pack) — AED 22.00

Salesman: 1

Bot:      How many cartons?

Salesman: 50

Bot:      Added to cart:
          Masafi 500ml 12pk x 50 = AED 900.00

          Customers who order Masafi water also order:
          Masafi Cups (50 pack) — AED 12.00
          Want to add? Or type another product, or 'done'.

Salesman: done

Bot:      Order Summary for Al Noor Trading:

          1. Masafi 500ml 12pk x 50 = AED 900.00
          ---
          Total: AED 900.00

          Delivery to: Industrial Area 2, Sharjah
          Payment: Credit terms
          Delivery: 24-48 hours

          Reply YES to confirm or EDIT to modify.

Salesman: YES

Bot:      Order placed successfully!
          Order ID: #100045678
          Customer: Al Noor Trading
          Total: AED 900.00
          The order is now in Magento and will be processed.
```

### Example 2: Standard Order (Arabic)

```
Salesman: مرحبا

Bot:      مرحبا احمد! لأي عميل تريد الطلب؟
          ١. النور للتجارة
          ٢. مؤسسة الخليج للتوريدات
          ٣. سوق الرياض
          أرسل رقم العميل أو اسمه.

Salesman: ١

Bot:      تم اختيار النور للتجارة.
          ماذا تريد أن تطلب؟

Salesman: مياه معدنية

Bot:      أي ماركة تفضل؟
          ١. مسافي
          ٢. العين
          ٣. أكوافينا

Salesman: ١

Bot:      مسافي — أي حجم؟
          ١. ٥٠٠ مل (١٢ عبوة) — ١٨ درهم
          ٢. ٥٠٠ مل (٢٤ عبوة) — ٣٤ درهم
          ٣. ١.٥ لتر (٦ عبوات) — ٢٢ درهم

Salesman: ١

Bot:      كم كرتون؟

Salesman: ٥٠

Bot:      تمت الإضافة:
          مسافي ٥٠٠ مل ١٢ عبوة × ٥٠ = ٩٠٠ درهم

          أي شيء آخر؟ اكتب اسم المنتج أو 'خلص' للتأكيد.

Salesman: خلص

Bot:      ملخص الطلب — النور للتجارة:

          ١. مسافي ٥٠٠ مل × ٥٠ = ٩٠٠ درهم
          ---
          المجموع: ٩٠٠ درهم

          التوصيل إلى: المنطقة الصناعية ٢، الشارقة
          الدفع: حسب شروط الائتمان
          التوصيل: ٢٤-٤٨ ساعة

          أرسل نعم للتأكيد أو تعديل للتغيير.

Salesman: نعم

Bot:      تم الطلب بنجاح!
          رقم الطلب: #١٠٠٠٤٥٦٧٨
          العميل: النور للتجارة
          المجموع: ٩٠٠ درهم
          الطلب الآن في النظام وسيتم معالجته.
```

---

## 6. Special Features

### 6.1 Smart Recommendations

The bot doesn't just take orders — it suggests products the customer might need.

```
How Recommendations Work:

+-------------------+     +------------------------+     +------------------+
| Salesman adds     |     | Bot checks:            |     | Bot suggests:    |
| "Masafi Water"    +---->| - What do similar      +---->| "Customers also  |
| to cart           |     |   customers buy?        |     |  buy Masafi Cups" |
|                   |     | - What did this         |     |                  |
|                   |     |   customer order before? |     |                  |
+-------------------+     +------------------------+     +------------------+
```

**Result:** Higher average order value without the salesman needing to remember product combinations.

### 6.2 Reorder ("Same as Last Time")

Salesmen can instantly repeat a previous order:

```
Salesman: Same as last order for Al Noor

Bot:      Last order for Al Noor Trading (#100045123, 15 June):
          1. Masafi 500ml 12pk x 50 = AED 900.00
          2. Pepsi 330ml 24pk x 20 = AED 480.00
          Total: AED 1,380.00

          Shall I place the same order? YES to confirm, NO to modify.

Salesman: YES

Bot:      Order placed! Order #100045679
```

**Result:** Repeat orders in under 30 seconds.

### 6.3 Out of Stock Handling

If a product is unavailable, the bot automatically suggests alternatives:

```
Salesman: Masafi 500ml

Bot:      Masafi 500ml (12 pack) is currently out of stock.

          Similar available products:
          1. Al Ain 500ml (12 pack) — AED 16.00
          2. Aquafina 500ml (12 pack) — AED 17.00

          Which would you prefer?
```

**Result:** No lost sales due to stock issues.

### 6.4 Cart Editing

The salesman can modify their order before confirming:

```
Salesman: EDIT

Bot:      What would you like to change?
          1. Change quantity of an item
          2. Remove an item
          3. Add more items
          4. Change delivery address
```

### 6.5 Multi-Language

The bot automatically detects whether the salesman is writing in **English** or **Arabic** and responds in the same language. No setup needed — it just works.

---

## 7. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        YOUR INFRASTRUCTURE                              │
│                                                                         │
│  ┌──────────────┐     ┌──────────────────────────────────────────────┐  │
│  │              │     │         WhatsApp Order Bot                    │  │
│  │   Magento    │     │                                              │  │
│  │   2.3.3      │     │  ┌────────────┐    ┌─────────────────────┐   │  │
│  │              │     │  │  WhatsApp   │    │  AI Conversation    │   │  │
│  │  - Products  │◄────┤  │  Webhook    │───►│  Engine             │   │  │
│  │  - Customers │     │  │  Receiver   │    │  (understands       │   │  │
│  │  - Orders    │     │  └────────────┘    │   intent, generates │   │  │
│  │  - Stock     │     │                    │   replies)           │   │  │
│  │  - Addresses │     │                    └──────────┬──────────┘   │  │
│  │              │────►│                               │              │  │
│  └──────────────┘     │  ┌────────────┐    ┌──────────▼──────────┐   │  │
│                       │  │   Redis    │    │  Recommendation     │   │  │
│                       │  │  (Session  │    │  Engine             │   │  │
│                       │  │   State)   │    │  (suggests related  │   │  │
│                       │  └────────────┘    │   products)         │   │  │
│                       │                    └─────────────────────┘   │  │
│                       │  ┌────────────────────────────────────────┐  │  │
│                       │  │  Conversation Logger (audit trail)     │  │  │
│                       │  └────────────────────────────────────────┘  │  │
│                       └──────────────────────────────────────────────┘  │
│                                      ▲                                  │
└──────────────────────────────────────┼──────────────────────────────────┘
                                       │
                              ┌────────┴────────┐
                              │   WhatsApp       │
                              │   Business API   │
                              │   (Meta Cloud)   │
                              └────────┬────────┘
                                       │
                              ┌────────┴────────┐
                              │   Salesman's     │
                              │   WhatsApp       │
                              │   (Phone)        │
                              └─────────────────┘
```

---

## 8. What Data Is Tracked

Every interaction is logged for transparency and analytics:

```
┌──────────────────────────────────────────────────────────────────────┐
│                         DATA TRACKED                                  │
│                                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │
│  │ Conversation│  │   Orders    │  │Recommenda-  │  │  Customer  │  │
│  │    Logs     │  │   Placed    │  │   tions     │  │  Profiles  │  │
│  │             │  │             │  │             │  │            │  │
│  │ - Who said  │  │ - Order ID  │  │ - What was  │  │ - Name     │  │
│  │   what      │  │ - Items     │  │   suggested │  │ - Address  │  │
│  │ - When      │  │ - Total     │  │ - Was it    │  │ - Language │  │
│  │ - Intent    │  │ - Customer  │  │   accepted? │  │ - History  │  │
│  │   detected  │  │ - Salesman  │  │ - Improves  │  │            │  │
│  │ - Action    │  │ - Status    │  │   over time │  │            │  │
│  │   taken     │  │             │  │             │  │            │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │
│                                                                       │
│  This data enables:                                                   │
│  - Full audit trail of every order placed via WhatsApp                │
│  - Track which recommendations increase order value                   │
│  - Identify most active salesmen and customers                        │
│  - Measure time-to-order improvements                                 │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 9. Security & Access Control

```
┌─────────────────────────────────────────────────────────┐
│                   SECURITY LAYERS                        │
│                                                          │
│  Layer 1: SALESMAN VERIFICATION                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Only pre-registered WhatsApp numbers can use the   │  │
│  │ bot. Unknown numbers are blocked automatically.    │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  Layer 2: CUSTOMER SCOPE                                 │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Each salesman can ONLY see and order for their     │  │
│  │ assigned customers. No cross-access possible.      │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  Layer 3: ENCRYPTED COMMUNICATION                        │
│  ┌────────────────────────────────────────────────────┐  │
│  │ WhatsApp messages are end-to-end encrypted.        │  │
│  │ All API calls use HTTPS + secure tokens.           │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  Layer 4: AUDIT TRAIL                                    │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Every message, every order, every action is        │  │
│  │ logged with timestamps. Full traceability.         │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  Layer 5: RATE LIMITING                                  │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Maximum 10 messages per minute per number.         │  │
│  │ Prevents abuse and system overload.                │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 10. Before vs After — Business Impact

```
┌──────────────────────────┬────────────────┬────────────────┐
│      Metric              │    Before      │     After      │
│                          │   (App-based)  │  (WhatsApp)    │
├──────────────────────────┼────────────────┼────────────────┤
│ Time to place order      │  8-12 minutes  │  60-90 seconds │
├──────────────────────────┼────────────────┼────────────────┤
│ App login required       │     Yes        │      No        │
├──────────────────────────┼────────────────┼────────────────┤
│ Internet quality needed  │   Good (app)   │  Basic (chat)  │
├──────────────────────────┼────────────────┼────────────────┤
│ Repeat order time        │  5-8 minutes   │  Under 30 sec  │
├──────────────────────────┼────────────────┼────────────────┤
│ Product recommendations  │     None       │   Automatic    │
├──────────────────────────┼────────────────┼────────────────┤
│ Language support          │  English only  │ English+Arabic │
├──────────────────────────┼────────────────┼────────────────┤
│ Out-of-stock handling    │  Manual search │  Auto-suggest  │
├──────────────────────────┼────────────────┼────────────────┤
│ Order audit trail        │   Basic logs   │ Full chat log  │
├──────────────────────────┼────────────────┼────────────────┤
│ Training needed          │   App training │  Zero (chat)   │
└──────────────────────────┴────────────────┴────────────────┘
```

---

## 11. Implementation Timeline

```
Week 1-2          Week 3-4          Week 5-6          Week 7-8
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  SETUP   │     │  SEARCH  │     │  ORDER   │     │  POLISH  │
│          │     │          │     │          │     │          │
│ WhatsApp │     │ Product  │     │ Cart +   │     │ Testing  │
│ connected│────►│ search   │────►│ Order    │────►│ Security │
│ Auth     │     │ Smart Q  │     │ placement│     │ Launch   │
│ working  │     │ working  │     │ working  │     │ ready    │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

| Week | What Gets Done | You Can See |
|------|---------------|-------------|
| **1-2** | WhatsApp connected, salesman authentication, customer selection | Bot responds to messages, shows customer list |
| **3-4** | Product search, smart questions, AI engine | Products found via chat with brand/size filtering |
| **5-6** | Cart building, order placement, recommendations | Real orders appearing in Magento via WhatsApp |
| **7-8** | Multi-language, error handling, security, testing | Production-ready system for real salesmen |

---

## 12. Phase 1 Scope

### What Is Included (Phase 1)

| Feature | Status |
|---------|--------|
| Salesman identification by WhatsApp number | Included |
| Customer selection from assigned list | Included |
| Product search by name, SKU, or category | Included |
| Smart clarifying questions (brand, size) | Included |
| Multi-item cart with running totals | Included |
| Stock check before adding to cart | Included |
| Out-of-stock alternatives | Included |
| Product recommendations (cross-sell) | Included |
| Reorder previous orders | Included |
| Delivery address from saved address | Included |
| Order placement in Magento | Included |
| English + Arabic language support | Included |
| Full conversation audit trail | Included |
| Cart editing (change qty, remove item) | Included |

### What Comes Later (Phase 2+)

| Feature | Phase |
|---------|-------|
| Voice note ordering (speak to order) | Phase 2 |
| Photo/image ordering (send product photo) | Phase 3 |
| Cash collection via WhatsApp | Phase 2 |
| Credit limit check before ordering | Phase 2 |
| Payment link (UPI/card) in chat | Phase 2 |
| Order status tracking via WhatsApp | Phase 2 |
| Delivery notifications | Phase 2 |
| Customer self-ordering (without salesman) | Phase 2 |
| Admin analytics dashboard | Phase 2 |

---

## 13. Future Vision

```
     2026 NOW                2026 Q3                2026 Q4               2027+
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│                 │   │                 │   │                 │   │                 │
│   TEXT ORDER    │   │  VOICE ORDER    │   │  IMAGE ORDER    │   │  PREDICTIVE     │
│                 │   │                 │   │                 │   │                 │
│  Salesman types │   │ Salesman sends  │   │ Salesman sends  │   │ Bot proactively │
│  what to order  │──►│ voice note to   │──►│ product photo   │──►│ suggests orders │
│  via WhatsApp   │   │ place order     │   │ to reorder      │   │ based on pattern│
│                 │   │                 │   │                 │   │                 │
│  Phase 1        │   │  Phase 2        │   │  Phase 3        │   │  Phase 4        │
└─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘
```

---

## 14. Key Numbers

| Metric | Target |
|--------|--------|
| Average order time | Under 90 seconds |
| Order placed in Magento | Within 60 seconds of confirmation |
| Supported languages | English + Arabic |
| Uptime target | 99.5% |
| Session timeout | 30 minutes inactive |
| Max concurrent salesmen | Unlimited |
| Orders appear in | Existing Magento admin panel |
