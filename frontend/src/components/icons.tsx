interface IconProps {
  className?: string;
}

export function ShieldSearchIcon({ className }: IconProps) {
  return (
    <svg aria-hidden="true" className={className} viewBox="0 0 52 52" fill="none">
      <path d="M26 4 43 10v13c0 11.5-7 19.8-17 25C16 42.8 9 34.5 9 23V10l17-6Z" stroke="currentColor" strokeWidth="2.2" />
      <circle cx="24" cy="23" r="8" stroke="currentColor" strokeWidth="2.2" />
      <path d="m30 29 7 7" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" />
      <path d="M19 22h10M24 17v12" stroke="currentColor" strokeWidth="1.2" opacity=".48" />
    </svg>
  );
}

export function WarningIcon({ className }: IconProps) {
  return (
    <svg aria-hidden="true" className={className} viewBox="0 0 20 20" fill="none">
      <path d="M10 2.6 18 16.5H2L10 2.6Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
      <path d="M10 7v4.4M10 14.1h.01" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

export function ExternalLinkIcon({ className }: IconProps) {
  return (
    <svg aria-hidden="true" className={className} viewBox="0 0 16 16" fill="none">
      <path d="M9 2h5v5M14 2 7 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M12 9v4a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

export function CheckIcon({ className }: IconProps) {
  return (
    <svg aria-hidden="true" className={className} viewBox="0 0 20 20" fill="none">
      <path d="m4 10.5 4 4L16.5 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}