import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { GraphService, GraphData } from '../../services/graph.service';
import { GraphViewerComponent } from '../../components/graph-viewer/graph-viewer.component';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-graph',
  standalone: true,
  imports: [CommonModule, GraphViewerComponent, RouterModule],
  templateUrl: './graph.page.html',
  styleUrls: ['./graph.page.scss'],
})
export class GraphPage implements OnInit {
  seed = '';
  depth = 1;
  graphData: GraphData | null = null;
  error: string | null = null;
  pageRankScores: { [title: string]: number } | null = null;

  loading = true;
  calculatingPageRank = false;

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
    this.pageRankScores = null;

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

  calculatePageRank() {
    if (!this.graphData) return;

    this.calculatingPageRank = true;
    this.error = null;

    this.graphService.calculatePageRank(this.graphData.nodes).subscribe({
      next: (response) => {
        this.pageRankScores = response.pagerank;
        this.calculatingPageRank = false;
        console.log('PageRank calculado:', this.pageRankScores);
      },
      error: (err) => {
        console.error('Erro ao calcular PageRank:', err);
        this.error = err.error?.detail || 'Erro ao calcular PageRank';
        this.calculatingPageRank = false;
      }
    });
  }
}
