import { z } from "zod";

export const memoryDecisionSchema = z.object({
  memory: z.object({
    id: z.string(),
    text: z.string(),
    kind: z.string(),
    decision_note: z.string().nullable().optional()
  }),
  status: z.enum(["selected", "ignored", "demoted", "blocked", "contradiction"]),
  reason: z.string(),
  score: z.number()
});

export const agentRunSchema = z.object({
  mode: z.enum(["no_memory", "raw_memory", "erinys_qwen"]),
  answer: z.string(),
  used_memories: z.array(z.string()),
  memory_decisions: z.array(memoryDecisionSchema),
  prompt_tokens_estimate: z.number()
});

export const benchmarkSchema = z.object({
  request: z.string(),
  runs: z.array(agentRunSchema)
});

export const erinysStatusSchema = z.object({
  provider: z.literal("erinys"),
  runtime: z.string(),
  version: z.string(),
  policy: z.string(),
  select_threshold: z.number(),
  token_divisor: z.number()
});

export const qwenStatusSchema = z.object({
  provider: z.string(),
  model: z.string(),
  base_url: z.string(),
  api_key_configured: z.boolean(),
  mock_requested: z.boolean(),
  mode: z.enum(["mock", "misconfigured", "live"])
});

export const healthSchema = z.object({
  status: z.string(),
  seed: z.string(),
  qwen: qwenStatusSchema,
  erinys: erinysStatusSchema,
  persisted_memories: z.number()
});

export const memoryCreateResponseSchema = z.object({
  memory: memoryDecisionSchema.shape.memory,
  persisted: z.boolean(),
  store: z.string(),
  user_memory_count: z.number()
});

export type AgentRun = z.infer<typeof agentRunSchema>;
export type BenchmarkResponse = z.infer<typeof benchmarkSchema>;
export type HealthResponse = z.infer<typeof healthSchema>;
export type MemoryCreateResponse = z.infer<typeof memoryCreateResponseSchema>;
export type MemoryDecision = z.infer<typeof memoryDecisionSchema>;
export type MemoryStatus = MemoryDecision["status"];
export type QwenStatus = z.infer<typeof qwenStatusSchema>;
export type ErinysStatus = z.infer<typeof erinysStatusSchema>;
