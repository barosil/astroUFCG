# Cosmologia

:::{error}
Este documento foi quase todo feito pelo DeepSeek e ainda não revisei tudo.

Trabalho em andamento.
:::

## Entropia, Temperatura e Desacoplamento de Neutrinos

### Entropia e Temperatura em Cosmologia

#### Definição de Entropia no Contexto Cosmológico

##### Definição e Importância da Entropia em Cosmologia

A entropia é uma quantidade fundamental em cosmologia que se conserva durante a expansão adiabática do universo. Sua densidade é crucial para entender:

- A formação de estruturas
- A nucleossíntese primordial
- A evolução térmica do universo
- O desacoplamento de partículas

### Densidade de Entropia

##### Primeira Lei da Termodinâmica

A primeira lei da termodinâmica para um sistema com número de partículas variável:

$$
dU = T dS - P dV + \mu dN
$$

onde:

- $U$ é a energia interna
- $T$ é a temperatura
- $S$ é a entropia
- $P$ é a pressão
- $V$ é o volume
- $\mu$ é o potencial químico
- $N$ é o número de partículas

Para sistemas homogêneos, trabalhamos com quantidades por unidade de volume:

- Densidade de energia: $\rho = U/V$
- Densidade de entropia: $s = S/V$
- Densidade numérica: $n = N/V$

A primeira lei torna-se:

$$
d(\rho V) = T d(sV) - P dV + \mu d(nV)
$$

Para radiação (fótons) ou quando $\mu = 0$ (como no universo primordial após o desaparecimento de assimetrias):

$$
d(\rho V) = T d(sV) - P dV
$$

Expandindo os diferenciais:

$$
V d\rho + \rho dV = T V ds + T s dV - P dV
$$

Reorganizando os termos:

$$
V d\rho + \rho dV - T V ds - T s dV + P dV = 0
$$

Agrupando termos com $dV$ e $ds$ separadamente:

$$
V d\rho - T V ds + (\rho - T s + P) dV = 0
$$

Para volume constante ($dV = 0$):

$$
V d\rho - T V ds = 0 \quad \Rightarrow \quad d\rho = T ds
$$

Portanto:

$$
ds = \frac{d\rho}{T}
$$

Para que a equação seja válida para variações arbitrárias de $s$ e $V$, ambos os coeficientes devem ser zero:

1. $d\rho - T ds = 0$
2. $\rho - T s + P = 0$

Da segunda equação:

$$
T s = \rho + P \quad \Rightarrow \quad s = \frac{\rho + P}{T}
$$

Para um gás de radiação (fótons):

- Densidade de energia: $\rho = \frac{\pi^2}{15} \frac{(kT)^4}{(\hbar c)^3}$
- Pressão: $P = \frac{1}{3} \rho$

Usando a relação demonstrada:

$$
s = \frac{\rho + P}{T} = \frac{\rho + \frac{1}{3}\rho}{T} = \frac{4}{3} \frac{\rho}{T}
$$

Substituindo $\rho$:

$$
s = \frac{4}{3} \frac{1}{T} \cdot \frac{\pi^2}{15} \frac{(kT)^4}{(\hbar c)^3} = \frac{4\pi^2}{45} \frac{k^4 T^3}{(\hbar c)^3}
$$

#### Entropia para Gás de Radiação

Para um gás de radiação em equilíbrio térmico, a densidade de entropia é dada por:

$$
s = \frac{\rho + P}{T}
$$

onde:

- $\rho$ é a densidade de energia
- $P$ é a pressão
- $T$ é a temperatura

Para radiação de corpo negro:

- $\rho = \frac{\pi^2}{30} g_* T^4$
- $P = \frac{1}{3} \rho$

Portanto:
$$
s = \frac{\frac{4}{3} \rho}{T} = \frac{4}{3} \frac{\pi^2}{30} g_* T^3 = \frac{2\pi^2}{45} g_* T^3
$$

#### Graus de Liberdade Efetivos

