// Sigma2 Claude Cowork — Onboarding wizard (single-file JSX)
// Bokmål + English toggle, dark "infrastructure" aesthetic.

const { useState, useEffect, useMemo, useRef } = React;

/* ─── Copy dictionaries ───────────────────────────────────────── */
const COPY = {
  no: {
    appName: "Claude Cowork",
    org: "Sigma2",
    langLabel: "Språk",
    langNO: "Norsk",
    langEN: "English",
    skip: "Hopp over",
    next: "Neste",
    back: "Tilbake",
    finish: "Fullfør oppsett",
    step: "Steg",
    of: "av",

    // Step 1 — welcome
    s1Overline: "Velkommen til Cowork",
    s1Title: "Claude, koblet til Sigma2-systemene dine.",
    s1Lede:
      "Cowork lar deg snakke med Claude og samtidig slå opp data i Sigma2s interne systemer — fra MAS og RT til lønn, timer og regnskap. Du velger selv hvilke verktøy som skal være påskrudd.",
    s1Point1Title: "Du bestemmer tilgangen",
    s1Point1: "Skru verktøy av og på når som helst. Claude bruker bare det du har skrudd på.",
    s1Point2Title: "Din Sigma2-pålogging",
    s1Point2: "Vi bruker Feide-innlogging. Claude får ingen passord å se.",
    s1Point3Title: "Alt er sporbart",
    s1Point3: "Hvert oppslag logges i RT og kan revideres av IT.",
    s1Start: "Kom i gang",

    // Step 2 — identity
    s2Overline: "Steg 1 — Identifiser deg",
    s2Title: "Logg inn med Feide",
    s2Lede: "Vi henter navn, avdeling og roller fra LDAP slik at verktøyene vet hvem du er.",
    s2Btn: "Logg inn med Feide",
    s2Connected: "Tilkoblet som",
    s2Role: "Rolle",
    s2Dept: "Avdeling",

    // Step 3 — tools
    s3Overline: "Steg 2 — Velg verktøy",
    s3Title: "Hva skal Claude kunne gjøre?",
    s3Lede:
      "Skru på de verktøyene du bruker i det daglige. Du kan endre dette senere under Innstillinger.",
    s3AllOn: "Skru på alle",
    s3AllOff: "Skru av alle",
    s3Recommended: "Anbefalt for din rolle",
    s3Selected: "valgt",

    // Step 4 — confirm
    s4Overline: "Steg 3 — Bekreft",
    s4Title: "Klar til å starte",
    s4Lede:
      "Gjennomgå valgene dine. Du kan endre alt senere fra verktøylisten i Cowork.",
    s4Summary: "Oppsummering",
    s4You: "Deg",
    s4Tools: "Aktive verktøy",
    s4Rights: "Tilganger Claude får",
    s4RightsItem1: "Lese-tilgang til valgte systemer via din Feide-profil",
    s4RightsItem2: "Skriv-tilgang kun til UBW Agresso-bilag (når aktivert)",
    s4RightsItem3: "Alle kall logges automatisk i RT",
    s4LetsGo: "Åpne Cowork",

    // Step 5 — done
    s5Overline: "Ferdig",
    s5Title: "Oppsettet er lagret",
    s5Lede:
      "Cowork er klart. Still Claude et spørsmål for å se hvordan verktøyene dine svarer.",
    s5Try: "Prøv en eksempelprompt",
    s5Examples: "Eksempelprompter",
    s5Open: "Åpne Cowork",

    // Shared
    connect: "Koble til",
    connected: "Tilkoblet",
    on: "På",
    off: "Av",
    permissions: "Tilganger",
    whenActive: "Når aktivert",

    // Tool copy
    tools: {
      mas: {
        name: "MAS",
        tagline: "Slå opp i metadatasystemet og lenk data til prosjekter.",
        scope: "Lese: datasett, katalog, nøkler",
        who: "Forskningsstøtte, data-team",
      },
      rt: {
        name: "RT",
        tagline: "Les, kommenter og oppretter saker i Request Tracker.",
        scope: "Lese + kommentere tilkoblede køer",
        who: "Support, drift",
      },
      lonn: {
        name: "Lønn",
        tagline: "Oppslag i egen lønnsdata — lønnsslipp, feriepenger, skattetrekk.",
        scope: "Kun lesing av egne lønnsdata",
        who: "Alle ansatte",
      },
      timer: {
        name: "Timer",
        tagline: "Se og summer egne timer fra DFØ, per prosjekt og periode.",
        scope: "Lese egne timelister",
        who: "Alle ansatte",
      },
      regnskap: {
        name: "Regnskap",
        tagline: "Hent saldoer, transaksjoner og prosjektkostnader fra Agresso.",
        scope: "Lese regnskapsdata for prosjekter du har tilgang til",
        who: "Prosjektledere, økonomi",
      },
      ldap: {
        name: "LDAP",
        tagline: "Søk etter kolleger, avdelinger og roller.",
        scope: "Lese katalogoppføringer",
        who: "Alle ansatte",
      },
      agresso: {
        name: "UBW Agresso",
        tagline: "Generer og bokfør bilag i Agresso automatisk fra kvitteringer.",
        scope: "Skrive bokføringsbilag — krever ekstra bekreftelse per bilag",
        who: "Økonomi",
      },
    },

    // Example prompts
    prompts: [
      "Hvor mye har prosjekt «NIRD-utvidelse» brukt av budsjettet hittil i år?",
      "Finn alle RT-saker i køen «drift» som er eldre enn 7 dager.",
      "Bokfør denne kvitteringen på konto 6540, prosjekt 4021.",
      "Hva er feriepengegrunnlaget mitt for 2025?",
    ],
  },
  en: {
    appName: "Claude Cowork",
    org: "Sigma2",
    langLabel: "Language",
    langNO: "Norsk",
    langEN: "English",
    skip: "Skip",
    next: "Next",
    back: "Back",
    finish: "Finish setup",
    step: "Step",
    of: "of",

    s1Overline: "Welcome to Cowork",
    s1Title: "Claude, wired into your Sigma2 systems.",
    s1Lede:
      "Cowork lets you talk to Claude while it looks things up in Sigma2's internal systems — from MAS and RT to payroll, timesheets and accounting. You decide which tools are active.",
    s1Point1Title: "You control access",
    s1Point1: "Toggle tools on and off whenever you like. Claude only uses what's on.",
    s1Point2Title: "Your Sigma2 login",
    s1Point2: "We sign you in via Feide. Claude never sees your password.",
    s1Point3Title: "Everything is auditable",
    s1Point3: "Each lookup is logged in RT and reviewable by IT.",
    s1Start: "Get started",

    s2Overline: "Step 1 — Identify yourself",
    s2Title: "Sign in with Feide",
    s2Lede: "We read your name, department and roles from LDAP so the tools know who you are.",
    s2Btn: "Sign in with Feide",
    s2Connected: "Signed in as",
    s2Role: "Role",
    s2Dept: "Department",

    s3Overline: "Step 2 — Pick your tools",
    s3Title: "What should Claude be able to do?",
    s3Lede:
      "Turn on the tools you use day-to-day. You can change this later from Settings.",
    s3AllOn: "Turn all on",
    s3AllOff: "Turn all off",
    s3Recommended: "Recommended for your role",
    s3Selected: "selected",

    s4Overline: "Step 3 — Confirm",
    s4Title: "Ready to go",
    s4Lede:
      "Review your choices. You can change everything later from the tool list in Cowork.",
    s4Summary: "Summary",
    s4You: "You",
    s4Tools: "Active tools",
    s4Rights: "What Claude can do",
    s4RightsItem1: "Read access to selected systems via your Feide profile",
    s4RightsItem2: "Write access only to UBW Agresso vouchers (when active)",
    s4RightsItem3: "Every call is automatically logged in RT",
    s4LetsGo: "Open Cowork",

    s5Overline: "Done",
    s5Title: "Your setup is saved",
    s5Lede:
      "Cowork is ready. Ask Claude a question to see how your tools respond.",
    s5Try: "Try an example prompt",
    s5Examples: "Example prompts",
    s5Open: "Open Cowork",

    connect: "Connect",
    connected: "Connected",
    on: "On",
    off: "Off",
    permissions: "Permissions",
    whenActive: "When active",

    tools: {
      mas: {
        name: "MAS",
        tagline: "Look up the metadata system and link records to projects.",
        scope: "Read: datasets, catalogue, keys",
        who: "Research support, data teams",
      },
      rt: {
        name: "RT",
        tagline: "Read, comment on and open tickets in Request Tracker.",
        scope: "Read and comment on connected queues",
        who: "Support, operations",
      },
      lonn: {
        name: "Payroll",
        tagline: "Look up your own payroll data — payslip, holiday pay, tax.",
        scope: "Read your own payroll data only",
        who: "Everyone",
      },
      timer: {
        name: "Timesheets",
        tagline: "See and sum your hours in DFØ, by project and period.",
        scope: "Read your own timesheets",
        who: "Everyone",
      },
      regnskap: {
        name: "Accounting",
        tagline: "Pull balances, transactions and project costs from Agresso.",
        scope: "Read accounting data for projects you can access",
        who: "Project leads, finance",
      },
      ldap: {
        name: "LDAP",
        tagline: "Search for colleagues, departments and roles.",
        scope: "Read directory entries",
        who: "Everyone",
      },
      agresso: {
        name: "UBW Agresso",
        tagline: "Generate and post vouchers in Agresso from receipts, automatically.",
        scope: "Write vouchers — requires per-voucher confirmation",
        who: "Finance",
      },
    },

    prompts: [
      "How much of project \"NIRD expansion\"'s budget has been used this year?",
      "Find all RT tickets in the 'ops' queue older than 7 days.",
      "Post this receipt to account 6540, project 4021.",
      "What's my holiday-pay base for 2025?",
    ],
  },
};

