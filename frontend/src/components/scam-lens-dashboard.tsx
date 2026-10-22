"use client";

import { useEffect, useRef, useState } from "react";

import { ShieldSearchIcon } from "@/components/icons";
import OfferForm from "@/components/offer-form";
import RiskReportView from "@/components/risk-report";
import { isTrustReport, type TrustReport } from "@/types/trust-report";

const apiBaseUrl = (process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000").replace(/\/+$/, "");

export default function ScamLensDashboard() {
  const [text, setText] = useState("");
  const [mode, setMode] = useState<"live" | "mock" | null>(null);
  const [report, setReport] = useState<TrustReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const resultsRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let active = true;
    fetch(`${apiBaseUrl}/health`, { cache: "no-store" })
      .then((response) => {
        if (!response.ok) throw new Error("Health check unavailable");
        return response.json() as Promise<{ mode?: unknown }>;
      })
      .then((health) => {
        if (active && (health.mode === "live" || health.mode === "mock")) {
          setMode(health.mode);
        }
      })
      .catch(() => {
        if (active) setMode(null);
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!report || !resultsRef.current) return;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    resultsRef.current.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
  }, [report]);

  async function verifyOffer(offerText: string) {
    if (!offerText.trim() || loading) return;
    setLoading(true);
    setError(null);
    setReport(null);

    const controller = new AbortController();
    let timedOut = false;
    const timeoutId = window.setTimeout(() => {
      timedOut = true;
      controller.abort();
    }, 60_000);

    try {
      const response = await fetch(`${apiBaseUrl}/api/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: offerText }),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error("The verification service returned an error. Please try again.");
      }

      const payload: unknown = await response.json();
      if (!isTrustReport(payload)) {
        throw new Error("The verification service returned an unexpected response. Please try again.");
      }
      setReport(payload);
    } catch (requestError) {
      if (timedOut) {
        setError("The check took longer than 30 seconds. Please retry in a moment.");
      } else if (requestError instanceof Error && requestError.message.startsWith("The verification service")) {
        setError(requestError.message);
      } else {
        setError("We couldn’t connect to ScamLens AI. Check that the API is running, then retry.");
      }
    } finally {
      window.clearTimeout(timeoutId);
      setLoading(false);
    }
  }

  function clearResults() {
    setReport(null);
    setError(null);
    formRef.current?.querySelector("textarea")?.focus();
  }

  return (
    <main className="relative isolate min-h-screen overflow-hidden px-4 pb-8 pt-5 sm:px-7 sm:pt-8">
      <div aria-hidden="true" className="ambient-orb ambient-orb-cyan" />
      <div aria-hidden="true" className="ambient-orb ambient-orb-blue" />

      <div className="mx-auto max-w-5xl">
        <header className="flex flex-wrap items-center justify-between gap-3 border-b border-white/[0.07] pb-4">
          <a href="#top" className="inline-flex items-center gap-3 rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300" aria-label="ScamLens AI home">
            <span className="relative grid size-10 place-items-center text-cyan-200">
              <span aria-hidden="true" className="logo-pulse absolute inset-0 rounded-full bg-cyan-300/20 blur-lg" />
              <ShieldSearchIcon className="relative size-9" />
            </span>
            <span className="text-sm font-semibold tracking-wide text-slate-100">ScamLens <span className="text-cyan-300">AI</span></span>
          </a>
          {mode && (
            <span className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 font-mono text-[10px] ${
              mode === "live"
                ? "border-cyan-300/20 bg-cyan-300/[0.06] text-cyan-100"
                : "border-slate-400/20 bg-slate-400/[0.06] text-slate-300"
            }`}>
              <span className={`size-1.5 rounded-full ${mode === "live" ? "bg-cyan-300" : "bg-slate-400"}`} />
              {mode === "live" ? "Live mode" : "Demo mode"}
            </span>
          )}
        </header>

        <section id="top" className="pb-8 pt-10 text-center sm:pb-10 sm:pt-14">
          <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.24em] text-cyan-200/70">Student offer verification</p>
          <h1 className="mt-3 bg-gradient-to-r from-cyan-200 via-sky-300 to-blue-400 bg-clip-text text-4xl font-semibold text-transparent sm:text-5xl">
            ScamLens AI
          </h1>
          <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-slate-300 sm:text-base">
            Check internship and job offers for scam signs
          </p>
          <div className="mt-5 flex flex-wrap justify-center gap-2">
            {[
              ["01", "Instant analysis"],
              ["02", "Evidence-backed"],
              ["03", "Free to use"],
            ].map(([number, label]) => (
              <span key={label} className="inline-flex items-center gap-2 rounded-full border border-white/[0.08] bg-white/[0.025] px-3 py-1.5 text-[11px] text-slate-300">
                <span className="font-mono text-[9px] text-cyan-300/70">{number}</span>{label}
              </span>
            ))}
          </div>
        </section>

        <div ref={formRef} className="scroll-mt-6">
          <OfferForm
            text={text}
            loading={loading}
            onTextChange={setText}
            onSubmit={() => void verifyOffer(text)}
          />
        </div>

        {loading && (
          <section aria-live="polite" aria-busy="true" className="fade-slide-in mt-5 overflow-hidden rounded-xl border border-cyan-300/15 bg-slate-950/45 px-5 py-4">
            <div className="flex items-center gap-3">
              <span className="size-4 animate-spin rounded-full border-2 border-cyan-200/20 border-t-cyan-200" />
              <p className="text-sm font-medium text-cyan-100">Analyzing offer...</p>
              <span className="ml-auto hidden font-mono text-[10px] text-slate-500 sm:inline">CLAIMS / CHECKS / EVIDENCE</span>
            </div>
            <div className="relative mt-4 h-1 overflow-hidden rounded-full bg-white/[0.06]">
              <span className="scan-line absolute inset-x-0 top-0 h-full w-1/3 rounded-full bg-gradient-to-r from-transparent via-cyan-300 to-transparent" />
            </div>
          </section>
        )}

        {error && (
          <section role="alert" aria-live="assertive" className="fade-slide-in mt-5 flex flex-col gap-4 rounded-xl border border-rose-300/20 bg-rose-300/[0.055] p-4 sm:flex-row sm:items-center sm:justify-between sm:p-5">
            <div>
              <h2 className="text-sm font-semibold text-rose-100">We couldn’t complete the check</h2>
              <p className="mt-1 text-sm leading-6 text-slate-300">{error}</p>
            </div>
            <button
              type="button"
              onClick={() => void verifyOffer(text)}
              disabled={loading || !text.trim()}
              className="shrink-0 rounded-lg border border-rose-200/25 px-4 py-2 text-sm font-semibold text-rose-100 transition hover:bg-rose-200/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Retry
            </button>
          </section>
        )}

        {report && (
          <div ref={resultsRef} className="mt-10 scroll-mt-6">
            <RiskReportView report={report} onCheckAnother={clearResults} />
          </div>
        )}

        <footer className="mt-12 border-t border-white/[0.07] pt-5 text-center">
          <p className="mx-auto max-w-3xl text-xs leading-5 text-slate-400">
            ScamLens AI gives a risk indicator, not a guarantee. Always verify offers through the company&apos;s official website.
          </p>
          <p className="mt-4 font-mono text-[10px] text-slate-600">Built for [hackathon] · ScamLens AI</p>
        </footer>
      </div>
    </main>
  );
}