:::{figure} #entropia
:label: fig-entropia
:::

O parâmetro $g_*$ representa os graus de liberdade efetivos para entropia:

$$
g_* = \sum_{\text{bósons}} g_i + \frac{7}{8} \sum_{\text{férmions}} g_i
$$

onde $g_i$ são os graus de liberdade de cada espécie de partícula.

1. **Atualmente**:
   - Densidade de entropia: $s_0 \approx 2.89 \times 10^9 \, \text{m}^{-3}$
   - Razão entropia/fóton: $s/n_\gamma \approx 7.04$

2. **Na época da nucleossíntese** ($T \approx 10^9$ K):
   - Densidade de entropia: $s \approx 10^{41} \, \text{m}^{-3}$
   - Razão entropia/fóton: $s/n_\gamma \approx 7.26$

1. **Alta taxa de expansão**: A entropia domina a densidade de energia nos estágios iniciais
2. **Preservação de assimetrias**: A grande entropia por bárion ($\eta^{-1} \approx 10^9$) explica por que pequenas assimetrias matéria-antimatéria puderam levar à matéria dominante hoje
3. **Freeze-out de partículas**: A competição entre taxas de interação e expansão é governada pela densidade de entropia

Em cosmologia, a entropia é uma quantidade crucial que se conserva em processos adiabáticos (como a expansão do universo). Para um gás de radiação e partículas relativísticas:

A entropia comóvel por volume é dada por:

$$
s = \frac{2\pi^2}{45} g_{*s} T^3
$$

onde:

- $T$ é a temperatura
- $g_{*s}$ é o número efetivo de graus de liberdade de entropia

#### Conservação da Entropia

Durante a expansão adiabática do universo, a entropia total em um volume comovente se conserva:

$$
S = sa^3 = \text{constante}
$$

onde $a$ é o fator de escala. Isto implica que:

$$
g_{*s} T^3 a^3 = \text{constante}
$$

#### Relação entre Temperatura e Fator de Escala

Para a radiação (fótons), quando $g_{*s}$ é constante:

$$
T \propto a^{-1}
$$

## 2. Desacoplamento de Fótons e Neutrinos

### 2.1. O Processo de Desacoplamento

No universo primordial, fótons, elétrons, pósitrons e neutrinos estavam em equilíbrio térmico através de interações como:

$$
e^- + e^+ \leftrightarrow \gamma + \gamma
$$
$$
\nu + \bar{\nu} \leftrightarrow e^- + e^+
$$
$$
e^- + \nu \leftrightarrow e^- + \nu
$$

À medida que o universo se expandia e esfriava, as taxas de interação diminuíam.

### 2.2. Temperatura de Desacoplamento dos Neutrinos

Os neutrinos desacoplam quando a taxa de interação $\Gamma$ cai abaixo da taxa de expansão $H$:

$$
\Gamma(T_d) \approx H(T_d)
$$

Para neutrinos, isso ocorre quando:

$$
T_d^{\nu} \approx 1 \, \text{MeV} \quad (\approx 1.16 \times 10^{10} \, \text{K})
$$

### 2.3. O Efeito da Aniquilação $e^+e^-$

Pouco após o desacoplamento dos neutrinos, ocorre a aniquilação de elétrons e pósitrons:

$$
e^- + e^+ \to \gamma + \gamma
$$

Esta aniquilação aquece os fótons, mas não os neutrinos que já estão desacoplados.

### Determinação da Temperatura dos Neutrinos

#### Cálculo da Razão de Temperaturas

Antes da aniquilação $e^+e^-$ (T > 1 MeV):

- Fótons, elétrons, pósitrons e neutrinos em equilíbrio
- Todos à mesma temperatura: $T_\gamma = T_\nu$

Após a aniquilação $e^+e^-$:

- A entropia dos fótons é aumentada
- Os neutrinos não participam deste processo

A conservação da entropia permite calcular a nova razão de temperaturas.

#### Cálculo da Entropia

Antes da aniquilação ($T > 1$ MeV):