/* ─── Tools list (stable order) ───────────────────────────────── */
const TOOL_IDS = ["ldap", "mas", "rt", "timer", "lonn", "regnskap", "agresso"];

/* Icons — hand-drawn SVG, 4px-stroke circle/line motif from manual.
   24x24 grid, stroke-based, round caps/joins. */
const toolIcon = (id) => {
  const props = {
    width: 28,
    height: 28,
    viewBox: "0 0 28 28",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 2,
    strokeLinecap: "round",
    strokeLinejoin: "round",
  };
  switch (id) {
    case "ldap":
      return (
        <svg {...props}>
          <circle cx="14" cy="9" r="3.5" />
          <circle cx="6.5" cy="19" r="2.5" />
          <circle cx="21.5" cy="19" r="2.5" />
          <path d="M14 12.5V16M14 16l-6 2M14 16l6 2" />
        </svg>
      );
    case "mas":
      return (
        <svg {...props}>
          <path d="M4 8.5C4 7 5 6 6.5 6h3l2 2H21.5C23 8 24 9 24 10.5v9C24 21 23 22 21.5 22h-15C5 22 4 21 4 19.5v-11z" />
          <path d="M8 12h12M8 16h8" />
        </svg>
      );
    case "rt":
      return (
        <svg {...props}>
          <path d="M5 7h18v12c0 1-.8 2-2 2H7c-1.2 0-2-1-2-2V7z" />
          <path d="M5 7l9 7 9-7" />
          <circle cx="22" cy="7" r="3" fill="currentColor" stroke="none" />
        </svg>
      );
    case "timer":
      return (
        <svg {...props}>
          <circle cx="14" cy="14.5" r="8.5" />
          <path d="M14 9v5.5l3.5 2" />
          <path d="M10 3h8" />
        </svg>
      );
    case "lonn":
      return (
        <svg {...props}>
          <rect x="3.5" y="7" width="21" height="13" rx="2" />
          <circle cx="14" cy="13.5" r="3" />
          <path d="M7 13.5h.01M21 13.5h.01" />
        </svg>
      );
    case "regnskap":
      return (
        <svg {...props}>
          <path d="M5 22V8l9-4 9 4v14" />
          <path d="M5 22h18" />
          <path d="M10 22v-7h8v7" />
        </svg>
      );
    case "agresso":
      return (
        <svg {...props}>
          <rect x="5" y="3.5" width="18" height="21" rx="2" />
          <path d="M9 9h10M9 13h10M9 17h6" />
          <circle cx="19.5" cy="18" r="3" fill="var(--s2-coral-100)" stroke="none" />
          <path d="M18.3 18l.9.9 1.8-1.8" stroke="#fff" strokeWidth="1.6" />
        </svg>
      );
  }
};

