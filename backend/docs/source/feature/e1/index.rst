Performance Cards
================================================================
.. toctree::
  :hidden:
  :caption: Epic E1
  :maxdepth: 1

  f1
  f2
  f3
  f4
  f5
  f6

What is it?
---------------------

A dashboard that displays key school performance metrics.

Purpose
---------------------
To provide educators, parents, and policymakers with easy access to school performance data to inform decision-making and drive improvements.


Background
---------------------
The website is built on top of more than a decade worth of California education policy,
so understanding the history of that policy is essential to understanding the data we are showing you today.
It all starts with the Local Control Funding Formula (LCFF), passed by the California Legislature and signed into law in July 2013 [1],
which fundamentally overhauled the state’s K-12 accountability and funding model.
This overhaul created a multi-indicator accountability system that drives not only every metric you see on our website
but how schools ensure that academic achievement is aligned with their expenditures[2]. The overhaul called for a shift in California's school
funding streams to be based on a formula that gives additional resources to schools that are continuously improving academic and behavioral outcomes for
high-need students (e.g., English learners, low-income, foster youth, special education)[3].

As a result of this legislation, schools now need to create Local Control and Accountability Plans (LCAPs),
which outline their goals and strategies for continuously improving outcomes for high-need students. 
To assist schools in this effort, the state developed a system to provide parents and guardians with meaningful information on school and district 
progress of these outcomes so they can participate in decisions to improve student learning. Working with stakeholders, the state developed the 
"California School Dashboard", which displays the schools performance on these outcomes[4].


Problem we are solving
---------------------
The section that we have seen that has that most technological need is the section that displays 
the California School Dashboard color-coded system to indicate performance levels, ranging from red (lowest) to blue (highest).
It based on multiple measures, including test scores, graduation rates, and suspension rates. 
The challenge is to present this data in an actionable timeframe, while ensuring privacy, accuracy, 
and clarity for diverse audiences. More specifically, this data is currently released once a year,
which means that any changes made based on the data take a long time to be reflected in the dashboard.
This lag makes it difficult for stakeholders to make timely decisions and adjustments to improve student outcomes.




Who it serves
---------------------

The following people who want real‑time, personalized performance data

  -  Guardians
  -  Schools
  -  Educational Policy Makers

How it works
---------------------

.. mermaid::


   flowchart TD
       %% Data Ingestion
       subgraph A[Data Ingestion]
           A1[Fetch from API]
           A2[Manual upload]
       end

       %% Business Rules
       subgraph B[Business Rules]
           B1[Map raw values → status/change levels]
           B2[Handle uncertified / small-N cases]
       end

       %% Presentation
       subgraph C[Presentation]
           C1[React/Tailwind cards]
           C2[Accessible colors]
           C3[Responsive layout]
       end

       %% Persistence
       subgraph D[Persistence]
           D1[Optional backend storage]
           D2[Local SQLite]
       end

       %% Connect the main nodes
       A --> B --> C --> D
_____


FAQs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


**Q: What measures are included on the Performance Cards?**

A: The Performance Cards include the following measures:
    - English
    - Math
    - Science
    - Progress of English as a Second Language Learners
    - Suspension Rates
    - Chronic Absenteeism
    - Graduation Rate
    - College/Career Readiness

**Q: How often are the Performance Cards updated?**

A: The publicly displayed Performance Cards are updated annually, typically in the fall, to reflect the most recent data available from the CDE.
However, If you are using a local or private instance of the Performance Cards application,
you can update the data as frequently as needed by re-ingesting the latest data from your sources.
Feel free to look into the documentation for guidance on how to update the data in your specific setup.

**Q: Where can I find more information about the Performance Cards?**


A:  For detailed information about the Performance Cards, including technical documentation and data sources, please visit the
California Department of Education's Performance Cards webpage: `CDE Performance Cards <https://www.cde.ca.gov/ta/ac/cm/performancecards.asp>`_.
For questions or assistance regarding the Performance Cards, you can contact the CDE directly at
`CDE Contact Page <https://www.cde.ca.gov/re/di/or/contactus.asp>`_. Additionally, you can refer to the
components documentation within this project for more insights on how to we calculate and display the measures.



Citation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **[1]California Department of Education.** *Local Control Funding Formula (LCFF).* California Department of Education, n.d.  
  `https://www.cde.ca.gov/fg/aa/lc/ <https://www.cde.ca.gov/fg/aa/lc/>`_

- **[2]California Legislature.** *Assembly Bill 97, Chapter 47 (2013).* California Legislative Information, 2013.  
  `https://www.leginfo.ca.gov/pub/13-14/bill/asm/ab_0051-0100/ab_97_cfa_20130614_153238_asm_floor.html <https://www.leginfo.ca.gov/pub/13-14/bill/asm/ab_0051-0100/ab_97_cfa_20130614_153238_asm_floor.html>`_

- **[3]California Department of Education.** *Local Control and Accountability Plan (LCAP).* California Department of Education, n.d.  
  `https://www.cde.ca.gov/re/lc/ <https://www.cde.ca.gov/re/lc/>`_

- **[4]California School Dashboard.** *California School Dashboard.* State of California — California Department of Education.  
  `https://www.caschooldashboard.org/ <https://www.caschooldashboard.org/>`_


