export type ApiEnvelope<T> = {
  data: T;
  message?: string;
};

export type User = {
  id: number;
  email: string;
  full_name?: string | null;
  is_active: boolean;
  roles: string[];
  permissions: string[];
};

export type KnowledgeBase = {
  id: number;
  name: string;
  description?: string | null;
  visibility: string;
  owner_id?: number | null;
  created_at?: string;
  updated_at?: string;
  documents?: DocumentRecord[];
};

export type DocumentRecord = {
  id: number;
  kb_id: number;
  filename: string;
  file_type: string;
  status: string;
  chunk_count: number;
  error_message?: string | null;
  created_at?: string;
  updated_at?: string;
};

export type AgentResponse = {
  run_id: string;
  task_id?: string;
  intent?: string | null;
  status: string;
  answer?: string | null;
  message?: string;
  approval_id?: string | null;
  progress_url?: string;
  trace_url: string;
  citations?: Array<Record<string, unknown>>;
  generated_sql?: string | null;
  sql_result?: Record<string, unknown> | null;
  tool_results?: Array<Record<string, unknown>>;
  error?: string | null;
};

export type RunRecord = {
  id: number;
  run_id: string;
  user_id?: number | null;
  session_id?: string | null;
  query: string;
  intent?: string | null;
  status: string;
  current_step?: string | null;
  final_answer?: string | null;
  error_message?: string | null;
  created_at?: string;
  updated_at?: string;
  finished_at?: string | null;
};

export type TaskProgress = {
  run_id?: string | null;
  task_id: string;
  task_type: string;
  status: string;
  progress: number;
  current_stage?: string | null;
  message?: string | null;
  error_message?: string | null;
  updated_at?: string;
};

export type ReportRecord = {
  id: number;
  report_id: string;
  run_id?: string | null;
  title: string;
  report_type: string;
  content_markdown: string;
  summary?: string | null;
  source_metadata_json?: Record<string, unknown> | null;
  status: string;
  created_at?: string;
};

export type ToolRecord = {
  id: number;
  name: string;
  description?: string | null;
  schema_json: Record<string, unknown>;
  permission_level: string;
  require_approval?: boolean;
  requires_approval?: boolean;
  enabled?: boolean;
  is_active?: boolean;
  timeout_ms?: number;
  retry_count?: number;
};

export type ApprovalRecord = {
  id: number;
  approval_id: string;
  tool_call_id?: string | null;
  tool_name?: string | null;
  run_id?: string | null;
  status: string;
  reason?: string | null;
  created_at?: string;
  approved_at?: string | null;
};

export type DashboardSummary = {
  knowledge_bases: number;
  documents: number;
  agent_runs: number;
  tasks: number;
  reports: number;
  tool_calls: number;
  pending_approvals: number;
  failed_tasks: number;
  recent_runs: RunRecord[];
  recent_reports: ReportRecord[];
  recent_tool_calls: Array<Record<string, unknown>>;
  recent_audit_logs: Array<Record<string, unknown>>;
  observability?: {
    agent_run_success_rate: number;
    avg_run_duration_ms: number;
    p95_run_duration_ms: number;
    rag_queries_total: number;
    sql_blocked_total: number;
    tool_success_rate: number;
    async_task_success_rate: number;
    reports_generated: number;
    provider_calls_total: number;
    estimated_total_cost: number;
    latest_eval_runs?: Array<Record<string, unknown>>;
  };
};
