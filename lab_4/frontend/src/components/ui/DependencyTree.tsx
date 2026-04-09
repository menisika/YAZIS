import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import type { TokenResponse } from "@/types";
import { posColor } from "@/lib/utils";
import { getDepEntry, getPosEntry, getTagEntry } from "@/lib/linguisticGlossary";

interface TreeNode {
  id: number;
  index: number;
  text: string;
  lemma: string;
  pos: string;
  tag: string;
  dep: string;
  head_index: number;
  is_stop: boolean;
  is_punct: boolean;
  ent_type: string;
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
      if (parent) parent.children.push(nodes[t.index]);
    }
  });
  // Fallback: if no ROOT token found, pick first
  if (!root) root = nodes[0] ?? null;
  return root;
}

export function DependencyTree({ tokens }: { tokens: TokenResponse[] }) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);

  useEffect(() => {
    if (!svgRef.current || !tokens.length) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    const tokenByIndex = new Map(tokens.map((token) => [token.index, token]));

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

    // Zoom
    const zoom = d3.zoom<SVGSVGElement, unknown>().scaleExtent([0.3, 3]).on("zoom", (event) => {
      g.attr("transform", event.transform.toString());
    });
    svg.call(zoom);

    // Links (curved paths)
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

    // Edge labels (dep relation)
    g.selectAll(".edge-label")
      .data(hierarchy.links())
      .join("text")
      .attr("class", "edge-label")
      .attr("x", (d) => ((d.source.x ?? 0) + (d.target.x ?? 0)) / 2)
      .attr("y", (d) => ((d.source.y ?? 0) + (d.target.y ?? 0)) / 2 - 4)
      .attr("text-anchor", "middle")
      .attr("font-size", 9)
      .attr("fill", "#9ca3af")
      .attr("font-family", "-apple-system, sans-serif")
      .text((d) => {
        const label = getDepEntry(d.target.data.dep).label;
        return label.length > 18 ? `${label.slice(0, 17)}…` : label;
      });

    // Node groups
    const nodeGroups = g.selectAll<SVGGElement, d3.HierarchyPointNode<TreeNode>>(".node")
      .data(descendants)
      .join("g")
      .attr("class", "node")
      .attr("transform", (d) => `translate(${d.x ?? 0},${d.y ?? 0})`)
      .style("cursor", "pointer")
      .on("mouseenter", (event, d) => {
        const token = tokenByIndex.get(d.data.index);
        if (!token) return;
        const svgRect = svgRef.current!.getBoundingClientRect();
        setTooltip({
          x: event.clientX - svgRect.left,
          y: event.clientY - svgRect.top,
          token,
        });
      })
      .on("mouseleave", () => setTooltip(null));

    // Circles with hand-drawn feel (slightly offset stroke)
    const R = 22;
    nodeGroups
      .append("circle")
      .attr("r", R + 2)
      .attr("fill", "none")
      .attr("stroke", (d) => posColor(d.data.pos))
      .attr("stroke-width", 0.5)
      .attr("opacity", 0.3);

    nodeGroups
      .append("circle")
      .attr("r", R)
      .attr("fill", (d) => posColor(d.data.pos) + "22")
      .attr("stroke", (d) => posColor(d.data.pos))
      .attr("stroke-width", 2);

    // Token text (surface form)
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
        return t.length > 8 ? t.slice(0, 7) + "…" : t;
      });

    // POS label below circle
    nodeGroups
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dy", R + 14)
      .attr("font-size", 9)
      .attr("font-family", "-apple-system, sans-serif")
      .attr("fill", (d) => posColor(d.data.pos))
      .text((d) => {
        const label = getPosEntry(d.data.pos).label;
        return label.length > 14 ? `${label.slice(0, 13)}…` : label;
      });
  }, [tokens]);

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
            maxWidth: 200,
          }}
        >
          {(() => {
            const posEntry = getPosEntry(tooltip.token.pos);
            const tagEntry = getTagEntry(tooltip.token.tag);
            const depEntry = getDepEntry(tooltip.token.dep);
            return (
              <>
          <p style={{ fontWeight: 700, marginBottom: 4 }}>{tooltip.token.text}</p>
          <p style={{ opacity: 0.8 }}>lemma: <strong>{tooltip.token.lemma}</strong></p>
          <p style={{ opacity: 0.8 }}>
            Part of Speech: <strong>{posEntry.label}</strong> ({posEntry.ruLabel})
          </p>
          <p style={{ opacity: 0.8 }}>
            Morphological Tag: <strong>{tagEntry.label}</strong> ({tagEntry.ruLabel})
          </p>
          <p style={{ opacity: 0.8 }}>
            Dependency Relation: <strong>{depEntry.label}</strong> ({depEntry.ruLabel})
          </p>
          {tooltip.token.ent_type && (
            <p style={{ opacity: 0.8 }}>entity: <strong>{tooltip.token.ent_type}</strong></p>
          )}
              </>
            );
          })()}
        </div>
      )}
    </div>
  );
}
