import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { SearchBarComponent } from '../../components/search-bar/search-bar.component';

Component;

@Component({
  selector: 'app-home',
  templateUrl: './home.page.html',
  styleUrls: ['./home.page.scss'],
  imports: [FormsModule, SearchBarComponent, RouterModule]
})
export class HomePage {
  query: string = '';
  depth: number = 1;

  constructor(private router: Router) { }

  generateGraph() {
    if (!this.query.trim()) return;
    this.router.navigate(['/graph'], {
      queryParams: {
        seed: this.query,
        depth: this.depth,
      },
    });
  }
}
