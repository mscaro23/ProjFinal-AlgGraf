import { Component, ElementRef, Input, OnChanges, SimpleChanges, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import * as d3 from 'd3';
import { SimulationNodeDatum } from 'd3';

interface D3Node extends SimulationNodeDatum {
  id: string;
  radius: number;
  x?: number;
  y?: number;
}

@Component({
  selector: 'app-graph-viewer',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './graph-viewer.component.html',
  styleUrl: './graph-viewer.component.scss',
})
export class GraphViewerComponent implements OnChanges {
  @Input() graph: any;
  @Input() pageRankScores: { [title: string]: number } | null = null;

  @ViewChild('svgRef') svgRef!: ElementRef<SVGElement>;

  // Controles de visualização
  maxNodes = 10; // Limite de nós a renderizar
  minPageRankThreshold = 0;
  Math = Math;

  ngOnChanges(changes: SimpleChanges): void {
    if (this.graph) {
      setTimeout(() => this.renderGraph(), 0);
    }
  }

  renderGraph() {
    const svg = d3.select(this.svgRef.nativeElement);
    svg.selectAll('*').remove();

    const { width, height } = this.svgRef.nativeElement.getBoundingClientRect();

    // Filtrar nós se houver muitos
    let filteredNodes = [...this.graph.nodes];
    
    if (filteredNodes.length > this.maxNodes) {
      if (this.pageRankScores) {
        filteredNodes = filteredNodes
          .filter(t => (this.pageRankScores![t] || 0) >= this.minPageRankThreshold)
          .sort((a, b) => (this.pageRankScores![b] || 0) - (this.pageRankScores![a] || 0))
          .slice(0, this.maxNodes);
      } else {
        const sorted = [...filteredNodes].sort((a, b) => a.localeCompare(b));
        filteredNodes = sorted.slice(0, this.maxNodes);
      }
      
      console.log(`Renderizando ${filteredNodes.length} de ${this.graph.nodes.length} nós`);
    }

    const nodeSet = new Set(filteredNodes);

    const nodes: D3Node[] = filteredNodes.map((t: string) => ({ 
      id: t,
      radius: this.pageRankScores ? (this.pageRankScores[t] || 0.01) * 200 + 5 : 10,
      x: undefined,
      y: undefined
    }));
    
    // Filtrar links para incluir apenas nós visíveis
    const links = this.graph.links
      .filter((l: any) => nodeSet.has(l.source) && nodeSet.has(l.target))
      .map((l: any) => ({ ...l }));

    const g = svg.append('g');

    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4]) // Min e max zoom
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom as any);

    const sim = d3
      .forceSimulation(nodes)
      .force(
        'link',
        d3
          .forceLink(links)
          .id((d: any) => d.id)
          .distance(100), // Distância menor para grafos grandes
      )
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide', d3.forceCollide().radius((d: any) => d.radius + 10));

    // Groups for layering (dentro do container g)
    const linkGroup = g.append('g').attr('class', 'links');
    const nodeGroup = g.append('g').attr('class', 'nodes');
    const labelGroup = g.append('g').attr('class', 'labels');

    // Draw Links
    const link = linkGroup
      .selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 1.5);

    // Draw Nodes
    const node = nodeGroup
      .selectAll('circle')
      .data(nodes)
      .enter()
      .append('circle')
      .attr('r', (d: any) => d.radius || 15) // Usa raio do PageRank ou padrão
      .attr('fill', '#4a6cf7') // Primary color
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer');

    // Draw Labels
    const label = labelGroup
      .selectAll('text')
      .data(nodes)
      .enter()
      .append('text')
      .text((d: any) => d.id)
      .attr('font-size', '14px') // Slightly larger font
      .attr('fill', '#fff') // White text
      .attr('dx', 18) // Adjusted offset for larger node
      .attr('dy', 5)
      .style('pointer-events', 'none') // Let clicks pass through to nodes
      .style('font-family', 'sans-serif'); // Ensure clean font

    // Hover Interactions
    node
      .on('mouseover', (event: any, d: any) => {
        // Highlight current node (aumenta 5px do raio original)
        d3.select(event.currentTarget)
          .transition()
          .duration(200)
          .attr('r', d.radius + 5)
          .attr('fill', '#ff6b6b');

        // Find neighbors
        const linkedNodeIds = new Set<string>();
        for (const l of links) {
          if (l.source.id === d.id) linkedNodeIds.add(l.target.id);
          if (l.target.id === d.id) linkedNodeIds.add(l.source.id);
        }

        // Dim unrelated nodes and links
        node.style('opacity', (n: any) => (n.id === d.id || linkedNodeIds.has(n.id) ? 1 : 0.2));
        link.style('opacity', (l: any) =>
          l.source.id === d.id || l.target.id === d.id ? 1 : 0.1
        );
        link.attr('stroke', (l: any) => 
            l.source.id === d.id || l.target.id === d.id ? '#ff6b6b' : '#999'
        ).attr('stroke-width', (l: any) => 
            l.source.id === d.id || l.target.id === d.id ? 2.5 : 1.5
        );
        
        // Emphasize labels of neighbors
        label.style('opacity', (n: any) => 
            n.id === d.id || linkedNodeIds.has(n.id) ? 1 : 0.2
        ).style('font-weight', (n: any) => 
            n.id === d.id || linkedNodeIds.has(n.id) ? 'bold' : 'normal'
        );
      })
      .on('mouseout', (event: any, d: any) => {
        // Reset node style (volta ao raio original)
        d3.select(event.currentTarget)
          .transition()
          .duration(200)
          .attr('r', d.radius)
          .attr('fill', '#4a6cf7');

        // Reset all styles
        node.style('opacity', 1);
        link.style('opacity', 1).attr('stroke', '#999').attr('stroke-width', 1.5);
        label.style('opacity', 1).style('font-weight', 'normal');
      });
      
     // Drag behavior
    node.call(
      d3.drag<SVGCircleElement, any>()
        .on('start', (event, d) => {
          if (!event.active) sim.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) sim.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
    );


    sim.on('tick', () => {
      // Constrain nodes within bounds (área expandida)
      for (const d of nodes) {
         d.x = Math.max(-width, Math.min(width * 1.1, d.x!));
         d.y = Math.max(-height, Math.min(height * 1.1, d.y!));
      }

      node.attr('cx', (d: any) => d.x).attr('cy', (d: any) => d.y);
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);
      
      label
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y);
    });
  }
}
