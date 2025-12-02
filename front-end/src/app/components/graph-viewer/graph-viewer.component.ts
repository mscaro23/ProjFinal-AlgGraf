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

    const nodes = this.graph.nodes.map((t: string) => ({ id: t }));
    const links = this.graph.links;

    const width = 900;
    const height = 600;

    const sim = d3
      .forceSimulation(nodes)
      .force(
        'link',
        d3
          .forceLink(links)
          .id((d: any) => d.id)
          .distance(150),
      )
      .force('charge', d3.forceManyBody().strength(-250))
      .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg
      .append('g')
      .selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('stroke', '#ddd');

    const node = svg
      .append('g')
      .selectAll('circle')
      .data(nodes)
      .enter()
      .append('circle')
      .attr('r', 10)
      .attr('fill', '#4a6cf7');

    sim.on('tick', () => {
      node.attr('cx', (d: any) => d.x).attr('cy', (d: any) => d.y);
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);
    });
  }
}
