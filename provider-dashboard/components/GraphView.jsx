// src/components/GraphView.jsx
import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { getInteractionGraph } from "../api";

export default function GraphView() {
  const svgRef = useRef(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadGraph() {
      setLoading(true);
      setErrorMsg("");

      try {
        const data = await getInteractionGraph();
        drawGraph(data);
      } catch (err) {
        console.error(err);
        setErrorMsg("Error loading interaction graph. Check /interaction_graph API.");
      } finally {
        setLoading(false);
      }
    }

    loadGraph();
  }, []);

  function drawGraph(data) {
    const svgEl = svgRef.current;
    if (!svgEl) return;

    const svg = d3.select(svgEl);
    svg.selectAll("*").remove();

    const width = svgEl.clientWidth || 600;
    const height = 400;

    svg.attr("viewBox", `0 0 ${width} ${height}`);

    const nodes = data.nodes || [];
    const links = data.edges || [];

    const simulation = d3
      .forceSimulation(nodes)
      .force(
        "link",
        d3
          .forceLink(links)
          .id((d) => d.id)
          .distance(100)
      )
      .force("charge", d3.forceManyBody().strength(-150))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg
      .append("g")
      .attr("stroke", "#aaa")
      .attr("stroke-width", 1.5)
      .selectAll("line")
      .data(links)
      .enter()
      .append("line");

    const node = svg
      .append("g")
      .selectAll("circle")
      .data(nodes)
      .enter()
      .append("circle")
      .attr("r", 6)
      .attr("fill", "#0077ff")
      .call(
        d3
          .drag()
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
          })
      );

    const labels = svg
      .append("g")
      .selectAll("text")
      .data(nodes)
      .enter()
      .append("text")
      .text((d) => d.label || d.id)
      .attr("font-size", 10)
      .attr("dx", 10)
      .attr("dy", 3);

    simulation.on("tick", () => {
      link
        .attr("x1", (d) => d.source.x)
        .attr("y1", (d) => d.source.y)
        .attr("x2", (d) => d.target.x)
        .attr("y2", (d) => d.target.y);

      node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);

      labels.attr("x", (d) => d.x).attr("y", (d) => d.y);
    });
  }

  return (
    <div className="card">
      <h2>Drug Interaction Graph</h2>
      {loading && <p>Loading interaction graph...</p>}
      {errorMsg && <p className="error">{errorMsg}</p>}
      <svg ref={svgRef} style={{ width: "100%", height: "400px", border: "1px solid #ddd" }} />
    </div>
  );
}
