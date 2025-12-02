import { HttpInterceptorFn, HttpResponse } from '@angular/common/http';
import { of } from 'rxjs';

export const mockBackendInterceptor: HttpInterceptorFn = (req, next) => {

  if (req.url.includes('/api/graph/build')) {

    const seed = req.params.get('seed') ?? 'Python';
    const depth = +(req.params.get('depth') ?? 1);

    const mockGraph = {
      nodes: [
        seed,
        "Programming",
        "Computer science",
        "Algorithm",
        "Mathematics",
        "Guido van Rossum",
        "Compilation",
        "Scripting language"
      ],
      links: [
        { source: seed, target: "Programming" },
        { source: seed, target: "Computer science" },
        { source: seed, target: "Scripting language" },
        { source: "Programming", target: "Algorithm" },
        { source: "Programming", target: "Mathematics" },
        { source: "Computer science", target: "Algorithm" },
        { source: "Computer science", target: "Compilation" },
        { source: "Guido van Rossum", target: seed }
      ]
    };

    return of(new HttpResponse({ status: 200, body: mockGraph }));
  }

  return next(req);
};

