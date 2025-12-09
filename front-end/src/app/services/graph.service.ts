import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class GraphService {
  private baseUrl = 'http://localhost:8080';

  constructor(private http: HttpClient) { }

  buildGraph(seed: string, depth: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/api/graph/build`, {
      params: { seed, depth: depth.toString() },
    });
  }

  calculatePageRank(d: number = 0.85, maxIter: number = 100, tol: number = 1e-6): Observable<any> {
    return this.http.post(`${this.baseUrl}/api/pagerank/calculate`, null, {
      params: {
        d: d.toString(),
        max_iter: maxIter.toString(),
        tol: tol.toString(),
      },
    });
  }

  findPaths(sourcePageId: number, targetPageId: number, maxDepth: number = 10): Observable<any> {
    const params = new HttpParams()
      .set('source_page_id', sourcePageId.toString())
      .set('target_page_id', targetPageId.toString())
      .set('max_depth', maxDepth.toString());
    
    return this.http.get(`${this.baseUrl}/api/paths`, { params });
  }

  getPageByTitle(title: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/api/pages/title/${encodeURIComponent(title)}`);
  }
}
