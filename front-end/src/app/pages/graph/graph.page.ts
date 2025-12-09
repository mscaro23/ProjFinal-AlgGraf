import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { GraphService } from '../../services/graph.service';
import { GraphViewerComponent } from '../../components/graph-viewer/graph-viewer.component';
import { NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

@Component({
  selector: 'app-graph',
  standalone: true,
  imports: [NgIf, GraphViewerComponent, FormsModule],
  templateUrl: './graph.page.html',
  // styleUrl: './graph.page.scss',
})
export class GraphPage implements OnInit {
  seed = '';
  depth = 1;
  graphData: any = null;

  loading = false;
  calculatingPageRank = false;
  findingPaths = false;

  // Para busca de caminhos
  sourcePageTitle = '';
  targetPageTitle = '';
  sourcePageId: number | null = null;
  targetPageId: number | null = null;
  pathsResult: any = null;

  // Resultado do PageRank
  pageRankResult: any = null;

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

  calculatePageRank() {
    this.calculatingPageRank = true;
    this.pageRankResult = null;

    this.graphService.calculatePageRank().subscribe({
      next: (result: any) => {
        this.pageRankResult = result;
        this.calculatingPageRank = false;
        // Recarrega o grafo para mostrar os novos PageRanks
        if (this.seed) {
          this.loadGraph();
        }
      },
      error: (error: any) => {
        console.error('Erro ao calcular PageRank:', error);
        this.calculatingPageRank = false;
        alert('Erro ao calcular PageRank: ' + (error.error?.detail || error.message));
      }
    });
  }

  async findPaths() {
    if (!this.sourcePageTitle.trim() || !this.targetPageTitle.trim()) {
      alert('Por favor, preencha ambos os títulos das páginas');
      return;
    }

    this.findingPaths = true;
    this.pathsResult = null;

    try {
      // Primeiro, busca os IDs das páginas pelos títulos
      const sourcePage = await firstValueFrom(this.graphService.getPageByTitle(this.sourcePageTitle));
      const targetPage = await firstValueFrom(this.graphService.getPageByTitle(this.targetPageTitle));

      if (!sourcePage || !targetPage) {
        alert('Uma ou ambas as páginas não foram encontradas');
        this.findingPaths = false;
        return;
      }

      this.sourcePageId = sourcePage.page_id;
      this.targetPageId = targetPage.page_id;

      // Agora busca os caminhos
      this.graphService.findPaths(this.sourcePageId, this.targetPageId).subscribe({
        next: (result: any) => {
          this.pathsResult = result;
          this.findingPaths = false;
        },
        error: (error: any) => {
          console.error('Erro ao buscar caminhos:', error);
          this.findingPaths = false;
          alert('Erro ao buscar caminhos: ' + (error.error?.detail || error.message));
        }
      });
    } catch (error: any) {
      console.error('Erro ao buscar páginas:', error);
      this.findingPaths = false;
      alert('Erro ao buscar páginas: ' + (error.error?.detail || error.message || 'Erro desconhecido'));
    }
  }
}