- $g_{*s} = g_\gamma + g_e + g_{\nu}$
- $g_\gamma = 2$ (2 polarizações)
- $g_e = g_{e^+} + g_{e^-} = \frac{7}{8} \times 2 \times 2 = \frac{7}{2}$ (elétron e pósitron, 2 estados de spin cada)
- $g_{\nu} = \frac{7}{8} \times 2 \times N_{\nu}$ (por neutrino, 2 estados de helicidade)

Para $N_{\nu} = 3$ (3 sabores de neutrino):

- $g_{*s} = 2 + \frac{7}{2} + \frac{7}{8} \times 6 = 2 + 3.5 + 5.25 = 10.75$

Após a aniquilação ($T < 1$ MeV):

- $g_{*s} = g_\gamma + g_{\nu} = 2 + \frac{7}{8} \times 6 = 2 + 5.25 = 7.25$

### 3.3. Razão de Temperaturas

Pela conservação da entropia:

$$
(g_{*s} T^3 a^3)_{\text{antes}} = (g_{*s} T^3 a^3)_{\text{depois}}
$$

Como os neutrinos já estavam desacoplados, $T_\nu^3 a^3$ é constante para eles. Para os fótons:

$$
(g_{*s} T_\gamma^3 a^3)_{\mathrm{antes}} = (g_{*s} T_\gamma^3 a^3)_{\mathrm{depois}}
$$

Mas como os neutrinos não participam da aniquilação:

$$
(T_\nu^3 a^3)_{\text{antes}} = (T_\nu^3 a^3)_{\text{depois}}
$$

Igualando as expressões:

$$
\left(\frac{T_\gamma}{T_\nu} \right)^3_{\text{depois}} = \frac{(g_{*s})_{\text{antes}}}{{(g_{*s})_{\text{depois}}}} = \frac{10.75}{7.25} \approx 1.48
$$

Portanto:

$$
\frac{T_\nu}{T_\gamma} = \left(\frac{4}{11}\right)^{1/3} \approx 0.714
$$

#### Temperatura Atual dos Neutrinos

Com a temperatura atual do CMB sendo $T_{\gamma,0} = 2.7255 \, \text{K}$:

$$
T_{\nu,0} = \left(\frac{4}{11}\right)^{1/3} T_{\gamma,0} \approx 1.945 \, \text{K}
$$

Em unidades de energia:

$$
kT_{\nu,0} \approx 1.676 \times 10^{-4} \, \text{eV}
$$

## 4. Implicações Observacionais

### 4.1. Densidade de Energia dos Neutrinos

A densidade de energia dos neutrinos relativísticos é:

$$
\rho_\nu = \frac{7}{8} N_{\text{eff}} \left(\frac{4}{11}\right)^{4/3} \rho_\gamma
$$

onde $N_{\text{eff}}$ é o número efetivo de espécies de neutrinos.

### 4.2. Constraints Observacionais

Medidas precisas do CMB (Planck) e de estrutura em grande escala restringem:

$$
N_{\text{eff}} = 3.04 \pm 0.08
$$

Consistente com três espécies de neutrinos relativísticos.

## 5. Resumo

| Quantidade | Valor | Significado |
|------------|-------|-------------|
| $T_d^\nu$ | ~1 MeV | Temperatura de desacoplamento dos neutrinos |
| $T_\nu/T_\gamma$ | $(4/11)^{1/3}$ | Razão de temperaturas após aniquilação $e^+e^-$ |
| $T_{\nu,0}$ | ~1.95 K | Temperatura atual dos neutrinos cósmicos |
| $N_{\text{eff}}$ | ~3.04 | Número efetivo de espécies de neutrinos |

:::{figure} #neutrinos
:label: fig-neutrinos
:::

## Nucleossíntese Primordial: Fundamentos e Cálculos

### Introdução à Nucleossíntese Primordial