/* ─── Sigma2 mark ─────────────────────────────────────────────── */
const Sigma2Mark = ({ color = "currentColor" }) => (
  <svg width="36" height="36" viewBox="0 0 36 36" fill="none" aria-hidden>
    <circle cx="18" cy="18" r="15" stroke={color} strokeWidth="3" />
    <path
      d="M12 13c0-2 1.5-3.5 4-3.5s4 1.5 4 3.5c0 2-1.5 3-4 4.5-2.5 1.5-4 2.5-4 4.5 0 2 1.5 3.5 4 3.5s4-1.5 4-3.5"
      stroke={color}
      strokeWidth="3"
      strokeLinecap="round"
      strokeLinejoin="round"
      fill="none"
    />
  </svg>
);

/* ─── Toggle switch ──────────────────────────────────────────── */
const Toggle = ({ on, onChange, label }) => (
  <button
    role="switch"
    aria-checked={on}
    aria-label={label}
    onClick={() => onChange(!on)}
    className={`s2-toggle ${on ? "on" : "off"}`}
  >
    <span className="s2-toggle-knob" />
  </button>
);

/* ─── Progress bar / steps ───────────────────────────────────── */
const StepBar = ({ step, total, labels, theme, onJump }) => (
  <div className="s2-stepbar" data-theme={theme}>
    {labels.map((l, i) => {
      const state = i < step ? "done" : i === step ? "active" : "todo";
      const clickable = state === "done";
      return (
        <div
          key={i}
          className={`s2-step ${state}`}
          role={clickable ? "button" : undefined}
          tabIndex={clickable ? 0 : -1}
          onClick={() => clickable && onJump && onJump(i + 1)}
          onKeyDown={(e) => { if (clickable && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); onJump && onJump(i + 1); } }}
          title={clickable ? l : undefined}
        >
          <div className="s2-step-dot">
            {state === "done" ? (
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M3 7l3 3 5-6" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            ) : (
              <span>{i + 1}</span>
            )}
          </div>
          <span className="s2-step-label">{l}</span>
          {i < labels.length - 1 && <div className="s2-step-line" />}
        </div>
      );
    })}
  </div>
);

