export type RiskLevel = "LOW RISK" | "MEDIUM RISK" | "HIGH RISK";
export type CheckStatus = "ok" | "warn" | "bad" | "error";

export interface EvidenceItem {
  label: string;
  url: string;
  retrieved_at: string;
}

export interface VerificationCheck {
  name: string;
  tool_used: string;
  status: CheckStatus;
  summary: string;
  risk_points: number;
  max_points: number;
  evidence: EvidenceItem[];
}

export interface TrustReport {
  claims: Record<string, unknown>;
  checks: VerificationCheck[];
  risk_score: number;
  level: RiskLevel;
  red_flags: string[];
  summary: string;
  generated_at: string;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isHttpUrl(value: string): boolean {
  try {
    const url = new URL(value);
    return url.protocol === "https:" || url.protocol === "http:";
  } catch {
    return false;
  }
}

export function isTrustReport(value: unknown): value is TrustReport {
  if (!isRecord(value)) return false;
  if (!isRecord(value.claims) || !Array.isArray(value.checks)) return false;
  if (!Array.isArray(value.red_flags) || !value.red_flags.every((flag) => typeof flag === "string")) return false;
  if (typeof value.risk_score !== "number" || typeof value.summary !== "string") return false;
  if (typeof value.generated_at !== "string") return false;
  if (value.level !== "LOW RISK" && value.level !== "MEDIUM RISK" && value.level !== "HIGH RISK") return false;

  return value.checks.every((check) => {
    if (!isRecord(check) || !Array.isArray(check.evidence)) return false;
    if (typeof check.name !== "string" || typeof check.tool_used !== "string") return false;
    if (typeof check.summary !== "string" || typeof check.risk_points !== "number") return false;
    if (typeof check.max_points !== "number") return false;
    if (!["ok", "warn", "bad", "error"].includes(String(check.status))) return false;
    return check.evidence.every((item) =>
      isRecord(item)
      && typeof item.label === "string"
      && typeof item.url === "string"
      && isHttpUrl(item.url)
      && typeof item.retrieved_at === "string",
    );
  });
}