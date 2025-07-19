# Aprendendo sobre a dimensão das coisas

```{admonition} Conceitos
:class: note
- 🌘 Escalas de Tempo na Astronomia.
- 🌘 Movimentos da Terra.
- 🌘 Movimentos aparentes no céu.
- 🌘 Eclíptica.
- 🌘 Zodíaco.
- 🌘 Equador Celeste.
- 🌘 Coordenadas celestes horizontais.
- 🌘 Coordenadas celestes equatoriais.
- 🌘 O sistema ICRS
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

```

## Introdução

Embora parece evidente, para nós, que a Terra é redonda, que orbita em torno do Sol, que as distâncias entre os astros é verdadeiramente imensa e que o Sol é muito maior do que a Terra, estes fatos tem pouco de evidente e nós simplesmente aprendemos desde cedo os resultados de muitos séculos de ciência.

Estudar como a civilização conseguiu medir estas grandezas é um exercício que permite compreender a quantidade de sutilezas existentes nas observações que fazemos de coisas eternamente em movimento, em sistemas não inerciais, fora da zona de conforto dos cursos de Física Básica.

Nesta unidade vamos reproduzir as experiências de Eratóstenes, que determinou o raio da Terra, e de Aristarco, que tentou determinar as distâncias entre a Terra e a Lua e a Terra e o Sol.

Para reproduzir estes resultados vamos utilizar um código em Python e várias visualizações. Embora estejamos fazendo uma simulação, vamos tentar, a medida do possível, obter do código as grandezas que os idealizador dos experimentos poderiam obter com medições disponíveis à época.

Não há dificuldade técnica significativa no código, mas há muitos conceitos de Astronomia ali. É muito instrutivo que o leitor procure acompanhar o que o código faz.

### O experimento de Eratóstenes

```{margin}
:::{figure} ../../00_images/people/eratosthenes.jpg
:width: 50px
:align: left
:::

[biografia](#bio_eratostenes)

```

200 anos antes da era comum, o egípcio-grego **Eratóstenes** criou um método simples e engenhoso para determinar o raio da Terra. Foram necessárias algumas aproximações e uma certa dose de sorte para estar no lugar certo para fazer a medida.

Vamos simular esta medida e assim não vamos precisar contar os nossos passos em uma viagem de mais de 800 km, porque para isso utilizaremos um modelo geodésico.

````{sidebar}
```{hint}
Existe um projeto interessante de comemoração anual do *dia de Eratostenes* com escolas públicas de todo o mundo. [veja mais](https://eratosthenes.ea.gr/)
```
````

Embora a experiência pareça bem simples, existe uma riqueza de sutilezas que devem ser consideradas, e muito o que aprender.

Ele sabia que, no solstício de Verão, havia um poço na cidade de Aswan (na denominação moderna) que refletia o Sol ao meio-dia, portanto a sombra dos objetos verticais tinha comprimento zero e este raio de Sol deveria passar, no seu prolongamento, pelo centro da Terra.

Com uma geometria simples, medindo o tamanho da sombra em outro lugar, seria possível determinar o raio da Terra. A medida do tamanho da sombra foi realizada em Alexandria.

Uma imagem pode esclarecer a ideia.

```{figure} ../../00_images/cap_01/eratosthenes.jpg
:width: 70 %


Uma ideia sensacional. Créditos da figura [^1]
[^1]: <https://images.fineartamerica.com/images-medium-large-5/eratosthenes-experiment-science-photo-library.jpg>
```

Vamos então seguir o seguinte roteiro:

```{note}
:class:
:name: roteiro-eratostenes

1. Vamos obter as coordenadas geográficas das cidades de Alexandria e Aswan.
   1. Vamos usar a biblioteca `osmnx` para obter os objetos `geocode` como coordenadas **Lat** e **Lon**.
2. Utilizando `geopy` podemos obter a distância geodésica entre as duas cidades de maneira bastante direta.
3. Vamos escolher o ano $200 ac$ para nosso experimento, uma época em que o idealizador estava vivo.
4. Precisamos determinar o dia do solstício de verão.
   1. Vamos utilizar a biblioteca `skyfield` para realizar os cálculos astronômicos.
   2. Precisamos de informações sobre as posições do Sol e da Terra neste ano.
      1. O serviço de efemérides [JPL/NASA](https://naif.jpl.nasa.gov/naif/)  pode fornecer os dados que queremos.
5. Precisamos determinar o meio-dia local nas duas cidades.
   1. Já temos como calcular a posição do Sol, vamos determinar as passagens do Sol pelo meridiano local.
6. A partir do meio-dia em Aswan, vamos contruir um vetor de tempos com duração de duas horas e examinar o tamanho da sombra projetada pelo Sol nas duas cidades.
   1. $$ \mathcal{L} = \frac{h}{\mathrm{Alt_\odot}} $$
7. Vamos fazer uma visualização em 3D para ver como seria a sombra no chão.
8. Vamos fazer um gráfico com o tamanho das sombras.
9. Vamos obter uma estimativa do radio da Terra fazendo a mesma suposição de eratóstenes.
10. Vamos agora fazer um raciocínio inverso e usar nossos dados para obter a latitude e longitude e a partir destas informações calcular o Raio da Terra levando em conta as posições reais das cidades, que poderiam ser medidas na época antiga se houvessem relógios confiáveis.
```