/* ─── Decorative circle/line motif ───────────────────────────── */
const CircleLineMotif = ({ variant = "a" }) => {
  if (variant === "a") {
    return (
      <svg className="s2-motif motif-a" viewBox="0 0 320 320" fill="none" aria-hidden>
        <circle cx="160" cy="160" r="140" stroke="currentColor" strokeWidth="4" />
        <circle cx="160" cy="160" r="90" stroke="currentColor" strokeWidth="4" />
        <path d="M20 160 H300" stroke="currentColor" strokeWidth="4" />
        <path d="M160 20 V300" stroke="currentColor" strokeWidth="4" />
      </svg>
    );
  }
  return (
    <svg className="s2-motif motif-b" viewBox="0 0 260 260" fill="none" aria-hidden>
      <circle cx="130" cy="130" r="110" stroke="currentColor" strokeWidth="4" />
      <path d="M20 130 H240" stroke="currentColor" strokeWidth="4" />
    </svg>
  );
};

/* ─── Steps ──────────────────────────────────────────────────── */
function StepWelcome({ t, onNext, theme }) {
  return (
    <div className="s2-step-welcome">
      <div className="s2-welcome-left">
        <div className="s2-overline s2-accent">{t.s1Overline}</div>
        <h1 className="s2-h1 s2-title">{t.s1Title}</h1>
        <p className="s2-p s2-lede">{t.s1Lede}</p>

        <div className="s2-points">
          <Point num="01" title={t.s1Point1Title} body={t.s1Point1} />
          <Point num="02" title={t.s1Point2Title} body={t.s1Point2} />
          <Point num="03" title={t.s1Point3Title} body={t.s1Point3} />
        </div>

        <div className="s2-actions">
          <button className="s2-btn s2-btn-primary" onClick={onNext}>
            {t.s1Start}
            <ArrowRight />
          </button>
        </div>
      </div>

      <div className="s2-welcome-right">
        <HeroCard t={t} theme={theme} />
      </div>
    </div>
  );
}

const Point = ({ num, title, body }) => (
  <div className="s2-point">
    <div className="s2-point-num">{num}</div>
    <div>
      <div className="s2-point-title">{title}</div>
      <div className="s2-point-body">{body}</div>
    </div>
  </div>
);

const ArrowRight = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden>
    <path d="M3 9h12M10 4l5 5-5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);
const ArrowLeft = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden>
    <path d="M15 9H3M8 4L3 9l5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

/* Hero chat preview — feels like Cowork */
function HeroCard({ t, theme }) {
  return (
    <div className="s2-hero-card">
      <CircleLineMotif variant="a" />
      <div className="s2-hero-chat">
        <div className="s2-chat-row user">
          <div className="s2-chat-bubble user">
            {t === COPY.no
              ? "Hei Claude, hvor mange timer har jeg ført på prosjekt 4021 i april?"
              : "Hey Claude, how many hours have I logged on project 4021 in April?"}
          </div>
        </div>

        <div className="s2-chat-row claude">
          <div className="s2-chat-tool">
            <div className="s2-chat-tool-head">
              <span className="s2-chat-tool-dot" />
              <span className="s2-chat-tool-name">
                {t === COPY.no ? "Bruker verktøy" : "Using tool"} · Timer
              </span>
              <span className="s2-chat-tool-status">
                {t === COPY.no ? "Fullført" : "Done"}
              </span>
            </div>
            <div className="s2-chat-tool-body s2-mono">
              <span className="dim">get_timesheet</span>
              {"({ project: 4021, period: \"2026-04\" })"}
            </div>
          </div>

          <div className="s2-chat-bubble claude">
            {t === COPY.no
              ? "Du har ført 42,5 timer på prosjekt 4021 i april. Tre dager mangler utfylling — vil du at jeg lager et RT-minne?"
              : "You've logged 42.5 hours on project 4021 in April. Three days are missing — want me to open an RT reminder?"}
          </div>
        </div>
      </div>
    </div>
  );
}

