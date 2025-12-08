import { Routes } from '@angular/router';
import { HomePage } from './pages/home/home.page';
import { GraphPage } from './pages/graph/graph.page';
import { PagerankPage } from './pages/pagerank/pagerank.page';

export const routes: Routes = [
  { path: '', component: HomePage },
  { path: 'graph', component: GraphPage },
  { path: 'pagerank', component: PagerankPage },
  { path: '**', redirectTo: '' },
];
