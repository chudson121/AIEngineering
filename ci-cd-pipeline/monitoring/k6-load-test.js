/**
 * k6 load test for AI application latency SLO validation
 * RA Section 5.6 – Performance, reliability, and cost
 * RA Section 6   – p95 latency gate
 *
 * Run:
 *   k6 run --out json=reports/k6_results.json \
 *     --env LLM_PROVIDER=openai \
 *     --env ENDPOINT=https://your-staging-endpoint \
 *     monitoring/k6-load-test.js
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend, Counter } from "k6/metrics";

// ── Custom metrics ──────────────────────────────────────────────────────────
const errorRate          = new Rate("errors");
const llmLatency         = new Trend("llm_response_duration_ms", true);
const toolCallLatency    = new Trend("tool_call_duration_ms", true);
const tokensUsed         = new Counter("total_tokens_used");
const fallbackCount      = new Counter("provider_fallbacks");

// ── Options ─────────────────────────────────────────────────────────────────
export const options = {
  stages: [
    { duration: "1m",  target: 5  },   // ramp-up
    { duration: "3m",  target: 20 },   // sustained load
    { duration: "1m",  target: 50 },   // peak
    { duration: "1m",  target: 0  },   // ramp-down
  ],
  thresholds: {
    // RA Section 6 – p95 must not exceed SLO
    http_req_duration: ["p(95)<3000"],
    // Error rate < 1%
    errors: ["rate<0.01"],
    // p99 tail latency
    "http_req_duration{percentile:99}": ["p(99)<6000"],
  },
};

const BASE_URL  = __ENV.ENDPOINT || "http://localhost:8000";
const PROVIDER  = __ENV.LLM_PROVIDER || "openai";

// Sample queries representative of real production traffic
const SAMPLE_QUERIES = [
  "What is the adoption leave policy for employees hired after 2023?",
  "Summarize the expense reimbursement guidelines.",
  "How do I submit a PTO request?",
  "What is the enterprise API rate limit for the standard tier?",
  "Explain the data retention policy for customer records.",
];

// ── Utility ──────────────────────────────────────────────────────────────────
function randomQuery() {
  return SAMPLE_QUERIES[Math.floor(Math.random() * SAMPLE_QUERIES.length)];
}

// ── Main VU scenario ────────────────────────────────────────────────────────
export default function () {
  const payload = JSON.stringify({
    query:    randomQuery(),
    session_id: `k6-${__VU}-${__ITER}`,
    provider: PROVIDER,
  });

  const params = {
    headers: {
      "Content-Type":  "application/json",
      "X-Test-Client": "k6-load-test",
    },
    timeout: "10s",
  };

  // ── RAG query endpoint ────────────────────────────────────────────────────
  const start = Date.now();
  const res = http.post(`${BASE_URL}/api/query`, payload, params);
  const duration = Date.now() - start;

  llmLatency.add(duration);

  const ok = check(res, {
    "status 200":           (r) => r.status === 200,
    "has answer field":     (r) => r.json("answer") !== null,
    "has sources field":    (r) => Array.isArray(r.json("sources")),
    "latency < 5s":         () => duration < 5000,
  });

  errorRate.add(!ok);

  // Track token usage if the API exposes it
  if (res.status === 200) {
    const body = res.json();
    if (body.usage && body.usage.total_tokens) {
      tokensUsed.add(body.usage.total_tokens);
    }
    if (body.provider_fallback === true) {
      fallbackCount.add(1);
    }
  }

  // ── Health / liveness endpoint (lightweight) ──────────────────────────────
  const healthRes = http.get(`${BASE_URL}/health`, { timeout: "2s" });
  check(healthRes, {
    "health 200": (r) => r.status === 200,
  });

  sleep(Math.random() * 2 + 1);   // 1–3 second think time
}

// ── Summary output handler ────────────────────────────────────────────────────
export function handleSummary(data) {
  // Flatten key percentiles for threshold checker downstream
  const summary = {
    p50_latency_ms: data.metrics.http_req_duration.values["p(50)"],
    p95_latency_ms: data.metrics.http_req_duration.values["p(95)"],
    p99_latency_ms: data.metrics.http_req_duration.values["p(99)"],
    error_rate:     data.metrics.errors          ? data.metrics.errors.values.rate : 0,
    fallback_count: data.metrics.provider_fallbacks
                      ? data.metrics.provider_fallbacks.values.count : 0,
    total_requests: data.metrics.http_reqs.values.count,
    metrics: data.metrics,
  };

  return {
    stdout:                    JSON.stringify(summary, null, 2),
    "reports/k6_results.json": JSON.stringify(summary, null, 2),
  };
}