/* Step 2 — Feide login */
function StepIdentity({ t, user, setUser, onNext, onBack }) {
  const [loading, setLoading] = useState(false);
  const connect = () => {
    setLoading(true);
    setTimeout(() => {
      setUser({
        name: "Ingrid Solberg",
        mail: "ingrid.solberg@sigma2.no",
        dept: "Forskningsstøtte",
        role: "Senior rådgiver",
        initials: "IS",
      });
      setLoading(false);
    }, 900);
  };
  return (
    <div className="s2-card-step">
      <div className="s2-overline s2-accent">{t.s2Overline}</div>
      <h2 className="s2-h2 s2-title-sm">{t.s2Title}</h2>
      <p className="s2-p s2-lede">{t.s2Lede}</p>

      <div className="s2-identity">
        {!user ? (
          <button
            className={`s2-feide-btn ${loading ? "loading" : ""}`}
            onClick={connect}
            disabled={loading}
          >
            <FeideGlyph />
            <span>{loading ? (t === COPY.no ? "Logger inn…" : "Signing in…") : t.s2Btn}</span>
          </button>
        ) : (
          <div className="s2-identity-card">
            <div className="s2-avatar">{user.initials}</div>
            <div className="s2-identity-meta">
              <div className="s2-identity-name">{user.name}</div>
              <div className="s2-identity-mail">{user.mail}</div>
              <div className="s2-identity-kv">
                <div>
                  <span className="k">{t.s2Role}</span>
                  <span className="v">{user.role}</span>
                </div>
                <div>
                  <span className="k">{t.s2Dept}</span>
                  <span className="v">{user.dept}</span>
                </div>
              </div>
            </div>
            <div className="s2-identity-badge">
              <Dot /> {t.s2Connected.replace(/ som$/, "").replace(/ as$/, "")}
            </div>
          </div>
        )}

        <div className="s2-identity-note s2-small">
          {t === COPY.no
            ? "Vi henter profilen din via Feide → LDAP. Passordet forlater aldri påloggingsvinduet."
            : "Your profile is read via Feide → LDAP. Your password never leaves the sign-in window."}
        </div>
      </div>

      <NavRow t={t} onNext={onNext} onBack={onBack} nextDisabled={!user} />
    </div>
  );
}

const FeideGlyph = () => (
  <svg width="22" height="22" viewBox="0 0 22 22" fill="none" aria-hidden>
    <circle cx="11" cy="11" r="10" fill="#EF4444" />
    <path d="M6 9h10M6 13h7" stroke="#fff" strokeWidth="2" strokeLinecap="round" />
  </svg>
);

const Dot = () => (
  <span
    style={{
      display: "inline-block",
      width: 8,
      height: 8,
      borderRadius: "50%",
      background: "#38D28C",
      boxShadow: "0 0 0 3px rgba(56,210,140,0.18)",
      marginRight: 8,
    }}
  />
);

/* Step 3 — tool selection */
function StepTools({ t, enabled, setEnabled, onNext, onBack, lang }) {
  const recommended = useMemo(() => ["ldap", "timer", "lonn", "rt"], []);
  const list = TOOL_IDS;
  const allOn = list.every((id) => enabled[id]);

  const setAll = (v) => {
    const next = {};
    list.forEach((id) => (next[id] = v));
    setEnabled(next);
  };

  const count = list.filter((id) => enabled[id]).length;

  return (
    <div className="s2-card-step tools-step">
      <div className="s2-tools-head">
        <div>
          <div className="s2-overline s2-accent">{t.s3Overline}</div>
          <h2 className="s2-h2 s2-title-sm">{t.s3Title}</h2>
          <p className="s2-p s2-lede">{t.s3Lede}</p>
        </div>
        <div className="s2-tools-head-right">
          <span className="s2-selected-count">
            <strong>{count}</strong>/{list.length} {t.s3Selected}
          </span>
          <button className="s2-btn-ghost s2-link" onClick={() => setAll(!allOn)}>
            {allOn ? t.s3AllOff : t.s3AllOn}
          </button>
        </div>
      </div>

      <div className="s2-tool-grid">
        {list.map((id) => {
          const info = t.tools[id];
          const on = !!enabled[id];
          const rec = recommended.includes(id);
          return (
            <article
              key={id}
              className={`s2-tool-card ${on ? "on" : ""}`}
              onClick={() => setEnabled({ ...enabled, [id]: !on })}
            >
              <div className="s2-tool-top">
                <div className={`s2-tool-icon tool-${id}`}>{toolIcon(id)}</div>
                <Toggle
                  on={on}
                  onChange={(v) => setEnabled({ ...enabled, [id]: v })}
                  label={info.name}
                />
              </div>
              <div className="s2-tool-body">
                <div className="s2-tool-name-row">
                  <h3 className="s2-h5 s2-tool-name">{info.name}</h3>
                  {rec && (
                    <span className="s2-tool-rec" title={t.s3Recommended}>
                      <Star />
                      <span>{lang === "no" ? "Anbefalt" : "Recommended"}</span>
                    </span>
                  )}
                </div>
                <p className="s2-tool-tag">{info.tagline}</p>
                <div className="s2-tool-scope s2-small">
                  <Lock />
                  <span>{info.scope}</span>
                </div>
              </div>
              <div className="s2-tool-corner" />
            </article>
          );
        })}
      </div>

      <NavRow t={t} onNext={onNext} onBack={onBack} />
    </div>
  );
}

