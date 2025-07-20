# Exercícios

```{exercise} Fazendo uma carta celeste
:label: carta_celeste
- Escolha as coordenadas geográficas que deseja utilizar.
- Escolha um ano e um mês.
- Determine o dia e hora em que começa a lua crescente.
- Faça uma carta celeste para este dia com os seguintes elementos
    - Sistema Solar: Lua, Sol e planetas até saturno.
    - Estrelas de magnitude $m<6$
    - Asterismos para as constelações do zodíaco.
    - Marcação das regiões das constelações de acordo com a IAU.
    - Cada constelação do zodíaco com uma cor diferente.
    - O gráfico deve ter o Norte para cima e o Leste para a direita.
    - O gráfico deve estar em coordenadas horizontais, com o zênite no centro.
    - Inclua o equador celeste e a eclíptica.
    - O gráfico deve ter uma projeção polar adequada a uma carta celeste.
    - Reproduza o mesmo gráfico, desta vez com a projeção Mollweide e em coordenadas equatoriais.

**Limites de Constelações**: [Vizier](https://vizier.cds.unistra.fr/vizier/VizieR/constellations.htx)

**Linhas das constelações**: [GitHub](https://github.com/MarcvdSluys/ConstellationLines)

**Catálogo Hiparco**: [Vizier](https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=1239/hip_main)

**Ferramentas** 
- Astroquery 
- Matplotlib 
- Pandas 
- Astropy 
- Skyfield
```

```{exercise} Como Kepler determinou as óribtas?
:label: kepler

Vamos reproduzir as medidas e análises de Kepler com respeito à órbita de Marte. 
- Você pode utilizar a biblioteca Skyfield para obter os dados, caso não queira, você pode fazer a partir da tabela de dados originais.
- A parte importante é explicar o raciocínio, mais do que obter a resposta numérica correta.

1. Determine os nós da órbita de marte, ou seja, os pontos em que a órbita de marte cruza a eclíptica.
2. Determine o período da órbita, usando estes pontos como base.
3. Calcule a inclinação da órbita com respeito a órbita da terra. (*Kepler não fez suposições específicas sobre a forma da órbita, mas nós vamos usar o nosso conhecimento de que a órbita é plana)
4. Determine as coordenadas de oposição total.
5. Determine a órbita.

Referência: [Kepler's Battle with the Mars orbit](https://studenttheses.uu.nl/bitstream/handle/20.500.12932/19118/Koot%202014%20-%20Keplers%20battle%20with%20the%20Mars%20orbit.pdf?sequence=2)

```
