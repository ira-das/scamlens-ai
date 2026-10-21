interface OfferFormProps {
  text: string;
  loading: boolean;
  onTextChange: (value: string) => void;
  onSubmit: () => void;
}

const scamExample = "Urgent internship opening! We need a ₹5000 security deposit before onboarding.\nEmail hr@internship-portal.xyz and contact me on WhatsApp immediately.\nRegards, Priya Sharma\nNo interview needed. Submit Aadhaar and OTP.";

const genuineExample = "TCS internship opportunity in software development.\nOfficial domain: tcs.com\nStipend ₹18000 per month.\nLocation: Bengaluru.\nNo fee required.";

export default function OfferForm({ text, loading, onTextChange, onSubmit }: OfferFormProps) {
  return (
    <form
      id="offer-form"
      className="glass-panel rounded-2xl border border-white/10 p-4 shadow-[0_24px_90px_-52px_rgba(34,211,238,0.32)] sm:p-6"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <label htmlFor="offer-text" className="block text-sm font-semibold text-slate-100">
            Offer message
          </label>
          <p className="mt-1 text-xs text-slate-400">Paste the complete message for a clearer assessment.</p>
        </div>
        <span className="font-mono text-xs tabular-nums text-slate-400" aria-live="polite">
          {text.length.toLocaleString()} characters
        </span>
      </div>

      <textarea
        id="offer-text"
        value={text}
        onChange={(event) => onTextChange(event.target.value)}
        placeholder="Paste the internship or job offer message here..."
        rows={7}
        className="min-h-48 w-full resize-y rounded-xl border border-white/10 bg-slate-950/60 px-4 py-4 text-sm leading-7 text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-cyan-300/60 focus:ring-4 focus:ring-cyan-300/10"
      />

      <div className="mt-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => onTextChange(scamExample)}
            disabled={loading}
            className="rounded-lg border border-rose-300/20 bg-rose-300/[0.04] px-3 py-2 text-xs font-medium text-slate-300 transition hover:border-rose-300/45 hover:bg-rose-300/[0.08] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Try a scam example
          </button>
          <button
            type="button"
            onClick={() => onTextChange(genuineExample)}
            disabled={loading}
            className="rounded-lg border border-emerald-300/20 bg-emerald-300/[0.04] px-3 py-2 text-xs font-medium text-slate-300 transition hover:border-emerald-300/45 hover:bg-emerald-300/[0.08] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Try a genuine example
          </button>
        </div>

        <button
          type="submit"
          disabled={!text.trim() || loading}
          className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-400 via-sky-500 to-blue-600 px-5 text-sm font-bold text-slate-950 shadow-[0_10px_32px_-12px_rgba(34,211,238,0.65)] transition hover:-translate-y-0.5 hover:shadow-[0_14px_38px_-12px_rgba(56,189,248,0.78)] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-cyan-200/40 disabled:translate-y-0 disabled:cursor-not-allowed disabled:opacity-45 disabled:shadow-none sm:w-auto"
        >
          {loading && <span aria-hidden="true" className="size-4 animate-spin rounded-full border-2 border-slate-900/30 border-t-slate-950" />}
          {loading ? "Analyzing..." : "Check Offer"}
          {!loading && <span aria-hidden="true" className="text-base leading-none">→</span>}
        </button>
      </div>
    </form>
  );
}