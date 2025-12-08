import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { GraphService } from '../../services/graph.service';
import { GraphViewerComponent } from '../../components/graph-viewer/graph-viewer.component';
import { NgIf } from '@angular/common';

@Component({
  selector: 'app-graph',
  standalone: true,
  imports: [NgIf, GraphViewerComponent, RouterModule],
  templateUrl: './graph.page.html',
  styleUrls: ['./graph.page.scss'],
})
export class GraphPage implements OnInit {
  seed = '';
  depth = 1;
  graphData: any = null;

  loading = true;

  constructor(
    private route: ActivatedRoute,
    private graphService: GraphService,
  ) { }

  ngOnInit() {
    this.route.queryParams.subscribe((params) => {
      this.seed = params['seed'];
      this.depth = params['depth'] ?? 1;
      this.loadGraph();
    });
  }

  loadGraph() {
    this.loading = true;

    this.graphService.buildGraph(this.seed, this.depth).subscribe((data: any) => {
      this.graphData = data;
      this.loading = false;
    });
  }
}
