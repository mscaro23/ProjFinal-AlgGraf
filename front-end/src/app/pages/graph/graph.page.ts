import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { GraphService, GraphData } from '../../services/graph.service';
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
  graphData: GraphData | null = null;
  error: string | null = null;

  loading = true;

  constructor(
    private readonly route: ActivatedRoute,
    private readonly graphService: GraphService,
  ) { }

  ngOnInit() {
    this.route.queryParams.subscribe((params) => {
      this.seed = params['seed'];
      this.depth = +(params['depth'] ?? 1); // Converte para número
      this.loadGraph();
    });
  }

  loadGraph() {
    this.loading = true;
    this.error = null;

    // Observable: "escuta" a resposta da API
    this.graphService.buildGraph(this.seed, this.depth).subscribe({
      next: (data) => {
        // Sucesso: dados chegaram
        this.graphData = data;
        this.loading = false;
        console.log(`Grafo carregado: ${data.nodes.length} nós, ${data.links.length} arestas`);
      },
      error: (err) => {
        // Erro: algo deu errado
        console.error('Erro ao carregar grafo:', err);
        this.error = err.error?.detail || 'Erro ao carregar o grafo';
        this.loading = false;
      }
    });
  }
}
