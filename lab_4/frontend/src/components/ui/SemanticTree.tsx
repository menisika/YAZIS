import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { useWordNet } from "@/api/hooks";
import type { TokenResponse } from "@/types";

// ─── Semantic role color palette ─────────────────────────────────────────────

const ROLE_COLORS: Record<string, string> = {
  AGNT: "#ef4444",   // Agent — red
  PAT: "#3b82f6",    // Patient — blue
  ACT: "#22c55e",    // Action — green
  INST: "#f59e0b",   // Instrument — amber
  LOC: "#8b5cf6",    // Location — violet
  ATTR: "#ec4899",   // Attribute — pink
  RCPT: "#06b6d4",   // Recipient — cyan
  MOD: "#6b7280",    // Modifier — gray
  NEG: "#dc2626",    // Negation — dark red
  AUX: "#9ca3af",    // Auxiliary — light gray
  POSS: "#92400e",   // Possessor — brown
  QUANT: "#65a30d",  // Quantity — lime
  DET: "#d1d5db",    // Determiner — light
  CONJ: "#a78bfa",   // Conjunction — indigo
  APPOS: "#fb923c",  // Apposition — orange
  PURP: "#14b8a6",   // Purpose — teal
  SRC: "#f87171",    // Source — rose
  GOAL: "#4ade80",   // Goal — light green
  TEMP: "#facc15",   // Time — yellow
  MANN: "#60a5fa",   // Manner — sky blue
  CAUS: "#e879f9",   // Cause — fuchsia
  PUNCT: "#e5e7eb",  // Punctuation — very light
};

function roleColor(role: string): string {
  return ROLE_COLORS[role] ?? "#9ca3af";
}

interface TreeNode {
  id: number;
  index: number;
  text: string;
  lemma: string;
  pos: string;
  dep: string;
  head_index: number;
  is_stop: boolean;
  is_punct: boolean;
  semantic_role: string;
  semantic_label: string;
  is_anomalous: boolean;
  anomaly_reason: string;
  children: TreeNode[];
}

interface TooltipState {
  x: number;
  y: number;
  token: TokenResponse;
}

function buildTree(tokens: TokenResponse[]): TreeNode | null {
  if (!tokens.length) return null;
  const nodes: Record<number, TreeNode> = {};
  tokens.forEach((t) => {
    nodes[t.index] = { ...t, children: [] };
  });
  let root: TreeNode | null = null;
  tokens.forEach((t) => {
    if (t.dep === "ROOT") {
      root = nodes[t.index];
    } else {
      const parent = nodes[t.head_index];
      if (parent && parent !== nodes[t.index]) parent.children.push(nodes[t.index]);
    }
  });
  if (!root) root = nodes[0] ?? null;
  return root;
}

interface SemanticTreeProps {
  tokens: TokenResponse[];
  onNodeClick?: (token: TokenResponse) => void;
}

