## Instruções de uso do llama Launcher versão 1.40 🦙  

O 🦙 llama Launcher é uma aplicação ultra leve e multiplataforma (testado em Windows e Linux), feito 100% em Python para executar modelos de linguagem (GGUF) com o poderoso llama.cpp. Oferece GUI simplificada com configuração e salvamento de parâmetros, suporte multimodal (mmproj) e aceleração por GPU (se disponível) com foco em privacidade - tudo rodando 100% local no seu computador.

**Aviso Legal / Disclaimer**

O llamaLauncher é um lançador de código aberto que facilita a execução de binários do llama.cpp (projeto MIT do repositório https://github.com/ggml-org/llama.cpp) e de modelos GGUF compatíveis.
O autor **não** é responsável, de forma alguma, pelo uso que os usuários venham a fazer da ferramenta ou dos modelos carregados por ela.
Em particular, o autor **não endossa nem se responsabiliza** por:
- Conteúdo gerado pelos modelos (incluindo, mas não limitado a: desinformação, discurso de ódio, conteúdo ilegal, difamação, violação de direitos autorais);
- Uso dos modelos em desacordo com as licenças respectivas; e
- Qualquer dano direto ou indireto causado pelo uso ou pelos outputs gerados.
O software é fornecido "como está", sem garantias de qualquer espécie (expressas ou implícitas), incluindo, mas não se limitando a, garantias de adequação a um propósito específico, não violação de direitos ou funcionamento ininterrupto.
O uso desta ferramenta é de exclusiva responsabilidade do usuário final, que deve respeitar todas as leis aplicáveis, as licenças dos modelos e as políticas de uso aceitável dos provedores originais.

### 1. Baixar o Modelo no Hugging Face (HF)

#### 1.1. Acesse → https://huggingface.co
#### 1.2. No campo de busca digite: `GGUF` + nome do modelo desejado (exemplos: `Qwen3.5`, `GLM-4.7`, `OSS`, `DeepSeek-R1` etc.).
#### 1.3. Clique em um repositório confiável (por exemplo: bartowski, unsloth, lmstudio-community ou o oficial do modelo).
#### 1.4. Vá na aba "Files and versions".
#### 1.5. Baixe o arquivo "alguma coisa.gguf", optando por alguma das recomendações de qualidade/velocidade a seguir:
   - `Q4_K_M.gguf` ou `Q5_K_M.gguf` → ótimo equilíbrio (muito utilizado);
   - UD-Q4_K_XL → Considerado por muitos a melhor combinação de desempenho e qualidade;
   - `Q8_0.gguf` → máxima qualidade (usa mais RAM/VRAM); e
   - `IQ4_XS.gguf` ou `Q3_K_M.gguf` → se quiser economizar memória e ainda ter uma qualidade razoável.
#### 1.6. Se quiser suporte multimodal (imagens / áudio / vídeo):
   - No mesmo repositório, baixe também o arquivo que termina com **`-mmproj.gguf`** (ex: `<nome-do-modelo-mmproj-F16>.gguf`). Se tiver limitação de hardware, opte pela quantização F16 do mmproj. Em regra geral utilize sempre o mmproj F16 por ser mais leve e ser uma boa combinação de desempenho e qualidade.
   - Atenção! O nome base deve ser igual ao do modelo principal para que o launcher detecte automaticamente a associação entre eles.
   - Por exemplo: o usuário foi no repositório do Unsloth e baixou o modelo: Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf. Esse modelo tem função de visão. Para que a função de visão funcione, o mmproj respectivo deverá ser renomeado para o seguinte nome de arquivo: Qwen3.5-35B-A3B-UD-Q4_K_XL-mmproj-F16.
#### 1.7. Abra e feche o llamaLauncher para criar automaticamente as pastas "bin" e "models" dentro da pasta "_internal" e mova os arquivos ".gguf" e ".mmproj" para "models".

✅ Pronto! O launcher vai mostrar o modelo na lista (com prefixo 👀 se for multimodal).

### 2. Baixar e Colocar o llama.cpp na Pasta `bin` (conforme seu hardware)

#### 2.1. Vá direto na página oficial mais atualizada  
**https://github.com/ggml-org/llama.cpp/releases/latest**

#### 2.2. Escolha o pacote com os binários (executáveis), exatamente conforme sua máquina

Na seção de releases, você encontrará a versão mais recente com vários arquivos compactados (.zip ou .tar.gz) com binários pré-compilados do llama.cpp para diferentes sistemas operacionais e tipos de aceleração de hardware.
Baixe o arquivo que melhor corresponde à sua configuração:

- Se você usa apenas CPU (sem placa de vídeo dedicada), escolha uma variante “CPU only” ou “x64” / “ubuntu-x64” / “macos-arm64” etc.;
- Se tem placa NVIDIA, procure variantes com CUDA (ex.: CUDA 12.x ou 13.x, dependendo da sua versão de driver e da idade da placa).;
- Se tem placa AMD ou Intel Arc, as opções mais comuns são as baseadas em Vulkan (geralmente funcionam bem em Windows e Linux).; e
- Para macOS (Apple Silicon ou Intel), há pacotes específicos com aceleração Metal.

**Dica importante:** as opções exatas e os nomes dos arquivos podem mudar um pouco a cada release. Leia com atenção as orientações disponíveis para escolher a versão correta para o seu sistema e hardware. Caso ainda tenha dúvida sobre qual baixar, a variante CPU-only é a mais segura e compatível com qualquer máquina (embora seja mais lenta por não utilizar GPU).

#### 2.3. Como instalar

##### 2.3.1. Baixe o binário e as bibliotecas necessárias de llama Cpp
##### 2.3.2. Abra e feche o llamaLauncher para criar automaticamente as pastas "bin" e "models" dentro da pasta "_internal"
##### 2.3.3. Extraia os binários e bibliotecas do llama Cpp, adequados ao seu hardware, para a pasta `bin`. São diversos arquivos etc., inclusive:
   - `llama-server` e `llama-cli` (quando Linux); ou
   - `llama-server.exe` e `llama-cli.exe` (quando Windows).
   
##### 2.3.4. **Importante para alguns casos de Linux** → dê permissão de executável para:
   ```bash
   chmod +x llama-server
   chmod +x llama-cli
   ```

### 3. Usar o llama Launcher (GUI)

#### 3.1. Execute o programa:
   - Linux → `llamaLauncher`
   - Windows → `llamaLauncher.exe`

#### 3.2. Primeira tela:
   - O dropdown já mostra todos os modelos da pasta `models/`;
   - Modelos multimodais aparecem com 👀; e
   - Status à direita mostra “✅ + Multi” ou “📄 Só Chat”.

#### 3.3. Configurações rápidas (todas têm tooltip explicativo ao passar o mouse):
   - **Camadas na GPU** (`-ngl`): `auto` ou `999` (usa tudo) → reduza se der erro de VRAM;
   - **Threads**: `auto` (padrão);
   - **Tamanho do Contexto**: 4096–32768 (depende do modelo);
   - **Multimodal** (checkbox): marque se quiser usar imagens (só aparece em modelos com mmproj); e
   - Outros parâmetros (temperatura, mirostat, XTC etc.) têm valores comuns e explicação.
   
   **Obs.:** as configurações padrão desses parâmetros atendem a maioria das situações para a maioria dos modelos. Havendo necessidade de ajustar os parâmetros em função de situações específicas (por exemplo: conversas mais longas, codificação, respostas mais objetivas, menos repetição etc.), basta proceder com as alterações e clicar no botão de salvar. Ao fazer isso, as configurações ficarão salvas em um arquivo ".txt" que será criado com o mesmo nome do modelo correspondente. dessa forma, sempre que retornar a esse modelo, os valores salvos serão carregados automaticamente. Para retornar com as configurações padrão, basta clicar no botão de "Restaurar valores padrão" e depois clicar em "Salvar configurações deste modelo" ou apagar o ".txt" que foi criado, clicando no botão "Abrir pasta models" para proceder com uma exclusão manual do arquivo ".txt"

#### 3.4. Escolha o modo:
   - **SERVER**: habilita o modo servidor (http://127.0.0.1:8080); e
   - **CLI**: habilita o modo cliente, abrindo um terminal separado para conversa direta.

#### 3.5. Clique no botão 🚀 (lançar) para carregar o modelo.

**O que acontece depois**:
- **Modo Server**: depois que carregar o modelo, clique no botão "Abrir navegador" para abrir interface completa com chat, upload documentos, vídeos, áudios, imagens (quando aplicável), histórico etc.; e
- **Modo CLI**: abre janela de terminal nativa (que também permite iterar com arquivos, ainda que de maneira mais limitada, quando há recurso multimodal).

### 4. Dicas gerais

- Primeira vez: ao abrir o programa ele criará as pastas `models/` e `bin/` automaticamente, dentro de "_internal";
- Para atualizar: basta baixar a release mais nova (de acordo com o seu sistema operacional e hardware) do llama.cpp e substituir os arquivos na pasta `bin/`;
- Multimodal desativado = mais rápido e usa menos VRAM (desmarque a checkbox “Multimodal” se não for usar esse recurso);
- API Key (proteção): só funciona se o IP for 0.0.0.0 (acesso na rede local). Por padrão vem configurado em loopback (127.0.0.1) para impedir que outros acessem. As Configurações gerais de IP, porta, API Key são salvas em `config.txt`;
- Problemas comuns:
  - “Binário não encontrado” → verifique pasta `bin/`;
  - “VRAM insuficiente” → ajuste para `-ngl 30` ou `auto`; e
  - CUDA não detectado → verifique versão do CUDA e use o pacote correto + DLLs.

Com esses passos você tem o launcher mais simples, prático, rápido e atualizado possível para utilização de modelos locais.

Divirta-se com o llamaLauncher! 🦙

## Apêndice: Escolhendo os GGUFs
(Fonte: Hugging Face, Llama Cpp)

### A. Orientações gerais

- **CPU-only (sem GPU)**: O modelo inteiro vai para RAM. Se não couber → swapping lento ou crash.
- **SSD/NVMe**: Ganho **enorme**! Carregamento inicial 5–10× mais rápido. Se o modelo for um pouco maior que a RAM, o swapping fica viável (sem NVMe fica insuportável).
- **GPU**: Acelera **10–100×** os tokens/s. Quanto mais VRAM, mais layers offload (--n-gpu-layers). Ideal: VRAM ≥ tamanho modelo + KV = full offload (velocidade máxima). Parcial offload ainda ajuda muito.

- **Quantizações recomendadas**:

  - Prefira Q4_K_M, Q5_K_M (ainda melhor para maior precisão matemática) ou **UD-Q4_K_XL** (Unsloth Dynamic) - melhor qualidade com tamanho parecido ao do Q4_K_M.
  - Alta qualidade: Q6_K e/ou qualquer variante deste (acima disto, em 95% dos casos, não precisa, basta usar o Q5_K_M ou o UD-Q4_K_XL).
  - Economia extrema mantendo ainda um custo x benefício razoável: IQ4_XS / Q3_K_M (mas teste a qualidade, vai ter perda, dependendo do trabalho).
  - Evite Q8_0 e suas variações ou superior em hardware limitado (arquivo muito grande).

- **Tamanho real total ocupado na memória** = modelo (arquivo GGUF) + mmproj (suporte multimodal, caso exista) + overhead + KV Cache.

#### A.1. Incremento de 2 a 4GB de overhead (sistema + contexto)

Isso significa que, além do tamanho do arquivo GGUF (ex: 11 GB de um modelo MoE OSS de 20B com quantização UD-Q4_K_XL), o programa de inferência (no caso o llamaLauncher com o llamaCpp) precisa de mais 2 a 4 GB de RAM/VRAM só para “funcionar”.

O que compõe esse overhead?

Sistema/inferência: O próprio motor do llama.cpp (ou o backend) necessita de algum espaço em memória. Ele carrega bibliotecas, threads, buffers internos, etc.

Contexto inicial: Todo prompt que você digita (system prompt + sua primeira mensagem) já consome um pouquinho de memória. Um prompt longo de 500–1000 tokens pode adicionar 0,5–1 GB.
Outros detalhes técnicos: Metadados do modelo, tensor de embedding, layernorm, etc. — coisas que não estão “dentro” do arquivo GGUF, mas são criadas na hora de carregar.

Exemplo:

Modelo: Um arquivo GGUF de 12 GB de tamanho
Overhead: 2 GB (uma média)
Total mínimo para carregar: 14 GB de RAM e/ou VRAM

Se você tiver só 16 GB de RAM total sem GPU (configuração muito comum), sobram uns 2 GB para o sistema operacional + KV cache. Por isso o modelo cabe “justinho”. Se o overhead for 4 GB (prompt muito longo + programa pesado), você já sente o PC usar swap (e fica lento).

#### A.2. KV cache de ~0.5 a 2GB por 8k a 32k tokens

O KV cache é a parte mais importante (e que mais confunde) para quem usa contexto longo.
O que é o KV cache?
É uma “memória de curto prazo” que o modelo guarda para lembrar tudo o que foi dito até agora. Sem ele, toda vez que você digitasse uma nova frase, o modelo teria que recalcular do zero (ficaria absurdamente lento).
Ele armazena dois vetores por token anterior:

K = Key (chave)
V = Value (valor)

Quanto mais tokens no contexto, maior fica esse cache.
Por que o tamanho varia de 0.5–2 GB?
Depende do modelo (número de camadas, tamanho dos vetores de atenção) e da quantização:

Modelos pequenos (4B-7B) → cache menor (~0.5 GB para 8k)
Modelos maiores (14B–32B) → cache maior (~1.5–2 GB para 32k)

Regra prática:

4K-8k tokens (contexto curto, conversa normal): ~0.5–1 GB
16k–32k tokens (conversa longa ou código grande): ~1–2 GB
64k tokens: dobra (fica ~2–4 GB), porque é proporcional ao número de tokens

Exemplo com o modelo 20B MoE em computador com 16GB RAM sem GPU:

Arquivo: 11 GB
Overhead: +3 GB
Contexto de 8k: +0.8 GB de KV cache
Total usado na RAM: 11 + 3 + 0.8 = 14.8 GB → cabe em 16 GB.

Se você aumentar o contexto para 32k:

KV cache → ~1.6 GB
Total: 16.6 GB → já começa a usar um pouquinho de swap (se tiver NVMe ou SSD, ainda roda ok; sem SSD, muito lento e pode travar).

Em 64k:

KV cache → ~3.2 GB
Total: ~18 GB → só roda bem com 32 GB de RAM ou com GPU offloading.

Por que o SSD/NVMe é tão importante aqui?
Se o KV cache + modelo não couberem 100% na RAM, o sistema “troca” partes para o disco (swapping). Com NVMe ou SSD isso funciona melhor; com HDD normal fica insuportável (velocidade cai para 1–2 tokens/segundo).
Resumo rápido para você usar no dia a dia
Modelo 11 GB + overhead médio 3 GB + KV cache desejado:

8k–16k contexto → precisa de ~15 GB RAM total
32k contexto → ~16–17 GB
64k contexto → ~19 GB (só com 32 GB de RAM e/ou GPU)

### B. Distinção importante: Densos × MoE
- **Densos**: Ativam todos os parâmetros o tempo todo. Memória e velocidade seguem o total de parâmetros.
  **Regra prática**: Com 16GB de RAM, acima de ~9B com quantização **maior que Q5_K_M não roda bem** em CPU-only - fica lento demais e/ou não cabe direito na RAM.

- **MoE**: (ex: Qwen-MoE, gpt-oss-20B, Mixtral etc.): Ativam só parte dos experts (ex: gpt-oss-20B tem 21B total mas só ~3.6B ativos).
  **Velocidade e qualidade** = no geral é melhor do que o denso em computadores mais modestos!
  **Vantagem enorme**: Você roda modelos maiores e mais inteligentes em um hardware mais simples.

**Exemplo**: gpt-oss-20B UD-Q4_K_XL (~11 GB) → roda **rápido** em CPU-only com 16 GB RAM com NVME ou SSD (e ainda sobra espaço pro contexto). É MoE, por isso fica rápido!

#### B.1. Tabela 1: CPU-only (sem GPU) - Recomendação por RAM
(Contexto 8k–32k, quant Q4_K_M ou UD-Q4_K_XL)

| RAM do PC     | Máx. Denso (total params) | Exemplo denso (GGUF) | Máx. MoE (total params) | Exemplo MoE (GGUF)                          |
|--|--|--|--|--|
| **8 GB**  | 4B  | Qwen3.5-4B, Gemma 3-4B, Llama 3.2-3B | 20B    | gpt-oss-20B |
| **16 GB** | 9B  | Qwen3.5-9B, Qwen3-8B, Llama 3.1-8B   | 30–35B | Qwen3.5-35B-A3B, Qwen3-30B-A3B |
| **32 GB** | 14B | Qwen3-14B, Gemma3-12B                | 80B    | Qwen3-Next-80B-A3B-Instruct |
| **64 GB** | 32B | Qwen3.5-27B, Qwen3-32B               | 109B   | Llama-4-Scout-17B-16E |

- Se o modelo for um pouco maior que a RAM → use **IQ3_M** ou **UD-Q3_K_M** (perde alguma qualidade mas ganha 20–30% de espaço).
- NVMe muda **tudo**: em 16 GB + NVMe você consegue rodar até o Qwen3-30B-A3B com 32k de contexto com um pouquinho de swap que não chega a inviabilizar o uso.

- Acima de 9B, prefira Q4_K_M ou inferior. Q5_K_M+ só se tiver RAM sobrando.

#### B.2. Tabela 2: Com GPU — VRAM para full offload
(Contexto 8k–32k, quant Q4_K_M ou UD-Q4_K_XL)

| VRAM da GPU   | Máx. Denso full offload     | Máx. MoE full offload       | Velocidade (t/s) |
|---------------|-----------------------------|-----------------------------|--------------------------|
| 8 GB          | ~9B                         | ~14B           | 30–60 t/s    |
| 12 GB         | ~14B                        | ~20–27B        | 40–80 t/s    |
| 16 GB         | ~20B                        | ~35B           | 50–100 t/s   |
| 24 GB         | ~32B                        | ~70B           | 70–150 t/s   |
| 32 GB+        | ~70B                        | ~100B          | 100–200 t/s  |
