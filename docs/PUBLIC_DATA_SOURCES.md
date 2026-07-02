# Public Data Sources

## 1. Data Usage Statement

This project does not use real enterprise internal data, real customer orders, real customer complaints, or private personal information.

The `demo_orders`, `demo_reviews`, and `demo_after_sales` records used by this project are deterministic simulated data for technical demonstration only. The knowledge-base files under `data/demo_docs/` are self-written sample policies for RAG testing.

## 2. Why Simulated Business Data Is Used

Real large-company order anomalies, customer complaints, refund decisions, and internal policy documents are usually private and cannot be redistributed in a public GitHub repository.

The project therefore uses simulated e-commerce data with realistic field names and business scenarios. This keeps the demo reproducible while avoiding privacy, compliance, and licensing issues.

## 3. Public Reference Sources

The following public sources can be used as learning references or linked as external source material. Do not copy large protected passages into this repository unless the license clearly allows redistribution.

- Apple Business Conduct and policy pages: https://www.apple.com/compliance/
- Microsoft Standards of Business Conduct: https://www.microsoft.com/en-us/legal/compliance/sbc
- Amazon return help pages: https://www.amazon.com/gp/help/customer/display.html
- CFPB Consumer Complaint Database: https://www.consumerfinance.gov/data-research/consumer-complaints/
- Olist Brazilian E-Commerce Public Dataset: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- Instacart Market Basket Dataset: https://www.instacart.com/datasets/grocery-shopping-2017

## 4. Demo Documents

The repository includes self-written demo documents:

- `data/demo_docs/sample_company_policy.md`
- `data/demo_docs/sample_after_sales_policy.md`
- `data/demo_docs/sample_return_policy.md`
- `data/demo_docs/sample_order_abnormal_handbook.md`

These files are designed to support RAG questions about conflicts of interest, human approval, data security, returns, refunds, delivery delay, damaged products, wrong items, and abnormal order analysis.

## 5. Demo Order Data

The repository includes deterministic simulated CSV files:

- `data/demo_orders/demo_customers.csv`
- `data/demo_orders/demo_products.csv`
- `data/demo_orders/demo_orders.csv`
- `data/demo_orders/demo_order_items.csv`
- `data/demo_orders/demo_reviews.csv`
- `data/demo_orders/demo_after_sales.csv`

The dataset covers at least 10 states, 10 product categories, 320 orders, 400 order items, 320 reviews, and more than 80 after-sales records.

Covered abnormal signals include:

- `canceled`
- `unavailable`
- `delivery_delay`
- `review_score <= 2`
- `refund_request`
- `product_damage`
- `wrong_item`
- `payment_issue`
- `customer_complaint`

## 6. Compliance Notes

- Do not commit `.env`, `.env.local`, real API keys, tokens, secrets, private database URLs, real customer data, or real enterprise documents.
- Keep only `.env.example` templates in Git.
- Use Mock LLM and Mock Embedding providers for public demos when real provider keys are not configured.
- Treat generated reports as demo output unless connected to a real approved environment.
- Before publishing, run `bash scripts/check_public_safety.sh`.

