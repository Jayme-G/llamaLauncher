# 🦙 llama Launcher - Versão 1.40 para Linux e Windows

## 1. Sobre o llamaLauncher (Frontend)

O 🦙 llama Launcher é uma aplicação ultra leve e multiplataforma (testado em Windows e Linux), feito 100% em Python para executar modelos de linguagem (GGUF) com o poderoso llama.cpp. Oferece GUI simplificada com configuração e salvamento de parâmetros, suporte multimodal (mmproj) e aceleração por GPU (se disponível) com foco em privacidade - tudo rodando 100% local no seu computador.

## 2. Aviso Legal / Disclaimer

O llamaLauncher é um lançador de código aberto que facilita a execução de binários do llama.cpp (projeto MIT do repositório https://github.com/ggml-org/llama.cpp) e de modelos GGUF compatíveis.
O autor **não** é responsável, de forma alguma, pelo uso que os usuários venham a fazer da ferramenta ou dos modelos carregados por ela.
Em particular, o autor **não endossa nem se responsabiliza** por:
- Conteúdo gerado pelos modelos (incluindo, mas não limitado a: desinformação, discurso de ódio, conteúdo ilegal, difamação, violação de direitos autorais);
- Uso dos modelos em desacordo com as licenças respectivas; e
- Qualquer dano direto ou indireto causado pelo uso ou pelos outputs gerados.
O software é fornecido "como está", sem garantias de qualquer espécie (expressas ou implícitas), incluindo, mas não se limitando a, garantias de adequação a um propósito específico, não violação de direitos ou funcionamento ininterrupto.
O uso desta ferramenta é de exclusiva responsabilidade do usuário final, que deve respeitar todas as leis aplicáveis, as licenças dos modelos e as políticas de uso aceitável dos provedores originais.

## 3. Licença do llamaLauncher (Frontend)

MIT License

Copyright (C) 2026 Jayme Gonçalves

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Veja em: https://opensource.org/licenses/MIT

## 4. Bibliotecas utilizadas (último acesso aos links das fontes a seguir ocorreu em 08/03/2026):

- os          - módulo da biblioteca padrão do Python que oferece uma interface portátil para funcionalidades dependentes do sistema operacional (manipulação de arquivos/diretórios, variáveis de ambiente, processos etc.). Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/os.html e https://docs.python.org/3/license.html.
- sys         - módulo da biblioteca padrão do Python que fornece acesso a parâmetros e funções específicas do interpretador e do sistema (como argumentos de linha de comando, versão do Python, caminhos de busca etc.). Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/sys.html e https://docs.python.org/3/license.html.
- subprocess  - módulo que permite gerenciar subprocessos, conectar-se aos seus pipes de entrada/saída/erro e obter seus códigos de retorno. Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/subprocess.html e https://docs.python.org/3/license.html.
- threading   - módulo da biblioteca padrão do Python que fornece suporte a programação concorrente baseada em threads. Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/threading.html e https://docs.python.org/3/license.html.
- platform    - módulo da biblioteca padrão do Python que fornece informações sobre a plataforma subjacente (sistema operacional, arquitetura, etc.). Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/platform.html e https://docs.python.org/3/license.html.
- webbrowser  - módulo da biblioteca padrão do Python que permite abrir URLs em navegadores web de forma portátil. Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/webbrowser.html e https://docs.python.org/3/license.html.
- shlex       - módulo da biblioteca padrão do Python para analisar sintaxe estilo shell (dividir comandos em argumentos). Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/shlex.html e https://docs.python.org/3/license.html.
- shutil      - módulo da biblioteca padrão do Python que oferece operações de alto nível em arquivos e coleções de arquivos (cópia, movimentação, remoção, arquivamento etc.). Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/shutil.html e https://docs.python.org/3/license.html.
- queue       - módulo da biblioteca padrão do Python que implementa filas thread-safe (FIFO, LIFO, PriorityQueue etc.), muito usado em programação concorrente. Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/queue.html e https://docs.python.org/3/license.html.
- json        - módulo da biblioteca padrão do Python para codificação e decodificação de JSON. Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/json.html e https://docs.python.org/3/license.html.
- tkinter     - biblioteca de interface gráfica do usuário (GUI) Python de código aberto, incluída na biblioteca padrão. Ela está licenciada sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/tkinter.html e https://docs.python.org/3/license.html.
- PIL         - Pillow (fork amigável do Python Imaging Library - PIL) - biblioteca para processamento e manipulação de imagens. Licenciada sob a HPND (Historical Permission Notice and Disclaimer), equivalente à antiga licença do PIL (MIT-like). Veja em: https://pillow.readthedocs.io/en/stable/ e https://github.com/python-pillow/Pillow/blob/main/LICENSE
- datetime    - módulo da biblioteca padrão do Python para manipulação de datas e horas. Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/datetime.html e https://docs.python.org/3/license.html.

## 5. Backend license:

llama.cpp - Engine de inferência de Large Language Models (LLM) em C/C++ de alto desempenho, com suporte a vários backends (CPU, GPU via CUDA/Metal/Vulkan/etc.) e formato GGUF. É a base principal deste launcher para execução local de modelos de linguagem. Licenciado sob a MIT License. Veja em: https://github.com/ggml-org/llama.cpp e https://github.com/ggml-org/llama.cpp/blob/master/LICENSE

## 6. Empacotador:

pyinstaller - ferramenta que permite empacotar uma aplicação python e todas as suas dependências em um único pacote. Ele está licenciado sob uma licença dual, usando tanto a licença GPL 2.0, com uma exceção que permite usá-lo para construir produtos comerciais e a licença Apache, versão 2.0. Veja em: <https://pyinstaller.org/en/stable/license.html>.
