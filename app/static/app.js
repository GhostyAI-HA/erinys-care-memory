const defaultRequest =
  "Draft the exact door-to-door plan for tomorrow's clinic visit using only what you remember. Include timing, transport, what to bring, questions to ask, and what not to expose. If you lack the memory, say what cannot be known instead of giving a generic checklist.";

const requestInput = document.querySelector("#requestInput");
const runButton = document.querySelector("#runButton");
const resetButton = document.querySelector("#resetButton");
const saveMemoryButton = document.querySelector("#saveMemoryButton");
const demoRunButton = document.querySelector("#demoRunButton");
const demoSaveButton = document.querySelector("#demoSaveButton");
const demoDecisionButton = document.querySelector("#demoDecisionButton");
const memoryInput = document.querySelector("#memoryInput");
const queryParams = new URLSearchParams(window.location.search);
const demoMode = queryParams.get("demo") === "1" || queryParams.get("video") === "1";
const autoTourMode = queryParams.get("autotour") === "1";
const autoSaveMode = queryParams.get("autosave") === "1";
const autoLiveMode = queryParams.get("live") !== "0";
const demoTourDelayMs = 2300;
const demoAutoStartDelayMs = 1000;
let demoTourRound = "initial";
const comparisonTourSteps = [
  {
    id: "no-memory",
    selector: ".no_memory",
    message: "1 No Memory: Qwen is cautious because no personal memory is available.",
  },
  {
    id: "raw-memory",
    selector: ".raw_memory",
    message: "2 Raw Memory: detailed, but stale context and private IDs enter the answer.",
  },
  {
    id: "decision-layer",
    selector: ".why-panel",
    message: "ERINYS classifies memory before Qwen sees the prompt.",
  },
  {
    id: "erinys-qwen",
    selector: ".erinys_qwen",
    message: "3 ERINYS + Qwen: current care facts are selected, unsafe memory is kept out.",
  },
];

requestInput.value = defaultRequest;
document.body.classList.toggle("video-mode", queryParams.get("video") === "1");
document.body.classList.toggle("demo-mode", demoMode);

function appUrl(path) {
  return new URL(path, document.baseURI).toString();
}

function setLoading(isLoading) {
  for (const button of [runButton, resetButton, saveMemoryButton, demoRunButton, demoSaveButton, demoDecisionButton]) {
    button.disabled = isLoading;
  }
  document.body.classList.toggle("loading", isLoading);
}

function setDemoStatus(message) {
  document.querySelector("#demoStatus").textContent = message;
}

function setDemoStep(step) {
  if (!demoMode) return;
  document.body.dataset.demoRound = demoTourRound;
  document.body.dataset.demoStep = step;
}

function focusDemo(selector, step = "manual") {
  if (!demoMode) return;
  setDemoStep(step);
  document.querySelectorAll(".demo-focus").forEach((element) => element.classList.remove("demo-focus"));
  const target = document.querySelector(selector);
  target?.classList.add("demo-focus");
  target?.scrollIntoView({ behavior: "auto", block: "center" });
}

function pauseDemo(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

async function runComparisonTour() {
  if (!demoMode) return;
  for (const step of comparisonTourSteps) {
    setDemoStatus(step.message);
    focusDemo(step.selector, step.id);
    await pauseDemo(demoTourDelayMs);
  }
}

async function runAutoTour() {
  if (!autoTourMode) return;
  await pauseDemo(demoAutoStartDelayMs);
  await runBenchmark({ live: autoLiveMode, focus: true });
  if (autoSaveMode) await saveMemoryAndRerun();
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`${response.status}: ${text}`);
  }
  return response.json();
}

async function refreshHealth() {
  const health = await fetchJson(appUrl("health"));
  const liveText = health.qwen_live_configured
    ? "Live Qwen Cloud configured"
    : "Demo fallback until QWEN_API_KEY is set";
  document.querySelector("#modelLabel").textContent = health.model;
  document.querySelector("#heroModel").textContent = health.qwen_live_configured
    ? `${health.model} live`
    : `${health.model} fallback`;
  document.querySelector("#healthLabel").textContent = liveText;
  document.querySelector("#liveProofLabel").textContent = liveText;
  document.querySelector("#liveDot").classList.toggle("online", health.qwen_live_configured);
  document.querySelector("#persistedBadge").textContent = `${health.persisted_memories} saved`;
  return health;
}

function modeTitle(mode) {
  return {
    no_memory: "No Memory",
    raw_memory: "Raw Memory",
    erinys_qwen: "ERINYS + Qwen",
  }[mode];
}