const Star = () => (
  <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor" aria-hidden>
    <path d="M6 .8l1.6 3.2 3.5.5-2.55 2.5.6 3.5L6 8.9 2.85 10.5l.6-3.5L.9 4.5l3.5-.5L6 .8z" />
  </svg>
);
const Lock = () => (
  <svg width="12" height="12" viewBox="0 0 14 14" fill="none" aria-hidden>
    <rect x="2.5" y="6" width="9" height="6.5" rx="1.5" stroke="currentColor" strokeWidth="1.3" />
    <path d="M4.5 6V4.5a2.5 2.5 0 015 0V6" stroke="currentColor" strokeWidth="1.3" />
  </svg>
);

/* Step 4 — confirm */
function StepConfirm({ t, user, enabled, onNext, onBack, lang }) {
  const active = TOOL_IDS.filter((id) => enabled[id]);
  return (
    <div className="s2-card-step">
      <div className="s2-overline s2-accent">{t.s4Overline}</div>
      <h2 className="s2-h2 s2-title-sm">{t.s4Title}</h2>
      <p className="s2-p s2-lede">{t.s4Lede}</p>

      <div className="s2-summary">
        <div className="s2-summary-col">
          <div className="s2-overline muted">{t.s4You}</div>
          {user && (
            <div className="s2-summary-user">
              <div className="s2-avatar sm">{user.initials}</div>
              <div>
                <div className="s2-summary-name">{user.name}</div>
                <div className="s2-summary-sub">{user.role} · {user.dept}</div>
              </div>
            </div>
          )}

          <div className="s2-overline muted" style={{ marginTop: 28 }}>{t.s4Rights}</div>
          <ul className="s2-rights">
            <li>{t.s4RightsItem1}</li>
            <li>{t.s4RightsItem2}</li>
            <li>{t.s4RightsItem3}</li>
          </ul>
        </div>

        <div className="s2-summary-col">
          <div className="s2-overline muted">
            {t.s4Tools} <span className="s2-count-chip">{active.length}</span>
          </div>
          <ul className="s2-active-tools">
            {active.map((id) => (
              <li key={id}>
                <span className={`s2-tool-icon-sm tool-${id}`}>{toolIcon(id)}</span>
                <div>
                  <div className="s2-active-name">{t.tools[id].name}</div>
                  <div className="s2-active-scope s2-small">{t.tools[id].scope}</div>
                </div>
              </li>
            ))}
            {active.length === 0 && (
              <li className="s2-empty">{lang === "no" ? "Ingen verktøy valgt" : "No tools selected"}</li>
            )}
          </ul>
        </div>
      </div>

      <NavRow t={t} onBack={onBack} onNext={onNext} nextLabel={t.s4LetsGo} />
    </div>
  );
}

