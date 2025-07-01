% This defines the footer of the site, and is not parsed as a regular "page"
% We point to it with the following in `myst.yml`:
% site:
% parts:
% footer: footer.md

% Here we use `grid` to add a basic grid structure to the HTML,
% but the formatting column sizes are defined manually in css/footer.css
% see the `grid-template-columns` line.
:::::{grid} 3 3 5 5
:class: outer-grid col-screen

<!-- Project description -->

::::{div}

# Um livro criado com {MyST}

```{image} ../images/logo-wide.svg
:width: 150px
:align: left
```

Utilizando MyST-markdown, jupyter, sphinx e LaTeX.
::::

<!-- Spacer between project description and links columns -->

::::{div}
::::

<!-- Link columns -->

% This a _second_ grid embedded within the first one, to create nicer
% responsive design experience. This grid will have a single column on narrow screens,
% and fan out into three columns on wide screens. However, it always remains within
% its parent grid column.
::::{grid} 1 1 3 3

:::{div}

- [About the author](frontmatter/about_author.md)
- [MyST](https://mystmd.org)
- [Jupyter Book](https://github.com/jupyter-book)
  :::

:::{div}
:::

:::{div}
:::

::::

::::: 
