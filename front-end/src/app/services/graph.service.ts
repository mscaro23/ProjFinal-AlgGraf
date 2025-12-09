import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface GraphLink {
  source: string;
  target: string;
}

export interface GraphData {
  nodes: string[];
  links: GraphLink[];
}

@Injectable({ providedIn: 'root' })
export class GraphService {
  private readonly baseUrl = 'http://localhost:8000/api/graph';

  constructor(private readonly http: HttpClient) { }

  buildGraph(seed: string, depth: number): Observable<GraphData> {
    return this.http.get<GraphData>(`${this.baseUrl}/build`, {
      params: { seed, depth: depth.toString() },
    });
  }
}
