import { CSSProperties, FormEvent, ReactNode, useEffect, useRef, useState } from "react";
import {
  AgentRun,
  BenchmarkResponse,
  HealthResponse,
  MemoryDecision,
  MemoryStatus,
  benchmarkSchema,
  healthSchema,
  memoryCreateResponseSchema
} from "./types";

const DEFAULT_REQUEST =
  "Draft the exact door-to-door plan for tomorrow's clinic visit using only what you remember. Include timing, transport, what to bring, questions to ask, and what not to expose. If you lack the memory, say what cannot be known instead of giving a generic checklist.";
const DEFAULT_MEMORY =
  "Ask reception to arrange wheelchair assistance at the north entrance before check-in.";
const DEFAULT_MEMORY_STATUS = "No extra memory saved in this browser session yet.";

const MODE_LABELS: Record<AgentRun["mode"], string> = {
  no_memory: "No Memory",
  raw_memory: "Raw Memory",
  erinys_qwen: "ERINYS + Qwen"
};

const MODE_COPY: Record<AgentRun["mode"], { badge: string; subtitle: string }> = {
  no_memory: { badge: "Baseline", subtitle: "Qwen without personal memory context" },
  raw_memory: { badge: "Unsafe", subtitle: "All retrieved memories passed directly" },
  erinys_qwen: { badge: "Governed & safe", subtitle: "ERINYS filters memory before Qwen" }
};

const DANGER_TERMS = ["09:00", "8:10 train", "address", "insurance", "ramen", "east stairway"];
const SAFE_TERMS = ["13:35", "14:20", "taxi", "north entrance", "medication notebook", "blue folder"];
const DECISION_STATUSES: MemoryStatus[] = ["contradiction", "blocked", "selected", "demoted"];
const TOKEN_BAR_MIN_WIDTH = 8;
const TOKEN_BAR_MAX_WIDTH = 100;
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
const IS_VIDEO_MODE = new URLSearchParams(window.location.search).get("video") === "1";

export function App() {
  const [request, setRequest] = useState(DEFAULT_REQUEST);
  const [result, setResult] = useState<BenchmarkResponse | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [memoryText, setMemoryText] = useState(DEFAULT_MEMORY);
  const [isRunning, setIsRunning] = useState(false);
  const [isSavingMemory, setIsSavingMemory] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [memoryStatus, setMemoryStatus] = useState(DEFAULT_MEMORY_STATUS);
  const autoRan = useRef(false);

  useEffect(() => {
    if (autoRan.current) return;
    autoRan.current = true;
    void syncHealth();
    void runBenchmark(DEFAULT_REQUEST);
  }, []);

  async function syncHealth() {
    setHealth(await fetchHealth());
  }

  async function runBenchmark(nextRequest: string) {
    setIsRunning(true);
    setError(null);
    try {
      const response = await fetchBenchmark(nextRequest);
      setResult(response);
      await syncHealth();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Qwen Cloud request failed.");
    } finally {
      setIsRunning(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void runBenchmark(request.trim());
  }

  async function saveMemory(nextMemory: string) {
    setIsSavingMemory(true);
    setError(null);
    try {
      const saved = await fetchCreateMemory(nextMemory);
      setMemoryStatus(`Persistent memory saved as ${saved.memory.id}. Re-running Qwen.`);
      await runBenchmark(request.trim());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Persistent memory save failed.");
    } finally {
      setIsSavingMemory(false);
    }
  }

  function handleMemorySubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void saveMemory(memoryText.trim());
  }

  const runs = groupRuns(result);
  const decisions = runs.erinys_qwen?.memory_decisions ?? [];
  const savings = calculateSavings(runs.raw_memory, runs.erinys_qwen);

  return (
    <main className={`app-shell${IS_VIDEO_MODE ? " video-mode" : ""}`}>
      <TopBar health={health} />
      <section className="content">
        <PromptComposer
          error={error}
          isRunning={isRunning}
          request={request}
          onChange={setRequest}
          onSubmit={handleSubmit}
        />
        <PersistentMemoryPanel
          isSaving={isSavingMemory}
          memory={memoryText}
          persistedCount={health?.persisted_memories ?? 0}
          status={memoryStatus}
          onChange={setMemoryText}
          onSubmit={handleMemorySubmit}
        />
        <ComparisonBanner savings={savings} />
        <section className="comparison-layout">
          <section className="answer-grid">
            <AnswerCard order="1" run={runs.no_memory} variant="no_memory" />
            <AnswerCard order="2" run={runs.raw_memory} variant="raw_memory" />
            <TransformColumn />
            <AnswerCard order="3" run={runs.erinys_qwen} variant="erinys_qwen" />
          </section>
          <MemoryDecisionPanel decisions={decisions} />
        </section>
        <TokenEfficiency rawRun={runs.raw_memory} governedRun={runs.erinys_qwen} />
      </section>
    </main>
  );
}

async function fetchBenchmark(request: string) {
  const response = await fetch(apiUrl("/run/benchmark"), {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ request, scenario: "care_visit" })
  });
  if (!response.ok) {
    throw new Error(await readApiError(response));
  }
  return benchmarkSchema.parse(await response.json());
}

