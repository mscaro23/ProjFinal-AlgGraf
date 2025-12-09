import { Component, ElementRef, Input, OnChanges, SimpleChanges, ViewChild } from '@angular/core';

import * as d3 from 'd3';

@Component({
  selector: 'app-graph-viewer',
  templateUrl: './graph-viewer.component.html',
  // styleUrl: './graph-viewer.component.scss',
})
export class GraphViewerComponent implements OnChanges {
  @Input() graph: any;

  @ViewChild('svgRef') svgRef!: ElementRef<SVGElement>;

  ngOnChanges(changes: SimpleChanges): void {
    if (this.graph) {
      setTimeout(() => this.renderGraph(), 0);
    }
  }

  renderGraph() {
    const svg = d3.select(this.svgRef.nativeElement);
    svg.selectAll('*').remove();

    const { width, height } = this.svgRef.nativeElement.getBoundingClientRect();

    const nodes = this.graph.nodes.map((t: string) => ({ id: t }));
    const links = this.graph.links.map((l: any) => ({ ...l }));

    // Simulation setup
    const sim = d3
      .forceSimulation(nodes)
      .force(
        'link',
        d3
          .forceLink(links)
          .id((d: any) => d.id)
          .distance(150),
      )
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide', d3.forceCollide(30)); 

    // Groups for layering
    const linkGroup = svg.append('g').attr('class', 'links');
    const nodeGroup = svg.append('g').attr('class', 'nodes');
    const labelGroup = svg.append('g').attr('class', 'labels');

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
      .attr('r', 15) // Increased size
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
        // Highlight current node
        d3.select(event.currentTarget)
          .transition()
          .duration(200)
          .attr('r', 20) // Larger highlight
          .attr('fill', '#ff6b6b');

        // Find neighbors
        const linkedNodeIds = new Set<string>();
        links.forEach((l: any) => {
          if (l.source.id === d.id) linkedNodeIds.add(l.target.id);
          if (l.target.id === d.id) linkedNodeIds.add(l.source.id);
        });

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
        // Reset node style
        d3.select(event.currentTarget)
          .transition()
          .duration(200)
          .attr('r', 15) // Reset to new default size
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
      // Constrain nodes within bounds
      nodes.forEach((d:any) => {
         d.x = Math.max(8, Math.min(width - 8, d.x));
         d.y = Math.max(8, Math.min(height - 8, d.y));
      });

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
