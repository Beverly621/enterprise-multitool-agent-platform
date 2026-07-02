# Sample Order Abnormal Analysis Handbook

> This self-written handbook supports the demo question: "结合最近 30 天订单异常数据和售后知识库生成一份分析报告。"

## 1. Abnormal Order Definition

For this demo project, an abnormal order includes any order with one or more of the following signals:

- `canceled`
- `unavailable`
- `delivery_delay`
- `review_score <= 2`
- `refund_request`
- `product_damage`
- `wrong_item`
- `payment_issue`
- `customer_complaint`

## 2. Canceled Orders

Canceled orders should be analyzed by region, product category, payment status, and cancellation reason. A concentration of cancellations in one region may indicate logistics or inventory problems.

## 3. Delivery Delay

Delivery delay should be grouped by region and category. Repeated delays in the same state may indicate carrier capacity issues. Delays in fragile or high-value categories may require proactive customer communication.

## 4. Low Review Score

Low review score means `review_score <= 2`. Low scores should be compared with issue type, delivery delay, after-sales status, and category. A cluster of low scores in one product category can indicate quality or expectation mismatch.

## 5. After-Sales Complaints

Common after-sales issue types include refund request, product damage, wrong item, payment issue, and customer complaint. The most frequent issue type should be included in the final report with recommended action.

## 6. Abnormal Amount

High-value abnormal orders should be reviewed manually. A high order amount combined with refund request or product damage increases business risk.

## 7. Regional Clustering

Regional clustering should identify which state has the most abnormal orders in the last 30 days. The report should include top regions, top categories, main issue types, and suggested operations follow-up.

## 8. Report Requirements

An order abnormal report should include time range, total abnormal order count, top abnormal regions, top issue types, low-score category distribution, relevant after-sales policy evidence, recommended actions, and traceable data sources.