async function fetchHealth() {
  const response = await fetch(apiUrl("/health"));
  return healthSchema.parse(await response.json());
}

async function fetchCreateMemory(text: string) {
  const response = await fetch(apiUrl("/memories"), {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ text, kind: "event", importance: 5, recency: 5 })
  });
  if (!response.ok) {
    throw new Error(await readApiError(response));
  }
  return memoryCreateResponseSchema.parse(await response.json());
}

function apiUrl(path: string) {
  return `${API_BASE_URL}${path}`;
}

async function readApiError(response: Response) {
  const body = await response.json().catch(() => ({}));
  return typeof body.detail === "string" ? body.detail : response.statusText;
}

function TopBar({ health }: { health: HealthResponse | null }) {
  const status = qwenStatusLabel(health);
  return (
    <header className="topbar">
      <div className="brand">
        <div className="brand-mark">E</div>
        <div>
          <strong>ERINYS Care Memory</strong>
          <span>Memory Governance Layer for Qwen Cloud Agents</span>
        </div>
      </div>
      <div className="topbar-actions">
        <span className="mode-pill">{erinysStatusLabel(health)}</span>
        <span className={`cloud-pill ${health?.qwen.mode ?? "unknown"}`}>{status}</span>
        <span className="mode-pill">{persistedMemoryLabel(health)}</span>
      </div>
    </header>
  );
}

function qwenStatusLabel(health: HealthResponse | null) {
  if (!health) return "Qwen status loading";
  if (health.qwen.mode === "live") return `Qwen Cloud live: ${health.qwen.model}`;
  if (health.qwen.mode === "misconfigured") return "Qwen Cloud key missing";
  return `Qwen mock: ${health.qwen.model}`;
}

function erinysStatusLabel(health: HealthResponse | null) {
  if (!health) return "ERINYS runtime loading";
  return `ERINYS Care Memory v${health.erinys.version}`;
}

function persistedMemoryLabel(health: HealthResponse | null) {
  if (!health) return "Persistent memory loading";
  if (IS_VIDEO_MODE && health.persisted_memories === 0) return "ERINYS memory store active";
  return memoryCountLabel(health.persisted_memories, "persisted memory", "persisted memories");
}

function PromptComposer({
  error,
  isRunning,
  request,
  onChange,
  onSubmit
}: {
  error: string | null;
  isRunning: boolean;
  request: string;
  onChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <form className="prompt-panel" onSubmit={onSubmit}>
      <div className="avatar">CG</div>
      <label htmlFor="caregiver-prompt">Caregiver prompt</label>
      <textarea
        id="caregiver-prompt"
        wrap="soft"
        value={request}
        onChange={(event) => onChange(event.target.value)}
      />
      <div className="prompt-actions">
        <span>{error ?? "Live comparison ready."}</span>
        <button disabled={isRunning || request.trim().length === 0} type="submit">
          {isRunning ? "Running..." : "Send"}
        </button>
      </div>
    </form>
  );
}

