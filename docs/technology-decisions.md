# V1 technology decisions

| Decision | Reason | Revisit when |
| --- | --- | --- |
| Native browser modules and CSS | All screens use one authenticated household projection. Semantic HTML, browser navigation and native controls can ship directly. Next.js adds package installation, a compiler and a rendering runtime. | Several clients need shared typed components or server rendering has a measured benefit. |
| One Python process with an HTTP API | The available standard library can serve a loopback evaluation build and execute short database transactions. | Before a networked pilot, move the request handlers behind a maintained production server with TLS, rate limits and monitoring. |
| SQLite | Transactions keep source review and plan revisions consistent. One local file keeps the operating cost and setup small. | Multiple application hosts or sustained write contention justify a managed relational database. |
| A bounded review workflow | Language interpretation can eventually propose fields. Application code owns authorization, state transitions and source references. | Model evaluations establish that adding a model reduces total review time and missed obligations. |
| Explicit text intake | Families can choose a single message without granting access to an entire mailbox. | Consented research demonstrates a high-value source that text intake cannot handle. |

Next.js documents its package and build requirements in its [installation guide](https://nextjs.org/docs/app/getting-started/installation). SQLite describes low-administration and single-host use in [Appropriate Uses for SQLite](https://www.sqlite.org/whentouse.html). Python explicitly limits the deployment suitability of its [standard HTTP server](https://docs.python.org/3/library/http.server.html).