export function SemanticTree({ tokens, onNodeClick }: SemanticTreeProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);

  // Fetch WordNet definition + synonyms for the hovered content word
  const isContentWord = !!tooltip && !tooltip.token.is_stop && !tooltip.token.is_punct;
  const { data: wordnetData, isLoading: wnLoading } = useWordNet(
    tooltip?.token.text ?? "",
    tooltip?.token.pos ?? "",
    isContentWord,
  );

  useEffect(() => {
    if (!svgRef.current || !tokens.length) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    const tokenByIndex = new Map(tokens.map((t) => [t.index, t]));

    const root = buildTree(tokens);
    if (!root) return;

    const nodeW = 80;
    const nodeH = 60;
    const margin = { top: 40, right: 30, bottom: 40, left: 30 };

    const hierarchy = d3.hierarchy(root, (d) => d.children);
    const treeLayout = d3.tree<TreeNode>().nodeSize([nodeW + 20, nodeH + 20]);
    treeLayout(hierarchy);

    const descendants = hierarchy.descendants();
    const minX = d3.min(descendants, (d) => d.x ?? 0) ?? 0;
    const maxX = d3.max(descendants, (d) => d.x ?? 0) ?? 0;
    const maxY = d3.max(descendants, (d) => d.y ?? 0) ?? 0;

    const width = maxX - minX + nodeW + margin.left + margin.right;
    const height = maxY + nodeH + margin.top + margin.bottom;

    svg.attr("width", width).attr("height", height);

    const g = svg
      .append("g")
      .attr("transform", `translate(${-minX + margin.left + nodeW / 2},${margin.top})`);

    const zoom = d3.zoom<SVGSVGElement, unknown>().scaleExtent([0.3, 3]).on("zoom", (event) => {
      g.attr("transform", event.transform.toString());
    });
    svg.call(zoom);

    // Links
    const linkGen = d3
      .linkVertical<d3.HierarchyLink<TreeNode>, d3.HierarchyNode<TreeNode>>()
      .x((d) => (d as d3.HierarchyPointNode<TreeNode>).x ?? 0)
      .y((d) => (d as d3.HierarchyPointNode<TreeNode>).y ?? 0);

    g.selectAll(".link")
      .data(hierarchy.links())
      .join("path")
      .attr("class", "link")
      .attr("d", (d) => linkGen(d))
      .attr("fill", "none")
      .attr("stroke", "#d1d5db")
      .attr("stroke-width", 1.5);

    // Edge labels — semantic label only, no syntactic fallback
    g.selectAll(".edge-label")
      .data(hierarchy.links())
      .join("text")
      .attr("class", "edge-label")
      .attr("x", (d) => ((d.source.x ?? 0) + (d.target.x ?? 0)) / 2)
      .attr("y", (d) => ((d.source.y ?? 0) + (d.target.y ?? 0)) / 2 - 4)
      .attr("text-anchor", "middle")
      .attr("font-size", 9)
      .attr("fill", (d) => roleColor(d.target.data.semantic_role))
      .attr("font-family", "-apple-system, sans-serif")
      .attr("font-weight", 600)
      .text((d) => {
        const lbl = d.target.data.semantic_label;
        if (!lbl) return "";
        return lbl.length > 16 ? `${lbl.slice(0, 15)}…` : lbl;
      });

    // Node groups
    const nodeGroups = g
      .selectAll<SVGGElement, d3.HierarchyPointNode<TreeNode>>(".node")
      .data(descendants)
      .join("g")
      .attr("class", "node")
      .attr("transform", (d) => `translate(${d.x ?? 0},${d.y ?? 0})`)
      .style("cursor", "pointer")
      .on("mouseenter", (event, d) => {
        const token = tokenByIndex.get(d.data.index);
        if (!token) return;
        const svgRect = svgRef.current!.getBoundingClientRect();
        setTooltip({ x: event.clientX - svgRect.left, y: event.clientY - svgRect.top, token });
      })
      .on("mouseleave", () => setTooltip(null))
      .on("click", (_event, d) => {
        const token = tokenByIndex.get(d.data.index);
        if (token && onNodeClick) onNodeClick(token);
      });

    const R = 22;

    // Outer glow ring for anomalous nodes
    nodeGroups
      .filter((d) => d.data.is_anomalous)
      .append("circle")
      .attr("r", R + 6)
      .attr("fill", "none")
      .attr("stroke", "#ef4444")
      .attr("stroke-width", 1.5)
      .attr("opacity", 0.4)
      .attr("stroke-dasharray", "4,2");

    // Standard outer ring
    nodeGroups
      .append("circle")
      .attr("r", R + 2)
      .attr("fill", "none")
      .attr("stroke", (d) => roleColor(d.data.semantic_role))
      .attr("stroke-width", 0.5)
      .attr("opacity", 0.3);

    // Main circle
    nodeGroups
      .append("circle")
      .attr("r", R)
      .attr("fill", (d) => roleColor(d.data.semantic_role) + "22")
      .attr("stroke", (d) => (d.data.is_anomalous ? "#ef4444" : roleColor(d.data.semantic_role)))
      .attr("stroke-width", (d) => (d.data.is_anomalous ? 2.5 : 2))
      .attr("stroke-dasharray", (d) => (d.data.is_anomalous ? "5,2" : "none"));

    // Token text
    nodeGroups
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dy", "0.35em")
      .attr("font-size", 11)
      .attr("font-weight", 600)
      .attr("font-family", "-apple-system, sans-serif")
      .attr("fill", "#1a1a1a")
      .text((d) => {
        const t = d.data.text;
        return t.length > 8 ? `${t.slice(0, 7)}…` : t;
      });

    // Role label below circle — semantic role/label only, no POS fallback
    nodeGroups
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dy", R + 14)
      .attr("font-size", 9)
      .attr("font-family", "-apple-system, sans-serif")
      .attr("fill", (d) => roleColor(d.data.semantic_role))
      .text((d) => {
        const lbl = d.data.semantic_label || d.data.semantic_role;
        if (!lbl) return "";
        return lbl.length > 12 ? `${lbl.slice(0, 11)}…` : lbl;
      });

    // Anomaly warning icon ⚠
    nodeGroups
      .filter((d) => d.data.is_anomalous)
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dy", -R - 6)
      .attr("font-size", 12)
      .attr("fill", "#ef4444")
      .text("⚠");
  }, [tokens, onNodeClick]);

  return (
    <div style={{ position: "relative", overflow: "hidden", borderRadius: 10, background: "var(--surface)", border: "1px solid var(--border)" }}>
      <svg ref={svgRef} style={{ width: "100%", minHeight: 200, display: "block" }} />

      {tooltip && (
        <div
          style={{
            position: "absolute",
            left: tooltip.x + 12,
            top: tooltip.y - 8,
            background: "#1a1a1a",
            color: "white",
            borderRadius: 7,
            padding: "8px 12px",
            fontSize: 12,
            pointerEvents: "none",
            zIndex: 10,
            boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
            maxWidth: 260,
          }}
        >
          <p style={{ fontWeight: 700, marginBottom: 4 }}>{tooltip.token.text}</p>
          <p style={{ opacity: 0.8, marginBottom: 4 }}>
            Semantic Role:{" "}
            <strong style={{ color: roleColor(tooltip.token.semantic_role) }}>
              {tooltip.token.semantic_label || tooltip.token.semantic_role || "—"}
            </strong>
          </p>

          {isContentWord && (
            <>
              {wnLoading && (
                <p style={{ opacity: 0.5, fontStyle: "italic", marginBottom: 2 }}>Loading definition…</p>
              )}
              {wordnetData?.definition && (
                <p style={{ opacity: 0.8, lineHeight: 1.4, marginBottom: 3 }}>
                  {wordnetData.definition}
                </p>
              )}
              {wordnetData && wordnetData.synonyms.length > 0 && (
                <p style={{ opacity: 0.65, marginBottom: 2 }}>
                  <span style={{ fontWeight: 600 }}>Synonyms: </span>
                  {wordnetData.synonyms.join(", ")}
                </p>
              )}
            </>
          )}

          {tooltip.token.is_anomalous && (
            <p style={{ color: "#ef4444", marginTop: 4, fontWeight: 600 }}>
              ⚠ {tooltip.token.anomaly_reason}
            </p>
          )}
          <p style={{ opacity: 0.5, marginTop: 4, fontSize: 10 }}>Click for WordNet relations</p>
        </div>
      )}

      {/* Legend */}
      <div style={{
        position: "absolute",
        bottom: 8,
        right: 8,
        background: "rgba(255,255,255,0.9)",
        borderRadius: 6,
        padding: "4px 8px",
        fontSize: 10,
        color: "#6b7280",
        border: "1px solid var(--border)",
      }}>
        Click a node to explore WordNet
      </div>
    </div>
  );
}
