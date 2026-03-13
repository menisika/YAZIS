import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Search, GitBranch, ArrowRight } from "lucide-react";
import { usePatternSearch } from "@/api/hooks";
import { PageHeader } from "@/components/ui/PageHeader";
import { posColor } from "@/lib/utils";
import { getDepEntry, getPosEntry } from "@/lib/linguisticGlossary";
import type { PatternMatch } from "@/types";

const POS_OPTIONS = ["NOUN", "VERB", "ADJ", "ADV", "PRON", "DET", "ADP", "CCONJ", "SCONJ", "PROPN", "NUM", "AUX"];

const DEP_OPTIONS = [
  "nsubj", "nsubjpass", "dobj", "iobj", "pobj", "amod", "advmod", "attr",
  "prep", "relcl", "advcl", "ccomp", "xcomp", "acl", "acomp",
  "nmod", "compound", "det", "aux", "cop", "mark", "case", "cc", "conj",
  "ROOT", "appos", "nummod", "neg", "expl", "poss",
];

interface SelectOption {
  value: string;
  label: string;
}

const POS_SELECT_OPTIONS: SelectOption[] = POS_OPTIONS.map((code) => ({
  value: code,
  label: `${getPosEntry(code).label} (${code})`,
}));

const DEP_SELECT_OPTIONS: SelectOption[] = DEP_OPTIONS.map((code) => ({
  value: code,
  label: `${getDepEntry(code).label} (${code})`,
}));

const PRESET_PATTERNS = [
  { label: "Subject → Verb", source_pos: "NOUN", dep_rel: "nsubj", target_pos: "VERB" },
  { label: "Verb → Object", source_pos: "VERB", dep_rel: "dobj", target_pos: "NOUN" },
  { label: "Adjective modifies Noun", source_pos: "NOUN", dep_rel: "amod", target_pos: "ADJ" },
  { label: "Adverb modifies Verb", source_pos: "VERB", dep_rel: "advmod", target_pos: "ADV" },
  { label: "Relative clause on Noun", source_pos: "NOUN", dep_rel: "relcl", target_pos: "VERB" },
];

function highlightSentence(text: string, sourceText: string, targetText: string): React.ReactNode {
  const parts: React.ReactNode[] = [];
  let remaining = text;
  const highlights = [
    { word: sourceText, color: "#5c6bc0" },
    { word: targetText, color: "#22c55e" },
  ].filter((h) => h.word);

  const regex = new RegExp(
    `(${highlights.map((h) => h.word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")})`,
    "g",
  );

  const splitParts = remaining.split(regex);
  splitParts.forEach((part, i) => {
    const match = highlights.find((h) => h.word === part);
    if (match) {
      parts.push(
        <mark
          key={i}
          style={{
            background: match.color + "33",
            color: match.color,
            fontWeight: 600,
            borderRadius: 3,
            padding: "0 2px",
          }}
        >
          {part}
        </mark>,
      );
    } else {
      parts.push(part);
    }
  });
  return parts;
}

