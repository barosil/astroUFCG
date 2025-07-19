# Medindo o Sol e a Lua

```{admonition} Conceitos
:class: note
- 🌘 Eclipses Solares
- 🌘 Eclipses Lunares
- 🌘 Zodíaco
- 🌘 Eclíptica.
- 🌘 Tamanho e distância relativos da Terra, Sol e Lua.
```

```{admonition} Bibliotecas Utilizadas
|**Biblioteca**   | **Utilização** |
|--------------|---------------|
|**skyfield** | Skyfield calcula posições para estrelas, planetas e satélites em órbita ao redor da Terra. Seus resultados devem concordar com as posições geradas pelo Observatório Naval dos Estados Unidos e seu Almanaque Astronômico dentro de 0,0005 segundos de arco (metade de um "mas" ou milissegundo de arco).
|**jplephem** | Este pacote pode carregar e usar uma efeméride do Laboratório de Propulsão a Jato (JPL) para prever a posição e velocidade de um planeta ou outro corpo do Sistema Solar. Atualmente suporta arquivos SPK binários (extensão .bsp) como aqueles distribuídos pelo Laboratório de Propulsão a Jato.|
| **pandas**| pandas é uma ferramenta de análise e manipulação de dados de código aberto rápida, poderosa, flexível e fácil de usar, construída sobre a linguagem de programação|
| **matplotlib**| Matplotlib é uma biblioteca de plotagem 2D do Python que produz figuras de qualidade de publicação em uma variedade de formatos impressos e ambientes interativos em diferentes plataformas. Matplotlib pode ser usado em scripts Python, nos shells Python e IPython, no notebook Jupyter, servidores de aplicações web e quatro kits de ferramentas de interface gráfica do usuário.|
| **pyvista** | PyVista é uma biblioteca auxiliar para o Toolkit de Visualização (VTK) que adota uma abordagem diferente para interfacear com o VTK através do NumPy e acesso direto a arrays. Este pacote fornece uma interface pythônica e bem documentada que expõe o poderoso backend de visualização do VTK para facilitar a prototipagem rápida, análise e integração visual de conjuntos de dados com referência espacial.|
| **sunpy** |Sunpy é um pacote de software livre e de código aberto desenvolvido pela comunidade para física solar. Seu objetivo é ser um ambiente abrangente de análise de dados que permita que pesquisadores da área de física solar realizem suas tarefas com o mínimo de esforço.|
| **píllow**|Pillow é uma biblioteca de processamento de imagens poderosa e amplamente utilizada para Python. É uma bifurcação ativamente mantida da Python Imaging Library (PIL) original, que não é mais desenvolvida. Pillow amplia os recursos da PIL e oferece suporte para versões modernas do Python (incluindo Python 3), bem como uma gama mais ampla de formatos e funcionalidades de arquivos de imagem.|
| **Astropy**| O Projeto Astropy é um esforço da comunidade para desenvolver um pacote básico comum para Astronomia em Python e promover um ecossistema de pacotes de astronomia interoperáveis.|
| **skimage**|scikit-image é uma coleção de algoritmos para processamento de imagens. Está disponível gratuitamente e sem restrições . Nos orgulhamos de oferecer código de alta qualidade, revisado por pares, escrito por uma comunidade ativa de voluntários .|

```

## Introdução

Pouco tempo antes de Eratóstenes, de maneira concomitante com a formalização da geometria por Euclides, Aristarco, na pequena ilha de Samos, no mar Egeu setentrional, planejava medir o Sol e a Lua, tanto o seus raios como suas distâncias.

Se sua ambição parecia desmedida, para um ambiente de tão pequenina ilha, lembremos que ela ali o templo principal de Hera, que ali também viveram Pitágoras,Esopo, Heródoto e Epicuro.

Num momento em que se conheciam propriedades trigonométricas e alguns importantes conceitos de geometria plana, mas não existiam os conceitos de funções trigonométricas, e mesmo o número zero era usado com certa recalcitrância na comunidade grega, Aristarco coloca seu intelecto em uma tarefa brilhante, mas impossível.

```{margin}
:::{figure} ../../00_images/processed/0002_quadrado_thumbnail.png
:width: 50px
:align: left
:::

[biografia](#bio_aristarco)

```

```{note}
:class:
:name: roteiro-aristarco
- Observações de eclipses solares totais deixaram claro que os diâmetros angulares desdes dois corpos são iguais.
    - Vamos confirmar este fato analisando fotos de eclipses e aplicando técnicas de processamento de imagens, obter informações para comparar uma foto comum com imagens científicas com ricos metadados.
- Quando a lua se apresenta meio-cheia, no início da fase de quarto crescente ou minguante, a Lua deve ser o vértice de um ângulo reto, feito com a Terra e o Sol.
    - Se for possível medir o ângulo entre o Sol e a Lua neste momento, poderemos determinar as distâncias relativas entre o Sol e a Lua, bem como seus raios relativos.
- Observando uma eclipse lunar total com cuidado, medindo o tempo que a Lua demora para percorrer porções da sombra da Terra, também é possível medir as distâncias relativas dos astros.
```

O método de Aristarco não tem nenhuma falha, mas veremos que ainda não haviam inventado os instrumentos necessários para realizar as medidas necessárias.

Mesmo obtendo valores bem distantes daqueles hoje aceitos, Aristarco concluiu que o Sol era bem maior do que a Terra e distante, o que o levou a postular um modelo heliocêntrico.

A cultura grega da época sabia o suficiente para refutar o argumento de Aristarco, não havia sido observado nenhum fenômeno de paralaxe que justificasse a terra estar a se mover. Uma objeção que foi verdadeira até o ano de 1838, quando Friedrich Bessel conseguiu medir a paralaxe da estrela *61 Cygni*.

A medida da distância do Sol realizada por Aristarco foi aceita até a época de Tycho Brahe.