function PersistentMemoryPanel({
  isSaving,
  memory,
  persistedCount,
  status,
  onChange,
  onSubmit
}: {
  isSaving: boolean;
  memory: string;
  persistedCount: number;
  status: string;
  onChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  const displayStatus = memoryPanelStatus(persistedCount, status);
  return (
    <form className="memory-panel" onSubmit={onSubmit}>
      <div>
        <strong>Persistent memory proof</strong>
        <span>{memoryPanelSubtitle(persistedCount)}</span>
      </div>
      <input value={memory} onChange={(event) => onChange(event.target.value)} />
      <button disabled={isSaving || memory.trim().length === 0} type="submit">
        {isSaving ? "Saving..." : "Save memory + rerun"}
      </button>
      <p>{displayStatus}</p>
    </form>
  );
}

function memoryPanelStatus(persistedCount: number, status: string) {
  if (persistedCount > 0 && status === DEFAULT_MEMORY_STATUS) {
    return "Persistent store loaded. Rerun uses saved memory.";
  }
  return status;
}

function memoryPanelSubtitle(persistedCount: number) {
  if (IS_VIDEO_MODE && persistedCount === 0) return "ERINYS care memory store loaded before Qwen answers";
  return `${memoryCountLabel(persistedCount, "saved note", "saved notes")} loaded before Qwen answers`;
}

function memoryCountLabel(count: number, singular: string, plural: string) {
  return `${count} ${count === 1 ? singular : plural}`;
}

function ComparisonBanner({ savings }: { savings: number }) {
  return (
    <section className="comparison-banner">
      <div>
        <strong>ERINYS governs memory before Qwen generates</strong>
        <span>Same prompt shows what changes when context is selected, blocked, and audited.</span>
      </div>
      <span className="answer-diff-pill">{savings > 0 ? `${savings}% fewer tokens` : "Answer Diff"}</span>
    </section>
  );
}

function AnswerCard({
  order,
  run,
  variant
}: {
  order: string;
  run?: AgentRun;
  variant: AgentRun["mode"];
}) {
  const copy = MODE_COPY[variant];
  return (
    <article className={`answer-card ${variant}`}>
      <header className="answer-card-header">
        <span className="order-badge">{order}</span>
        <div>
          <h2>{MODE_LABELS[variant]}</h2>
          <p>{copy.subtitle}</p>
        </div>
        <span className="mode-badge">{copy.badge}</span>
      </header>
      <OutcomeList variant={variant} />
      <AnswerBody run={run} variant={variant} />
      <p className="token-line">Prompt tokens (est.) {run ? `~${run.prompt_tokens_estimate}` : "..."}</p>
    </article>
  );
}

function AnswerBody({ run, variant }: { run?: AgentRun; variant: AgentRun["mode"] }) {
  const terms = variant === "raw_memory" ? DANGER_TERMS : SAFE_TERMS;
  const className = variant === "raw_memory" ? "danger-mark" : "safe-mark";
  const text = run?.answer ?? "Waiting for the benchmark response.";
  if (IS_VIDEO_MODE) return <VideoAnswerSummary run={run} variant={variant} />;
  return (
    <section className="answer-body">
      <strong>Answer</strong>
      <p>{highlightText(text, variant === "no_memory" ? [] : terms, className)}</p>
    </section>
  );
}

function VideoAnswerSummary({ run, variant }: { run?: AgentRun; variant: AgentRun["mode"] }) {
  return (
    <section className={`answer-summary ${variant}`}>
      <strong>{summaryTitle(variant)}</strong>
      <ul>
        {summaryItems(variant, run).map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
      <p>{summaryProof(variant)}</p>
    </section>
  );
}

function OutcomeList({ variant }: { variant: AgentRun["mode"] }) {
  const items = outcomeItems(variant);
  return (
    <section className="outcomes">
      {items.map((item) => (
        <span key={item}>{item}</span>
      ))}
    </section>
  );
}

function TransformColumn() {
  return (
    <aside className="transform-column">
      <strong>Why ERINYS changes the answer</strong>
      <TransformStep label="Select current care" tone="select" />
      <TransformStep label="Demote stale routine" tone="demote" />
      <TransformStep label="Block private IDs" tone="block" />
    </aside>
  );
}

function TransformStep({ label, tone }: { label: string; tone: string }) {
  return (
    <div className={`transform-step ${tone}`}>
      <span />
      <p>{label}</p>
    </div>
  );
}

function MemoryDecisionPanel({ decisions }: { decisions: MemoryDecision[] }) {
  return (
    <aside className="decision-panel">
      <h2>Memory Decisions</h2>
      <div className="decision-counts">
        <Metric label="selected" value={countStatus(decisions, "selected")} />
        <Metric label="conflicts" value={countStatus(decisions, "contradiction")} />
        <Metric label="demoted" value={countStatus(decisions, "demoted")} />
        <Metric label="blocked" value={countStatus(decisions, "blocked")} />
      </div>
      {DECISION_STATUSES.map((status) => (
        <DecisionList decisions={decisions} key={status} status={status} />
      ))}
    </aside>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

function DecisionList({ decisions, status }: { decisions: MemoryDecision[]; status: MemoryStatus }) {
  const visible = decisions.filter((decision) => decision.status === status).slice(0, 3);
  return (
    <section className={`decision-list ${status}`}>
      <h3>{statusLabel(status)}</h3>
      {visible.map((decision) => (
        <article key={decision.memory.id}>
          <strong>{decision.memory.text}</strong>
          <span>{decision.reason}</span>
        </article>
      ))}
    </section>
  );
}

function TokenEfficiency({
  rawRun,
  governedRun
}: {
  rawRun?: AgentRun;
  governedRun?: AgentRun;
}) {
  const saved = calculateSavings(rawRun, governedRun);
  return (
    <section className="token-efficiency">
      <div>
        <strong>Token Efficiency</strong>
        <span>Context sent to Qwen</span>
      </div>
      <TokenMetric
        label="Raw Memory"
        max={rawRun?.prompt_tokens_estimate}
        tone="raw"
        value={rawRun?.prompt_tokens_estimate}
      />
      <TokenMetric
        label="ERINYS context"
        max={rawRun?.prompt_tokens_estimate}
        tone="governed"
        value={governedRun?.prompt_tokens_estimate}
      />
      <div className="savings">
        <strong>{saved}%</strong>
        <span>fewer context tokens</span>
      </div>
    </section>
  );
}

function TokenMetric({
  label,
  max,
  value,
  tone
}: {
  label: string;
  max?: number;
  value?: number;
  tone: string;
}) {
  const width = tokenBarWidth(value, max);
  return (
    <div className={`token-metric ${tone}`}>
      <span>{label}</span>
      <strong>{value ? `~${value} tokens` : "..."}</strong>
      <div style={{ "--bar-width": width } as CSSProperties} />
    </div>
  );
}

function groupRuns(result: BenchmarkResponse | null) {
  return {
    no_memory: result?.runs.find((run) => run.mode === "no_memory"),
    raw_memory: result?.runs.find((run) => run.mode === "raw_memory"),
    erinys_qwen: result?.runs.find((run) => run.mode === "erinys_qwen")
  };
}

function outcomeItems(variant: AgentRun["mode"]) {
  if (variant === "raw_memory") return ["Confident but conflicted", "Private IDs may leak", "Stale route enters plan"];
  if (variant === "erinys_qwen") return ["Exact current plan", "Blocks private IDs", "Explains memory decisions"];
  return ["Cannot know exact timing", "Cannot know transport constraints", "Asks for missing facts"];
}

function summaryTitle(variant: AgentRun["mode"]) {
  if (variant === "raw_memory") return "What goes wrong";
  if (variant === "erinys_qwen") return "What ERINYS changes";
  return "What Qwen cannot know";
}

function summaryItems(variant: AgentRun["mode"], run?: AgentRun) {
  if (variant === "raw_memory") {
    return ["Leaks synthetic door code and phone ID.", "Mixes stale 09:00 routine into the plan.", "Sounds confident while using unsafe context."];
  }
  if (variant === "erinys_qwen") {
    if (hasPersistentCareMemory(run)) {
      return ["Selects the current 13:35 taxi plan.", "Adds wheelchair assistance from persisted memory.", "Blocks private IDs before Qwen sees them."];
    }
    return ["Selects the current 13:35 taxi plan.", "Blocks private IDs before Qwen sees them.", "Leaves selected, demoted, conflict, and blocked decisions auditable."];
  }
  return ["No appointment time.", "No transport or entrance constraints.", "No memory of forgotten paperwork."];
}

function hasPersistentCareMemory(run?: AgentRun) {
  return run?.used_memories.includes("u001") ?? false;
}

function summaryProof(variant: AgentRun["mode"]) {
  if (variant === "raw_memory") return "Memory is present, but ungoverned.";
  if (variant === "erinys_qwen") return "ERINYS governs memory. Qwen generates the answer.";
  return "Safe, but not operational.";
}

function countStatus(decisions: MemoryDecision[], status: MemoryStatus) {
  return decisions.filter((decision) => decision.status === status).length;
}

function statusLabel(status: MemoryStatus) {
  if (status === "contradiction") return "conflicts";
  return status;
}

function calculateSavings(rawRun?: AgentRun, governedRun?: AgentRun) {
  if (!rawRun || !governedRun || rawRun.prompt_tokens_estimate === 0) return 0;
  return Math.max(0, Math.round((1 - governedRun.prompt_tokens_estimate / rawRun.prompt_tokens_estimate) * 100));
}

function tokenBarWidth(value?: number, max?: number) {
  if (!value || !max) return "0%";
  const percent = Math.round((value / max) * TOKEN_BAR_MAX_WIDTH);
  return `${Math.max(TOKEN_BAR_MIN_WIDTH, Math.min(TOKEN_BAR_MAX_WIDTH, percent))}%`;
}

function highlightText(text: string, terms: readonly string[], className: string): ReactNode[] {
  if (terms.length === 0) return [text];
  const pattern = new RegExp(`(${terms.map(escapeRegex).join("|")})`, "gi");
  return text.split(pattern).map((part, index) =>
    terms.some((term) => term.toLowerCase() === part.toLowerCase()) ? (
      <mark className={className} key={`${part}-${index}`}>{part}</mark>
    ) : (
      part
    )
  );
}

function escapeRegex(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