export function PatternSearchPage() {
  const navigate = useNavigate();
  const patternSearch = usePatternSearch();

  const [sourcePos, setSourcePos] = useState("NOUN");
  const [depRel, setDepRel] = useState("nsubj");
  const [targetPos, setTargetPos] = useState("VERB");

  function handleSearch() {
    patternSearch.mutate({ source_pos: sourcePos, dep_rel: depRel, target_pos: targetPos });
  }

  function applyPreset(p: (typeof PRESET_PATTERNS)[0]) {
    setSourcePos(p.source_pos);
    setDepRel(p.dep_rel);
    setTargetPos(p.target_pos);
  }

  return (
    <div style={{ padding: 32, maxWidth: 900, margin: "0 auto" }}>
      <PageHeader
        title="Pattern Search"
        subtitle="Find sentences matching a grammatical structure across the entire corpus"
      />

      {/* Pattern builder */}
      <div className="card" style={{ padding: 20, marginBottom: 20 }}>
        <p style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 14 }}>
          Find: where a token with part of speech <strong>{getPosEntry(sourcePos).label}</strong> ({sourcePos}) is the head of a token with dependency{" "}
          <strong>{getDepEntry(depRel).label}</strong> ({depRel}) and part of speech <strong>{getPosEntry(targetPos).label}</strong> ({targetPos})
        </p>

        <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap", marginBottom: 16 }}>
          <SelectBox
            label="Source POS"
            value={sourcePos}
            options={POS_SELECT_OPTIONS}
            onChange={setSourcePos}
            color={posColor(sourcePos)}
          />
          <ArrowRight size={16} color="var(--text-muted)" style={{ flexShrink: 0 }} />
          <SelectBox
            label="Dependency"
            value={depRel}
            options={DEP_SELECT_OPTIONS}
            onChange={setDepRel}
            color="var(--accent)"
          />
          <ArrowRight size={16} color="var(--text-muted)" style={{ flexShrink: 0 }} />
          <SelectBox
            label="Target POS"
            value={targetPos}
            options={POS_SELECT_OPTIONS}
            onChange={setTargetPos}
            color={posColor(targetPos)}
          />

          <button
            className="btn btn-primary"
            style={{ marginLeft: "auto" }}
            onClick={handleSearch}
            disabled={patternSearch.isPending}
          >
            <Search size={14} />
            {patternSearch.isPending ? "Searching…" : "Search"}
          </button>
        </div>

        {/* Presets */}
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <span style={{ fontSize: 11, color: "var(--text-muted)", alignSelf: "center" }}>Presets:</span>
          {PRESET_PATTERNS.map((p) => (
            <button
              key={p.label}
              className="btn btn-ghost"
              style={{ fontSize: 11, padding: "3px 10px" }}
              onClick={() => applyPreset(p)}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Results */}
      <AnimatePresence>
        {patternSearch.isError && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{ color: "#dc2626", marginBottom: 16, fontSize: 13 }}
          >
            {patternSearch.error.message}
          </motion.p>
        )}

        {patternSearch.data && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
              <h3 style={{ fontSize: 16 }}>Results</h3>
              <span style={{ fontSize: 13, color: "var(--text-muted)" }}>
                {patternSearch.data.total} match{patternSearch.data.total !== 1 ? "es" : ""}
                {patternSearch.data.total === 500 ? " (limit)" : ""}
              </span>
            </div>

            {patternSearch.data.total === 0 ? (
              <p style={{ color: "var(--text-muted)", textAlign: "center", padding: "40px 0" }}>
                No sentences match this pattern.
              </p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {patternSearch.data.matches.map((match, i) => (
                  <MatchCard key={`${match.sentence.id}-${i}`} match={match} docId={match.sentence.document_id} onNavigate={navigate} />
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function SelectBox({
  label,
  value,
  options,
  onChange,
  color,
}: {
  label: string;
  value: string;
  options: SelectOption[];
  onChange: (v: string) => void;
  color: string;
}) {
  return (
    <div>
      <p style={{ fontSize: 10, color: "var(--text-muted)", marginBottom: 3 }}>{label}</p>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={{
          width: 120,
          borderColor: color + "66",
          color: color,
          fontWeight: 600,
        }}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}

function MatchCard({
  match,
  docId,
  onNavigate,
}: {
  match: PatternMatch;
  docId: number;
  onNavigate: (path: string) => void;
}) {
  return (
    <motion.div
      whileHover={{ x: 2 }}
      transition={{ duration: 0.1 }}
      className="card"
      style={{ padding: "12px 16px", cursor: "pointer" }}
      onClick={() => onNavigate(`/documents/${docId}/sentences/${match.sentence.id}`)}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
        <p style={{ fontSize: 13, lineHeight: 1.6, flex: 1 }}>
          {highlightSentence(match.sentence.text, match.source_text, match.target_text)}
        </p>
        <div style={{ display: "flex", alignItems: "center", gap: 6, flexShrink: 0 }}>
          <span style={{ fontSize: 11, color: "var(--text-muted)" }}>doc {match.sentence.document_id}</span>
          <GitBranch size={13} color="var(--accent)" />
        </div>
      </div>
      <div style={{ marginTop: 6, display: "flex", gap: 8 }}>
        <MatchToken text={match.source_text} color="#5c6bc0" />
        <ArrowRight size={12} color="var(--text-muted)" style={{ alignSelf: "center" }} />
        <MatchToken text={match.target_text} color="#22c55e" />
      </div>
    </motion.div>
  );
}

function MatchToken({ text, color }: { text: string; color: string }) {
  return (
    <span
      style={{
        fontSize: 11,
        fontWeight: 600,
        padding: "2px 8px",
        borderRadius: 4,
        background: color + "22",
        color,
      }}
    >
      {text}
    </span>
  );
}