A nucleossíntese primordial (Big Bang Nucleosynthesis - BBN) é o processo que ocorreu nos primeiros minutos após o Big Bang, quando os primeiros elementos leves foram formados. Este período crucial ocorreu entre aproximadamente 1 segundo e 20 minutos após o Big Bang.

### Interações Relevantes na Nucleossíntese Primordial

#### Reações Principais

As reações nucleares mais importantes durante a BBN são:

1. **Formação do Deutério**:
   - $p + n \leftrightarrow d + \gamma$

2. **Síntese de Hélio-3 e Trítio**:
   - $d + d \leftrightarrow ^3He + n$
   - $d + d \leftrightarrow t + p$

3. **Formação do Hélio-4**:
   - $d + t \leftrightarrow ^4He + n$
   - $d + ^3He \leftrightarrow ^4He + p$

4. **Produção de Lítio-7**:
   - $^4He + t \leftrightarrow ^7Li + \gamma$
   - $^4He + ^3He \leftrightarrow ^7Be + \gamma$
   - $^7Be + n \leftrightarrow ^7Li + p$

#### Equilíbrio Nuclear

A taxa de reações é governada pela equação:

$$
\frac{dY_i}{dt} = \sum_j k_{ij} Y_j - Y_i \sum_j k_{ji}
$$

onde $Y_i$ é a abundância do elemento i e $k_{ij}$ são as taxas de reação.

### Estimativa do Redshift da Nucleossíntese

#### Cálculo da Temperatura e Tempo

A nucleossíntese primordial ocorre quando a temperatura do universo atinge aproximadamente:

$$
T_{BBN} \approx 0.1 \text{ MeV} \approx 1.16 \times 10^9 \text{ K}
$$

Podemos relacionar o tempo cosmológico com a temperatura através da equação de Friedmann para um universo dominado por radiação:

$$
t = \frac{1}{2H} = \frac{1}{2} \sqrt{\frac{3}{8\pi G \rho_r}}
$$

onde a densidade de energia da radiação é:

$$
\rho_r = \frac{\pi^2}{30} g_* T^4
$$

com $g_*$ sendo o número efetivo de graus de liberdade.

#### Época da Nucleossíntese Primordial

- **Temperatura característica**: ~0.1 MeV (~1.16 × 10⁹ K)
- **Tempo correspondente**: ~100-200 segundos após o Big Bang
- **Redshift correspondente**: z ~ 10⁸-10⁹

#### Pontos Importantes

1. **Congelamento da razão n/p**: Ocorre em T ≈ 0.8 MeV (t ≈ 1 segundo), quando as interações fracas que convertem n ↔ p não conseguem mais acompanhar a expansão do universo.

2. **Formação do Deutério**: Começa em T ≈ 0.1 MeV (t ≈ 100 segundos), quando a densidade de fótons diminui o suficiente para evitar a fotodissociação imediata.

3. **Síntese dos elementos leves**: A maior parte do Hélio-4 é formada entre t ≈ 100-1000 segundos.

4. **Fim da BBN**: Por volta de t ≈ 20 minutos (T ≈ 0.03 MeV), as temperaturas são muito baixas para que ocorram mais reações nucleares.

#### Dependência com Parâmetros Cosmológicos

As abundâncias primordiais dependem criticamente de:

1. **Razão bárions-fótons (η)**: Determina a eficiência da nucleossíntese
2. **Número de espécies relativísticas (N_eff)**: Afeta a taxa de expansão do universo
3. **Tempo de vida do nêutron**: Influencia a razão n/p no congelamento

## Radiação Cósmica de Fundo: Desacoplamento e Recombinação

### Processo de Recombinação e Desacoplamento

#### Recombinação: Formação de Átomos Neutros

A recombinação é o processo onde elétrons e prótons se combinam para formar átomos de hidrogênio neutro. Este evento ocorreu quando o universo tinha aproximadamente 380.000 anos.

**Reação principal:**
$$
e^- + p^+ \leftrightarrow H + \gamma
$$

#### Desacoplamento: Liberação dos Fótons

