import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { X } from "lucide-react";
import { useConceptNet } from "@/api/hooks";
import type { ConceptNetEdge } from "@/types";

interface ForceNode extends d3.SimulationNodeDatum {
  id: string;
  label: string;
  isCenter: boolean;
}

interface ForceLink extends d3.SimulationLinkDatum<ForceNode> {
  relation: string;
}

interface ConceptNetPanelProps {
  word: string | null;
  onClose: () => void;
}

const RELATION_COLORS: Record<string, string> = {
  SimilarTo: "#a78bfa",   // Synonym — indigo
  Antonym: "#ef4444",     // Antonym — red
  IsA: "#3b82f6",         // Hypernym — blue
  Narrower: "#06b6d4",    // Hyponym — cyan
  PartOf: "#f59e0b",      // Holonym — amber
  HasPart: "#22c55e",     // Meronym — green
};

function relColor(rel: string): string {
  return RELATION_COLORS[rel] ?? "#9ca3af";
}

function buildForceGraph(
  svgRef: React.RefObject<SVGSVGElement>,
  word: string,
  edges: ConceptNetEdge[],
  onNodeClick: (label: string) => void,
) {
  if (!svgRef.current) return;
  const width = svgRef.current.clientWidth || 340;
  const height = 320;

  const svg = d3.select(svgRef.current);
  svg.selectAll("*").remove();
  svg.attr("width", width).attr("height", height);

  // Build unique nodes
  const nodeMap = new Map<string, ForceNode>();
  const centerId = word.toLowerCase();
  nodeMap.set(centerId, { id: centerId, label: word, isCenter: true });

  edges.forEach((e) => {
    const targetId = e.end_label.toLowerCase();
    if (!nodeMap.has(targetId)) {
      nodeMap.set(targetId, { id: targetId, label: e.end_label, isCenter: false });
    }
  });

  const nodes: ForceNode[] = Array.from(nodeMap.values());
  const links: ForceLink[] = edges
    .filter((e) => nodeMap.has(e.end_label.toLowerCase()))
    .map((e) => ({
      source: centerId,
      target: e.end_label.toLowerCase(),
      relation: e.relation,
    }));

  const simulation = d3
    .forceSimulation<ForceNode>(nodes)
    .force("link", d3.forceLink<ForceNode, ForceLink>(links).id((d) => d.id).distance(90))
    .force("charge", d3.forceManyBody().strength(-220))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide(32));

  // Arrow marker
  svg
    .append("defs")
    .append("marker")
    .attr("id", "arrow")
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 22)
    .attr("refY", 0)
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto")
    .append("path")
    .attr("d", "M0,-5L10,0L0,5")
    .attr("fill", "#9ca3af");

  const g = svg.append("g");

  // Zoom
  svg.call(
    d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.4, 2.5])
      .on("zoom", (event) => g.attr("transform", event.transform.toString())),
  );

  // Links
  const link = g
    .selectAll(".cn-link")
    .data(links)
    .join("line")
    .attr("class", "cn-link")
    .attr("stroke", (d) => relColor(d.relation))
    .attr("stroke-width", 1.5)
    .attr("stroke-opacity", 0.7)
    .attr("marker-end", "url(#arrow)");

  // Link labels
  const linkLabel = g
    .selectAll(".cn-link-label")
    .data(links)
    .join("text")
    .attr("class", "cn-link-label")
    .attr("font-size", 8)
    .attr("text-anchor", "middle")
    .attr("fill", (d) => relColor(d.relation))
    .attr("font-family", "-apple-system, sans-serif")
    .text((d) => d.relation);

  // Nodes
  const nodeGroup = g
    .selectAll<SVGGElement, ForceNode>(".cn-node")
    .data(nodes)
    .join("g")
    .attr("class", "cn-node")
    .style("cursor", "pointer")
    .call(
      d3.drag<SVGGElement, ForceNode>()
        .on("start", (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }),
    )
    .on("click", (_event, d) => {
      if (!d.isCenter) onNodeClick(d.label);
    });

  nodeGroup
    .append("circle")
    .attr("r", (d) => (d.isCenter ? 26 : 18))
    .attr("fill", (d) => (d.isCenter ? "#5c6bc022" : "#f9fafb"))
    .attr("stroke", (d) => (d.isCenter ? "#5c6bc0" : "#d1d5db"))
    .attr("stroke-width", (d) => (d.isCenter ? 2.5 : 1.5));

  nodeGroup
    .append("text")
    .attr("text-anchor", "middle")
    .attr("dy", "0.35em")
    .attr("font-size", (d) => (d.isCenter ? 11 : 9))
    .attr("font-weight", (d) => (d.isCenter ? 700 : 400))
    .attr("font-family", "-apple-system, sans-serif")
    .attr("fill", "#1a1a1a")
    .text((d) => (d.label.length > 10 ? `${d.label.slice(0, 9)}…` : d.label));

  simulation.on("tick", () => {
    link
      .attr("x1", (d) => (d.source as ForceNode).x ?? 0)
      .attr("y1", (d) => (d.source as ForceNode).y ?? 0)
      .attr("x2", (d) => (d.target as ForceNode).x ?? 0)
      .attr("y2", (d) => (d.target as ForceNode).y ?? 0);

    linkLabel
      .attr("x", (d) => (((d.source as ForceNode).x ?? 0) + ((d.target as ForceNode).x ?? 0)) / 2)
      .attr("y", (d) => (((d.source as ForceNode).y ?? 0) + ((d.target as ForceNode).y ?? 0)) / 2 - 4);

    nodeGroup.attr("transform", (d) => `translate(${d.x ?? 0},${d.y ?? 0})`);
  });
}

