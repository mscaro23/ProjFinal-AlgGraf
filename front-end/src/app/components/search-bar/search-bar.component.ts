import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-search-bar',
  templateUrl: './search-bar.component.html',
  styleUrls: ['./search-bar.component.scss'],
  imports: [FormsModule]
})
export class SearchBarComponent {
  @Input() value: string = '';
  @Output() valueChange = new EventEmitter<string>();
}
