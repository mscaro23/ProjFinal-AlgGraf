import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class GraphService {
  private baseUrl = 'http://localhost:8000/api/graph';

  constructor(private http: HttpClient) { }

  buildGraph(seed: string, depth: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/build`, {
      params: { seed, depth },
    });
  }
}
