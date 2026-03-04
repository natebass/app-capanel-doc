---
myst:
  html_meta:
    "description lang=en": |
      View education standards with the California Accountability Panel.
html_theme.sidebar_secondary.remove: true
---

California Accountability Panel
===============================

A dashboard that displays key school performance metrics.

```{gallery-grid}
:grid-columns: 1 2 2 3

- header: "{fas}`chart-simple;pst-color-primary` Dashboard panel"
  content: "View key school performance metrics and California state-wide metrics.\n- View our [website](https://lbsis.org)."
- header: "{fas}`circle-user;pst-color-primary` Who it's for"
  content: "For people who want real‑time, personalized performance data.\n- Guardians\n- Schools\n- Educational Policy Makers"
- header: "{fas}`gauge-simple-high;pst-color-primary` Metrics"
  content: "Metrics are based on student assessment results and other aspects of school performance."
- header: "{fas}`database;pst-color-primary` Public data"
  content: "Uses public data from the [California Department of Education](https://www.cde.ca.gov/)."
- header: "{fas}`file-csv;pst-color-primary` CSV upload"
  content: "Use your own data by uploading a CSV file."
- header: "{fas}`lightbulb;pst-color-primary` Contribute"
  content: "We welcome contributions! The project is open-source.\n- [GitHub](https://github.com/opensacorg/app-capanel-web)\n- [GitHub docs](https://github.com/opensacorg/app-capanel-doc)"
```

## User guide

Information about using the California Accountability Panel website.

```{toctree}
:maxdepth: 2

user-guide/index
```

## Developer guide

Information about developing this application and how you can contribute.

```{toctree}
:maxdepth: 2

developer-guide/index
```

## API reference

The application uses FastAPI. You can view the Open API docs at [lbsis.org/docs](https://lbsis.org/docs) or view the
full Python module
reference.

```{toctree}
:maxdepth: 2

developer-guide/all-modules
```