/* Step 5 — done */
function StepDone({ t, enabled, lang, onBack }) {
  const [promptIdx, setPromptIdx] = useState(0);
  const active = TOOL_IDS.filter((id) => enabled[id]);
  return (
    <div className="s2-card-step done">
      <div className="s2-done-top">
        <div className="s2-done-check">
          <svg width="44" height="44" viewBox="0 0 44 44" fill="none">
            <circle cx="22" cy="22" r="20" stroke="currentColor" strokeWidth="3" />
            <path d="M13 22l6 6 13-13" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        <div className="s2-overline s2-accent">{t.s5Overline}</div>
        <h2 className="s2-h2 s2-title-sm">{t.s5Title}</h2>
        <p className="s2-p s2-lede">{t.s5Lede}</p>
      </div>

      <div className="s2-done-examples">
        <div className="s2-overline muted">{t.s5Examples}</div>
        <div className="s2-prompt-list">
          {t.prompts.map((p, i) => (
            <button
              key={i}
              className={`s2-prompt-chip ${promptIdx === i ? "on" : ""}`}
              onClick={() => setPromptIdx(i)}
            >
              <span className="s2-prompt-chip-num">0{i + 1}</span>
              <span>{p}</span>
            </button>
          ))}
        </div>

        <div className="s2-done-active">
          <div className="s2-overline muted">
            {t.s4Tools} · {active.length}
          </div>
          <div className="s2-done-chips">
            {active.map((id) => (
              <span key={id} className={`s2-done-chip tool-${id}`}>
                <span className={`s2-tool-icon-sm tool-${id}`}>{toolIcon(id)}</span>
                {t.tools[id].name}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="s2-actions center" style={{ gap: 16 }}>
        <button className="s2-btn-ghost s2-nav-back" onClick={onBack}>
          <ArrowLeft /> {t.back}
        </button>
        <button className="s2-btn s2-btn-primary lg">
          {t.s5Open}
          <ArrowRight />
        </button>
      </div>
    </div>
  );
}

/* Nav */
function NavRow({ t, onBack, onNext, nextDisabled, nextLabel }) {
  return (
    <div className="s2-nav-row">
      {onBack ? (
        <button className="s2-btn-ghost s2-nav-back" onClick={onBack}>
          <ArrowLeft /> {t.back}
        </button>
      ) : <span />}
      <div className="s2-nav-right">
        <button
          className="s2-btn s2-btn-primary"
          onClick={onNext}
          disabled={nextDisabled}
        >
          {nextLabel || t.next}
          <ArrowRight />
        </button>
      </div>
    </div>
  );
}

/* ─── Root app ───────────────────────────────────────────────── */
function App() {
  // Tweakable defaults block — edited by the host
  const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
    "theme": "dark",
    "language": "no"
  }/*EDITMODE-END*/;

  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("s2.theme") || TWEAK_DEFAULTS.theme;
  });
  const [lang, setLang] = useState(() => {
    return localStorage.getItem("s2.lang") || TWEAK_DEFAULTS.language;
  });
  const [step, setStep] = useState(() => {
    const s = parseInt(localStorage.getItem("s2.step") || "0", 10);
    return isNaN(s) ? 0 : s;
  });
  const [user, setUser] = useState(null);
  const [enabled, setEnabled] = useState(() => {
    try {
      const saved = JSON.parse(localStorage.getItem("s2.enabled") || "null");
      if (saved) return saved;
    } catch {}
    return { ldap: true, timer: true, lonn: true, rt: false, mas: false, regnskap: false, agresso: false };
  });

  useEffect(() => { localStorage.setItem("s2.step", String(step)); }, [step]);
  useEffect(() => { localStorage.setItem("s2.enabled", JSON.stringify(enabled)); }, [enabled]);
  useEffect(() => { localStorage.setItem("s2.theme", theme); }, [theme]);
  useEffect(() => { localStorage.setItem("s2.lang", lang); }, [lang]);

  // Tweaks panel wiring
  const [tweaksOpen, setTweaksOpen] = useState(false);
  useEffect(() => {
    const onMsg = (e) => {
      const d = e.data;
      if (!d || !d.type) return;
      if (d.type === "__activate_edit_mode") setTweaksOpen(true);
      if (d.type === "__deactivate_edit_mode") setTweaksOpen(false);
    };
    window.addEventListener("message", onMsg);
    // Announce availability AFTER listener is registered
    window.parent.postMessage({ type: "__edit_mode_available" }, "*");
    return () => window.removeEventListener("message", onMsg);
  }, []);

  const persistTweak = (patch) => {
    window.parent.postMessage({ type: "__edit_mode_set_keys", edits: patch }, "*");
  };

  const t = COPY[lang];

  const stepLabels = [
    lang === "no" ? "Velkommen" : "Welcome",
    lang === "no" ? "Identitet" : "Identity",
    lang === "no" ? "Verktøy" : "Tools",
    lang === "no" ? "Bekreft" : "Confirm",
    lang === "no" ? "Ferdig" : "Done",
  ];

  // If page is reloaded and user is null but step > 1, drop a plausible user
  useEffect(() => {
    if (!user && step > 1) {
      setUser({
        name: "Ingrid Solberg",
        mail: "ingrid.solberg@sigma2.no",
        dept: lang === "no" ? "Forskningsstøtte" : "Research support",
        role: lang === "no" ? "Senior rådgiver" : "Senior advisor",
        initials: "IS",
      });
    }
  }, [step]); // eslint-disable-line

  return (
    <div className={`s2-app theme-${theme}`} data-theme={theme}>
      {/* Background circles motif */}
      <div className="s2-bg-motif" aria-hidden>
        <svg viewBox="0 0 1600 900" preserveAspectRatio="xMaxYMin slice">
          <circle cx="1480" cy="80" r="320" stroke="currentColor" strokeWidth="4" fill="none" />
          <circle cx="1480" cy="80" r="200" stroke="currentColor" strokeWidth="4" fill="none" />
          <path d="M60 800 H 1540" stroke="currentColor" strokeWidth="4" />
          <circle cx="120" cy="820" r="6" fill="currentColor" />
          <circle cx="260" cy="820" r="20" stroke="currentColor" strokeWidth="4" fill="none" />
        </svg>
      </div>

      {/* Top bar */}
      <header className="s2-topbar">
        <div className="s2-brand">
          <Sigma2Mark />
          <div className="s2-brand-text">
            <div className="s2-brand-org">{t.org}</div>
            <div className="s2-brand-app">{t.appName}</div>
          </div>
        </div>

        <div className="s2-top-right">
          <div className="s2-lang-toggle" role="tablist" aria-label={t.langLabel}>
            <button
              role="tab"
              aria-selected={lang === "no"}
              onClick={() => setLang("no")}
              className={lang === "no" ? "on" : ""}
            >
              NO
            </button>
            <button
              role="tab"
              aria-selected={lang === "en"}
              onClick={() => setLang("en")}
              className={lang === "en" ? "on" : ""}
            >
              EN
            </button>
          </div>
          {step > 0 && step < 4 && (
            <button
              className="s2-btn-ghost s2-skip"
              onClick={() => setStep(4)}
              title={t.skip}
            >
              {t.skip}
            </button>
          )}
        </div>
      </header>

      {/* Step bar */}
      {step > 0 && (
        <StepBar
          step={step - 1}
          total={4}
          labels={stepLabels.slice(1)}
          theme={theme}
          onJump={(n) => setStep(n)}
        />
      )}

      {/* Main */}
      <main className="s2-main">
        {step === 0 && <StepWelcome t={t} theme={theme} onNext={() => setStep(1)} />}
        {step === 1 && (
          <StepIdentity
            t={t}
            user={user}
            setUser={setUser}
            onNext={() => setStep(2)}
            onBack={() => setStep(0)}
          />
        )}
        {step === 2 && (
          <StepTools
            t={t}
            lang={lang}
            enabled={enabled}
            setEnabled={setEnabled}
            onNext={() => setStep(3)}
            onBack={() => setStep(1)}
          />
        )}
        {step === 3 && (
          <StepConfirm
            t={t}
            user={user}
            enabled={enabled}
            lang={lang}
            onNext={() => setStep(4)}
            onBack={() => setStep(2)}
          />
        )}
        {step === 4 && <StepDone t={t} enabled={enabled} lang={lang} onBack={() => setStep(3)} />}
      </main>

      {/* Footer / meta */}
      <footer className="s2-footer">
        <div className="s2-footer-left s2-small">
          {t.step} <strong>{step + 1}</strong> {t.of} 5 · {t.appName}
        </div>
        <div className="s2-footer-right s2-small">
          {lang === "no"
            ? "Bygget for Sigma2-ansatte · Alle oppslag logges"
            : "Built for Sigma2 staff · All lookups are logged"}
        </div>
      </footer>

      {/* Tweaks panel */}
      {tweaksOpen && (
        <aside className="s2-tweaks">
          <div className="s2-tweaks-head">
            <strong>Tweaks</strong>
            <button className="s2-tweaks-close" onClick={() => setTweaksOpen(false)} aria-label="Close">×</button>
          </div>
          <div className="s2-tweaks-row">
            <label className="s2-overline muted">Bakgrunn / Theme</label>
            <div className="s2-seg">
              <button
                className={theme === "dark" ? "on" : ""}
                onClick={() => { setTheme("dark"); persistTweak({ theme: "dark" }); }}
              >
                Mørk · Dark
              </button>
              <button
                className={theme === "light" ? "on" : ""}
                onClick={() => { setTheme("light"); persistTweak({ theme: "light" }); }}
              >
                Lys · Light
              </button>
            </div>
          </div>

          <div className="s2-tweaks-row">
            <label className="s2-overline muted">Språk / Language</label>
            <div className="s2-seg">
              <button
                className={lang === "no" ? "on" : ""}
                onClick={() => { setLang("no"); persistTweak({ language: "no" }); }}
              >
                Norsk
              </button>
              <button
                className={lang === "en" ? "on" : ""}
                onClick={() => { setLang("en"); persistTweak({ language: "en" }); }}
              >
                English
              </button>
            </div>
          </div>

          <div className="s2-tweaks-row">
            <label className="s2-overline muted">Start på nytt</label>
            <button
              className="s2-btn-ghost s2-link"
              onClick={() => {
                setStep(0);
                setUser(null);
                setEnabled({ ldap: true, timer: true, lonn: true, rt: false, mas: false, regnskap: false, agresso: false });
              }}
            >
              ↺ Nullstill onboarding
            </button>
          </div>
        </aside>
      )}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