function renderRun(run) {
  document.querySelector(`#${run.mode}_answer`).textContent = run.answer;
  const provider = providerLabel(run);
  const error = run.provider_error && run.mode === "erinys_qwen" ? ` / ${run.provider_error}` : "";
  document.querySelector(`#${run.mode}_meta`).textContent =
    `Prompt tokens (est.) ~${run.prompt_tokens_estimate} / ${provider}${error}`;
}

function providerLabel(run) {
  if (run.provider === "qwen_cloud") return "Qwen Cloud live";
  if (run.mode === "erinys_qwen" && run.provider_error) return "Qwen timeout fallback";
  if (run.mode === "erinys_qwen") return "governed baseline";
  return "comparison baseline";
}

function renderDecisions(decisions, counts) {
  const countRow = document.querySelector("#decisionCounts");
  countRow.innerHTML = "";
  for (const key of ["selected", "conflicted", "demoted", "blocked"]) {
    const badge = document.createElement("span");
    badge.className = `count ${key}`;
    badge.textContent = `${counts[key]} ${key}`;
    countRow.append(badge);
  }

  const list = document.querySelector("#decisionList");
  list.replaceChildren();
  for (const decision of decisions) {
    const item = document.createElement("div");
    item.className = `decision ${decision.status}`;

    const head = document.createElement("div");
    const id = document.createElement("strong");
    id.textContent = decision.memory.id;
    const status = document.createElement("span");
    status.textContent = decision.status;
    head.append(id, status);

    const reason = document.createElement("p");
    reason.textContent = decision.reason;
    const text = document.createElement("small");
    text.textContent = decision.memory.text;

    item.append(head, reason, text);
    list.append(item);
  }
}

async function runBenchmark({ live = true, focus = true } = {}) {
  setLoading(true);
  try {
    setDemoStatus(live ? "Running live Qwen benchmark..." : "Loading comparison baseline...");
    if (focus) focusDemo(".controls");
    for (const mode of ["no_memory", "raw_memory", "erinys_qwen"]) {
      document.querySelector(`#${mode}_answer`).textContent = `${modeTitle(mode)} is running...`;
    }
    const data = await fetchJson(appUrl("run/benchmark"), {
      method: "POST",
      body: JSON.stringify({
        request: requestInput.value,
        use_live_qwen: live,
        live_modes: ["no_memory", "raw_memory", "erinys_qwen"],
      }),
    });
    for (const run of data.runs) renderRun(run);
    const governed = data.runs.find((run) => run.mode === "erinys_qwen");
    renderDecisions(governed.memory_decisions, data.governance_counts);
    document.querySelector("#tokenBadge").textContent =
      `${data.token_reduction_percent}% fewer prompt tokens after ERINYS governance`;
    await refreshHealth();
    setDemoStatus(live ? "Live benchmark complete. Comparing all three strategies." : "Baseline loaded. Press run for live Qwen.");
    if (focus && demoMode) await runComparisonTour();
    if (focus && !demoMode) focusDemo(live ? ".erinys_qwen" : ".answer-grid");
  } finally {
    setLoading(false);
  }
}

async function saveMemoryAndRerun() {
  setLoading(true);
  try {
    setDemoStatus("Saving the new care memory...");
    demoTourRound = "saved";
    focusDemo(".memory-panel", "save-memory");
    await pauseDemo(demoTourDelayMs);
    await fetchJson(appUrl("memories"), {
      method: "POST",
      body: JSON.stringify({ text: memoryInput.value }),
    });
    await runBenchmark();
    setDemoStatus("Saved memory rerun complete. The governed answer has updated.");
    focusDemo(".decision-panel", "decisions");
  } finally {
    setLoading(false);
  }
}

async function resetMemory() {
  setLoading(true);
  try {
    setDemoStatus("Resetting saved demo memory...");
    demoTourRound = "initial";
    await fetchJson(appUrl("memories/runtime"), { method: "DELETE" });
    await runBenchmark();
    setDemoStatus("Saved memory reset. Demo is back to the initial state.");
  } finally {
    setLoading(false);
  }
}

runButton.addEventListener("click", () => runBenchmark({ live: true }));
saveMemoryButton.addEventListener("click", saveMemoryAndRerun);
resetButton.addEventListener("click", resetMemory);
demoRunButton.addEventListener("click", () => runBenchmark({ live: true }));
demoSaveButton.addEventListener("click", saveMemoryAndRerun);
demoDecisionButton.addEventListener("click", () => {
  setDemoStatus("Inspecting ERINYS memory decisions.");
  focusDemo(".decision-panel", "decisions");
});

refreshHealth().then(() => {
  setDemoStatus("Ready: press 1 to run live Qwen.");
  document.querySelector("#tokenBadge").textContent = "Press run to compare memory strategies.";
  return runAutoTour();
}).catch((error) => {
  document.querySelector("#healthLabel").textContent = error.message;
  setLoading(false);
});
