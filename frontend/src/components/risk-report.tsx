"use client";

import { useEffect, useState } from "react";

import { CheckIcon, ExternalLinkIcon, WarningIcon } from "@/components/icons";
import type { CheckStatus, RiskLevel, TrustReport, VerificationCheck } from "@/types/trust-report";

const riskTone: Record<RiskLevel, { text: string; badge: string; stroke: string; verdict: string }> = {
  "LOW RISK": {
    text: "text-emerald-300",
    badge: "border-emerald-300/25 bg-emerald-300/10 text-emerald-200",
    stroke: "#34d399",
    verdict: "Looks safe",
  },
  "MEDIUM RISK": {
    text: "text-amber-300",
    badge: "border-amber-300/25 bg-amber-300/10 text-amber-200",
    stroke: "#fbbf24",
    verdict: "Be careful",
  },
  "HIGH RISK": {
    text: "text-rose-300",
    badge: "border-rose-300/25 bg-rose-300/10 text-rose-200",
    stroke: "#fb7185",
    verdict: "Likely a scam",
  },
};

const statusStyle: Record<CheckStatus | "skipped", string> = {
  ok: "border-emerald-300/20 bg-emerald-300/10 text-emerald-200",
  warn: "border-amber-300/20 bg-amber-300/10 text-amber-200",
  bad: "border-rose-300/20 bg-rose-300/10 text-rose-200",
  error: "border-slate-400/20 bg-slate-400/10 text-slate-300",
  skipped: "border-slate-400/20 bg-slate-400/10 text-slate-300",
};

function RiskGauge({ score, level }: { score: number; level: RiskLevel }) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const radius = 48;
  const circumference = 2 * Math.PI * radius;
  const safeScore = Math.max(0, Math.min(100, score));
  const tone = riskTone[level];

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => setAnimatedScore(safeScore));
    return () => window.cancelAnimationFrame(frame);
  }, [safeScore]);

  return (
    <div role="img" aria-label={`Risk score ${score} out of 100, ${level.toLowerCase()}`} className="relative size-40 shrink-0 sm:size-48">
      <svg viewBox="0 0 120 120" className="size-full -rotate-90">
        <circle cx="60" cy="60" r={radius} fill="none" stroke="rgba(148,163,184,0.13)" strokeWidth="8" />
        <circle
          cx="60"
          cy="60"
          r={radius}
          fill="none"
          stroke={tone.stroke}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference * (1 - animatedScore / 100)}
          className="transition-[stroke-dashoffset] duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`font-mono text-5xl font-semibold tabular-nums ${tone.text}`}>{score}</span>
        <span className="mt-1 text-[10px] font-semibold uppercase text-slate-500">out of 100</span>
      </div>
    </div>
  );
}

function CheckCard({ check, index }: { check: VerificationCheck; index: number }) {
  const isSkipped = check.status === "error" && check.summary.toLowerCase().includes("skipped");
  const displayStatus = isSkipped ? "skipped" : check.status;
  const maxPoints = Math.max(0, check.max_points);
  const points = Math.max(0, Math.min(check.risk_points, maxPoints));
  const width = maxPoints > 0 ? `${(points / maxPoints) * 100}%` : "0%";
  const barColor = check.status === "bad"
    ? "bg-rose-400"
    : check.status === "warn"
      ? "bg-amber-300"
      : check.status === "ok"
        ? "bg-emerald-300"
        : "bg-slate-500";

  return (
    <article
      className="check-reveal flex min-h-56 flex-col rounded-xl border border-white/10 bg-slate-950/35 p-4"
      style={{ animationDelay: `${index * 70}ms` }}
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <h3 className="max-w-[16rem] text-sm font-semibold leading-5 text-slate-100">{check.name}</h3>
        <span className={`shrink-0 rounded-md border px-2 py-1 text-[10px] font-bold uppercase ${statusStyle[displayStatus]}`}>
          {displayStatus}
        </span>
      </div>
      <span className="mt-3 w-fit max-w-full truncate rounded-md border border-cyan-300/15 bg-cyan-300/[0.05] px-2 py-1 font-mono text-[10px] text-cyan-100/75">
        {check.tool_used}
      </span>
      <p className="mt-3 flex-1 text-xs leading-5 text-slate-400">{check.summary}</p>

      <div className="mt-4">
        <div className="mb-1.5 flex items-center justify-between font-mono text-[10px] text-slate-500">
          <span>Risk points</span>
          <span>{check.risk_points} / {check.max_points}</span>
        </div>
        <div className="h-1.5 overflow-hidden rounded-full bg-white/10">
          <div className={`h-full rounded-full transition-[width] duration-700 ${barColor}`} style={{ width }} />
        </div>
      </div>

      {check.evidence.length > 0 && (
        <ul className="mt-4 space-y-2 border-t border-white/[0.07] pt-3">
          {check.evidence.map((item, itemIndex) => (
            <li key={`${item.url}-${itemIndex}`} className="min-w-0">
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex max-w-full items-center gap-1.5 text-xs text-cyan-200 underline decoration-cyan-300/25 underline-offset-4 transition hover:text-cyan-100 focus-visible:rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300"
              >
                <span className="truncate">{item.label}</span>
                <ExternalLinkIcon className="size-3 shrink-0" />
              </a>
              <p className="mt-1 break-all font-mono text-[9px] leading-4 text-slate-600">{item.retrieved_at}</p>
            </li>
          ))}
        </ul>
      )}
    </article>
  );
}