O desacoplamento ocorre quando os fótons deixam de interager eficientemente com a matéria. Após a recombinação, o universo torna-se transparente à radiação, permitindo que os fótons viajem livremente - esta é a Radiação Cósmica de Fundo (CMB).

### Reações Relevantes

#### Processos de Ionização e Recombinação

1. **Fotoionização**: $H + \gamma \leftrightarrow e^- + p^+$
2. **Recombinação radiativa**: $e^- + p^+ \rightarrow H + \gamma$
3. **Ionização por colisão**: $e^- + H \leftrightarrow e^- + e^- + p^+$
4. **Recombinação tripla**: $e^- + e^- + p^+ \leftrightarrow e^- + H$

#### Taxa de Reações

A taxa de recombinação é dada por:
$$
\frac{dn_e}{dt} = -C_r n_e n_p + C_i n_H n_\gamma
$$
onde:

- $C_r$ é o coeficiente de recombinação
- $C_i$ é o coeficiente de ionização

### Equação de Saha para o Equilíbrio de Ionização

A equação de Saha descreve o equilíbrio entre átomos neutros, íons e elétrons:

$$
\frac{n_e n_p}{n_H} = \left(\frac{m_e k_B T}{2\pi \hbar^2}\right)^{3/2} e^{-\chi_H/k_B T}
$$

onde:

- $n_e$, $n_p$, $n_H$ são as densidades numéricas de elétrons, prótons e átomos de hidrogênio
- $\chi_H = 13.6$ eV é a energia de ionização do hidrogênio
- $m_e$ é a massa do elétron

#### Fração de Ionização

Definindo a fração de ionização:
$$
x_e = \frac{n_e}{n_e + n_H} = \frac{n_p}{n_b}
$$
onde $n_b = n_p + n_H$ é a densidade total de bárions.

A equação de Saha torna-se:
$$
\frac{x_e^2}{1 - x_e} = \frac{1}{n_b} \left(\frac{m_e k_B T}{2\pi \hbar^2}\right)^{3/2} e^{-\chi_H/k_B T}
$$

### Equação de Boltzmann para a Evolução da Ionização

Quando o universo se expande muito rapidamente para manter o equilíbrio térmico, usamos a equação de Boltzmann:

$$
\frac{dx_e}{dt} = -C_r \left[x_e^2 n_b - \frac{(1 - x_e)n_b}{\lambda(T)} e^{-\chi_H/k_B T}\right]
$$

onde:

- $C_r$ é o coeficiente de recombinação
- $\lambda(T) = \left(\frac{2\pi \hbar^2}{m_e k_B T}\right)^{3/2} n_b$

### Determinação do Redshift de Recombinação

#### Cálculo do Redshift

O redshift de recombinação é determinado resolvendo a equação de Saha ou Boltzmann para encontrar quando $x_e$ cai significativamente (tipicamente $x_e \approx 0.1$).

#### Redshift de Recombinação

- **Usando a equação de Saha**: z ≈ 1370
- **Usando a equação de Boltzmann**: z ≈ 1080

#### Tempo Correspondente

- **Recombinação (Saha)**: ≈ 240 mil anos após o Big Bang
- **Recombinação (Boltzmann)**: ≈ 380 mil anos após o Big Bang

#### Diferença entre as Abordagens

1. **Equação de Saha**: Assume equilíbrio térmico completo. É uma boa aproximação para redshifts mais altos, mas superestima o redshift de recombinação.

2. **Equação de Boltzmann**: Leva em conta o afastamento do equilíbrio térmico devido à expansão acelerada do universo. Fornece uma estimativa mais precisa do redshift de recombinação.

### Importância Cosmológica

O redshift de recombinação é crucial porque:

1. **Determina a idade do universo** quando a CMB foi emitida
2. **Influencia o espectro de anisotropias** da CMB
3. **Fornece constraints** sobre os parâmetros cosmológicos
4. **Define a escala do horizonte sonoro** no momento do desacoplamento