export function ConceptNetPanel({ word, onClose }: ConceptNetPanelProps) {
  const svgRef = useRef<SVGSVGElement>(null!);
  const [exploredWord, setExploredWord] = useState<string | null>(null);

  const activeWord = exploredWord ?? word;
  const { data, isLoading, isError } = useConceptNet(activeWord ?? "", !!activeWord);

  // Reset explored word when the source word changes
  useEffect(() => {
    setExploredWord(null);
  }, [word]);

  useEffect(() => {
    if (!data || !activeWord) return;
    buildForceGraph(svgRef, activeWord, data.edges, (label) => setExploredWord(label));
  }, [data, activeWord]);

  if (!word) return null;

  return (
    <div
      style={{
        width: 360,
        flexShrink: 0,
        background: "var(--surface)",
        border: "1px solid var(--border)",
        borderRadius: 10,
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div style={{ padding: "10px 14px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <p style={{ fontWeight: 700, fontSize: 13 }}>
            WordNet:{" "}
            <span style={{ color: "var(--accent)" }}>&ldquo;{activeWord}&rdquo;</span>
          </p>
          {exploredWord && (
            <button
              style={{ fontSize: 11, color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer", padding: 0, marginTop: 2 }}
              onClick={() => setExploredWord(null)}
            >
              ← back to &ldquo;{word}&rdquo;
            </button>
          )}
        </div>
        <button
          onClick={onClose}
          style={{ background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)", padding: 4 }}
          aria-label="Close ConceptNet panel"
        >
          <X size={16} />
        </button>
      </div>

      {/* Graph area */}
      <div style={{ flex: 1, minHeight: 320, position: "relative" }}>
        {isLoading && (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 320, color: "var(--text-muted)", fontSize: 13 }}>
            Loading WordNet…
          </div>
        )}
        {isError && (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 320, color: "#ef4444", fontSize: 13, padding: 16, textAlign: "center" }}>
            Failed to load WordNet relations.
          </div>
        )}
        {data && !isLoading && (
          <>
            <svg ref={svgRef} style={{ width: "100%", display: "block" }} />
            {data.edges.length === 0 && (
              <p style={{ textAlign: "center", color: "var(--text-muted)", fontSize: 12, padding: 16 }}>
                No WordNet relations found for &ldquo;{activeWord}&rdquo;
              </p>
            )}
          </>
        )}
      </div>

      {/* Relation legend */}
      {data && data.edges.length > 0 && (
        <div style={{ padding: "8px 14px", borderTop: "1px solid var(--border)", display: "flex", flexWrap: "wrap", gap: 4 }}>
          {Array.from(new Set(data.edges.map((e) => e.relation))).slice(0, 6).map((rel) => (
            <span
              key={rel}
              style={{
                fontSize: 9,
                padding: "1px 6px",
                borderRadius: 4,
                background: relColor(rel) + "22",
                color: relColor(rel),
                fontWeight: 600,
              }}
            >
              {rel}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