export default function RiskReportView({ report, onCheckAnother }: { report: TrustReport; onCheckAnother: () => void }) {
  const tone = riskTone[report.level];

  return (
    <section aria-live="polite" aria-busy="false" className="fade-slide-in space-y-10">
      <article className="glass-panel overflow-hidden rounded-2xl border border-white/10 shadow-[0_24px_90px_-52px_rgba(34,211,238,0.32)]">
        <div className="grid items-center gap-6 p-5 sm:grid-cols-[auto_1fr] sm:gap-9 sm:p-8">
          <div className="mx-auto">
            <RiskGauge score={report.risk_score} level={report.level} />
          </div>
          <div className="text-center sm:text-left">
            <div className="flex flex-wrap items-center justify-center gap-3 sm:justify-start">
              <span className={`rounded-full border px-3 py-1.5 text-xs font-bold tracking-wide ${tone.badge}`}>
                {report.level}
              </span>
              <span className="font-mono text-[10px] uppercase text-slate-500">Trust assessment</span>
            </div>
            <h2 className={`mt-4 text-2xl font-semibold sm:text-3xl ${tone.text}`}>{tone.verdict}</h2>
            <p className="mx-auto mt-3 max-w-2xl text-sm leading-7 text-slate-300 sm:mx-0">{report.summary}</p>
            <p className="mt-4 font-mono text-[10px] text-slate-600">Generated {report.generated_at}</p>
          </div>
        </div>
        <div className="h-px bg-gradient-to-r from-transparent via-cyan-300/20 to-transparent" />
        <div className="flex flex-wrap items-center justify-center gap-x-8 gap-y-2 px-5 py-4 text-[10px] font-semibold uppercase tracking-[0.12em] text-slate-500 sm:justify-start sm:px-8">
          <span>Claim extraction</span><span>Live checks</span><span>Evidence review</span>
        </div>
      </article>

      <section aria-labelledby="red-flags-title">
        <div className="mb-4 flex items-center gap-3">
          <span className="h-5 w-1 rounded-full bg-rose-400" />
          <h2 id="red-flags-title" className="text-lg font-semibold text-slate-100">Red flags</h2>
          <span className="font-mono text-xs text-slate-500">{report.red_flags.length.toString().padStart(2, "0")}</span>
        </div>
        {report.red_flags.length > 0 ? (
          <ul className="space-y-2">
            {report.red_flags.map((flag, index) => (
              <li key={`${flag}-${index}`} className="flex items-start gap-3 rounded-lg border border-rose-300/10 bg-rose-300/[0.035] px-4 py-3 text-sm leading-6 text-slate-300">
                <WarningIcon className="mt-1 size-4 shrink-0 text-rose-300" />
                <span>{flag}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="flex items-center gap-2 rounded-lg border border-emerald-300/15 bg-emerald-300/[0.05] px-4 py-3 text-sm text-emerald-200">
            <CheckIcon className="size-4" /> No red flags found
          </p>
        )}
      </section>

      <section aria-labelledby="checks-title">
        <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-cyan-200/60">Verification trail</p>
            <h2 id="checks-title" className="mt-1 text-lg font-semibold text-slate-100">Checks performed</h2>
          </div>
          <span className="font-mono text-xs text-slate-500">{report.checks.length} checks</span>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {report.checks.map((check, index) => (
            <CheckCard key={`${check.name}-${index}`} check={check} index={index} />
          ))}
        </div>
      </section>

      <div className="flex justify-center pt-1">
        <button
          type="button"
          onClick={onCheckAnother}
          className="rounded-xl border border-cyan-300/25 bg-cyan-300/[0.05] px-5 py-3 text-sm font-semibold text-cyan-100 transition hover:border-cyan-200/50 hover:bg-cyan-300/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300"
        >
          Check another offer
        </button>
      </div>
    </section>
  );
}