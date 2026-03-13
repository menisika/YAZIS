import { useRef, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import * as d3 from "d3";
import { ArrowLeft } from "lucide-react";
import { useAllSentences, useDocument } from "@/api/hooks";
import { PageHeader } from "@/components/ui/PageHeader";
import { Skeleton } from "@/components/ui/Skeleton";
import type { SentenceListItem } from "@/types";

interface CellTooltip {
  x: number;
  y: number;
  sentence: SentenceListItem;
}

export function HeatmapPage() {
  const { id } = useParams<{ id: string }>();
  const docId = Number(id);
  const navigate = useNavigate();

  const { data: doc } = useDocument(docId);
  const { data: sentences, isLoading } = useAllSentences(docId);

  const svgRef = useRef<SVGSVGElement>(null);
  const legendRef = useRef<SVGSVGElement>(null);
  const [tooltip, setTooltip] = useState<CellTooltip | null>(null);

  useEffect(() => {
    if (!svgRef.current || !sentences?.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const colorScale = d3.scaleSequential(d3.interpolateRdYlBu).domain([100, 0]);

    const containerWidth = svgRef.current.parentElement?.clientWidth ?? 800;
    const CELL_HEIGHT = 36;
    const CELL_GAP = 3;
    const MIN_CELL_W = 12;
    const MAX_CELL_W = 60;

    const cellW = Math.min(MAX_CELL_W, Math.max(MIN_CELL_W, Math.floor((containerWidth - 24) / sentences.length - CELL_GAP)));
    const totalWidth = sentences.length * (cellW + CELL_GAP);
    const svgWidth = Math.max(containerWidth, totalWidth + 24);

    svg.attr("width", svgWidth).attr("height", CELL_HEIGHT + 16);

    const g = svg.append("g").attr("transform", "translate(12, 8)");

    g.selectAll(".cell")
      .data(sentences)
      .join("rect")
      .attr("class", "cell")
      .attr("x", (_, i) => i * (cellW + CELL_GAP))
      .attr("y", 0)
      .attr("width", cellW)
      .attr("height", CELL_HEIGHT)
      .attr("rx", 3)
      .attr("fill", (d) => colorScale(d.complexity_score))
      .attr("stroke", "var(--bg)")
      .attr("stroke-width", 1)
      .style("cursor", "pointer")
      .on("mouseenter", (event, d) => {
        const svgRect = svgRef.current!.getBoundingClientRect();
        setTooltip({ x: event.clientX - svgRect.left, y: event.clientY - svgRect.top, sentence: d });
        d3.select(event.currentTarget).attr("stroke", "#1a1a1a").attr("stroke-width", 1.5);
      })
      .on("mouseleave", (event) => {
        setTooltip(null);
        d3.select(event.currentTarget).attr("stroke", "var(--bg)").attr("stroke-width", 1);
      })
      .on("click", (_event, d) => {
        navigate(`/documents/${docId}/sentences/${d.id}`);
      });
  }, [sentences, docId, navigate]);

  // Legend
  useEffect(() => {
    if (!legendRef.current) return;
    const svg = d3.select(legendRef.current);
    svg.selectAll("*").remove();

    const W = 200;
    const H = 14;
    const margin = { top: 4, right: 30, bottom: 34, left: 30 };
    svg.attr("width", W + margin.left + margin.right).attr("height", H + margin.top + margin.bottom);

    const legendGroup = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    const defs = svg.append("defs");
    const grad = defs.append("linearGradient").attr("id", "heatmap-legend-grad");
    const stops = d3.range(0, 1.01, 0.1);
    const colorScale = d3.scaleSequential(d3.interpolateRdYlBu).domain([100, 0]);
    stops.forEach((t) => {
      grad.append("stop")
        .attr("offset", `${t * 100}%`)
        .attr("stop-color", colorScale(t * 100));
    });

    legendGroup
      .append("rect")
      .attr("x", 0)
      .attr("y", 0)
      .attr("width", W)
      .attr("height", H)
      .attr("rx", 4)
      .attr("fill", "url(#heatmap-legend-grad)");

    const xScale = d3.scaleLinear().domain([0, 100]).range([0, W]);
    const axis = d3.axisBottom(xScale).ticks(5).tickSize(3);
    legendGroup
      .append("g")
      .attr("transform", `translate(0,${H + 4})`)
      .call(axis)
      .call((g) => g.select(".domain").remove())
      .call((g) => g.selectAll("text").attr("font-size", 9).attr("fill", "var(--text-muted)").attr("dy", "0.9em"));

    legendGroup
      .append("text")
      .attr("x", 0)
      .attr("y", H + 28)
      .attr("font-size", 9)
      .attr("fill", "var(--text-muted)")
      .attr("text-anchor", "start")
      .text("Simple");
    legendGroup
      .append("text")
      .attr("x", W)
      .attr("y", H + 28)
      .attr("font-size", 9)
      .attr("fill", "var(--text-muted)")
      .attr("text-anchor", "end")
      .text("Complex");
  }, [sentences]);

  return (
    <div style={{ padding: 32, maxWidth: 1200, margin: "0 auto" }}>
      <div style={{ marginBottom: 8 }}>
        <Link
          to={`/documents/${docId}`}
          style={{ fontSize: 12, color: "var(--text-muted)", display: "inline-flex", alignItems: "center", gap: 4 }}
        >
          <ArrowLeft size={12} /> Sentences
        </Link>
      </div>

      <PageHeader
        title="Complexity Heatmap"
        subtitle={doc?.filename}
      />

      <div style={{ marginBottom: 16 }}>
        <p style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 12 }}>
          Each cell is one sentence. Click any cell to view its dependency tree.
        </p>
        <svg ref={legendRef} />
      </div>

      {isLoading ? (
        <Skeleton height={52} />
      ) : !sentences?.length ? (
        <p style={{ color: "var(--text-muted)" }}>No sentences found.</p>
      ) : (
        <div
          className="card"
          style={{ padding: 16, overflow: "auto", position: "relative" }}
        >
          <svg ref={svgRef} style={{ display: "block", minWidth: "100%" }} />

          {tooltip && (
            <div
              style={{
                position: "absolute",
                left: tooltip.x + 14,
                top: tooltip.y - 8,
                background: "#1a1a1a",
                color: "white",
                borderRadius: 7,
                padding: "8px 12px",
                fontSize: 12,
                pointerEvents: "none",
                zIndex: 10,
                maxWidth: 280,
                boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
              }}
            >
              <p style={{ fontWeight: 600, marginBottom: 4 }}>Sentence {tooltip.sentence.index + 1}</p>
              <p style={{ opacity: 0.8, marginBottom: 4, lineHeight: 1.4 }}>
                {tooltip.sentence.text.slice(0, 100)}{tooltip.sentence.text.length > 100 ? "…" : ""}
              </p>
              <p style={{ opacity: 0.6 }}>
                Complexity: {tooltip.sentence.complexity_score.toFixed(1)} · {tooltip.sentence.token_count} tokens
              </p>
            </div>
          )}
        </div>
      )}

      {sentences && sentences.length > 0 && (
        <div style={{ marginTop: 20 }}>
          <h3 style={{ fontSize: 16, marginBottom: 12 }}>Top 5 Most Complex Sentences</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {[...sentences]
              .sort((a, b) => b.complexity_score - a.complexity_score)
              .slice(0, 5)
              .map((s) => (
                <div
                  key={s.id}
                  className="card"
                  style={{ padding: "12px 14px", cursor: "pointer", display: "flex", gap: 12, alignItems: "center" }}
                  onClick={() => navigate(`/documents/${docId}/sentences/${s.id}`)}
                >
                  <span
                    style={{
                      width: 10,
                      height: 10,
                      borderRadius: "50%",
                      background: d3.scaleSequential(d3.interpolateRdYlBu).domain([100, 0])(s.complexity_score),
                      flexShrink: 0,
                    }}
                  />
                  <span style={{ fontSize: 13, flex: 1 }}>
                    {s.text.slice(0, 120)}{s.text.length > 120 ? "…" : ""}
                  </span>
                  <span
                    style={{
                      fontSize: 11,
                      fontWeight: 600,
                      color: d3.scaleSequential(d3.interpolateRdYlBu).domain([100, 0])(s.complexity_score),
                      flexShrink: 0,
                    }}
                  >
                    {s.complexity_score.toFixed(1)}
                  </span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
