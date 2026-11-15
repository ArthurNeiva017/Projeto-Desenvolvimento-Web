# 🎬 CineTrack

> Plataforma web para gerenciamento pessoal de filmes e séries.

**Instituição:** Centro Universitário de Brasília (UniCEUB)  
**Curso:** Análise e Desenvolvimento de Sistemas (ADS)  
**Disciplina:** Desenvolvimento Web  
**Turma / Semestre:** 2026.2  
**Professor:** Felippe Pires Ferreira  
**Status do projeto:** Em desenvolvimento

---

## Sumário

- [1. Descrição do projeto](#1-descrição-do-projeto)
- [2. Funcionalidades](#2-funcionalidades)
- [3. Demonstração](#3-demonstração)
- [4. Tecnologias utilizadas](#4-tecnologias-utilizadas)
- [5. Arquitetura](#5-arquitetura)
- [6. Organização dos diretórios](#6-organização-dos-diretórios)
- [7. Participantes](#7-participantes)
- [8. Como executar](#8-como-executar)
- [9. Configuração](#9-configuração)
- [10. Testes](#10-testes)
- [11. Uso de inteligência artificial](#11-uso-de-inteligência-artificial)
- [12. Contribuição e fluxo de trabalho](#12-contribuição-e-fluxo-de-trabalho)
- [13. Histórico de versões](#13-histórico-de-versões)
- [14. Limitações e próximos passos](#14-limitações-e-próximos-passos)
- [15. Licença, referências e contato](#15-licença-referências-e-contato)

---

## 1. Descrição do projeto

O **CineTrack** é uma aplicação web voltada para a organização pessoal de filmes e séries. A plataforma permitirá que usuários mantenham uma biblioteca com os títulos que desejam assistir, estão assistindo ou já assistiram.

A aplicação busca resolver a dificuldade de organizar conteúdos de diferentes tipos em um único lugar. Além do cadastro manual, o sistema utilizará uma API externa de filmes e séries para auxiliar na consulta de informações dos títulos.

O CineTrack também permitirá pesquisar conteúdos cadastrados, registrar avaliações e acompanhar informações da biblioteca por meio de indicadores e relatórios.

### Objetivos

**Objetivo geral:**

Desenvolver uma aplicação web utilizando Python e Django que permita ao usuário organizar e acompanhar filmes e séries em uma biblioteca pessoal.

**Objetivos específicos:**

- Permitir o cadastro e gerenciamento de filmes e séries.
- Permitir a classificação dos títulos por status.
- Permitir a pesquisa de títulos cadastrados.
- Permitir que o usuário registre notas e comentários.
- Integrar dados de filmes e séries utilizando uma API externa.
- Apresentar indicadores e relatórios sobre a biblioteca.
- Disponibilizar parte dos dados por meio de uma API REST própria.
- Desenvolver uma interface responsiva para computadores e dispositivos móveis.

### Público-alvo

- Pessoas que assistem filmes e séries com frequência.
- Usuários que desejam organizar os conteúdos que pretendem assistir.
- Usuários que desejam manter um histórico dos títulos já assistidos.

---

## 2. Funcionalidades

| Funcionalidade | Descrição | Status |
|---|---|---|
| Autenticação | Login e logout de usuários | Planejada |
| Biblioteca pessoal | Visualização dos filmes e séries adicionados pelo usuário | Planejada |
| Cadastro de títulos | Adicionar filmes e séries à biblioteca | Planejada |
| Edição de títulos | Alterar informações de registros existentes | Planejada |
| Exclusão de títulos | Remover registros da biblioteca | Planejada |
| Busca | Pesquisar filmes e séries cadastrados | Planejada |
| Filtros | Filtrar títulos por tipo, gênero ou status | Planejada |
| Status | Classificar títulos como "Quero assistir", "Assistindo" ou "Assistido" | Planejada |
| Avaliação | Registrar nota e comentário sobre um título | Planejada |
| Dashboard | Apresentar indicadores gerais da biblioteca | Planejada |
| Relatórios | Exibir dados consolidados sobre filmes e séries cadastrados | Planejada |
| API REST própria | Disponibilizar dados selecionados da aplicação em JSON | Planejada |
| Integração externa | Consultar informações de filmes e séries em uma API externa | Planejada |

### Requisitos não funcionais

- **Desempenho:** a aplicação deverá responder às operações comuns de forma adequada para uso normal.
- **Segurança:** senhas deverão ser armazenadas de forma segura pelo mecanismo de autenticação do Django e a aplicação deverá utilizar HTTPS em produção.
- **Usabilidade:** a interface deverá ser simples, intuitiva e de fácil utilização.
- **Responsividade:** as páginas deverão funcionar adequadamente em computadores e dispositivos móveis.
- **Disponibilidade:** a versão final deverá permanecer publicada durante o período de avaliação.
- **Manutenibilidade:** o código deverá seguir uma organização compatível com a estrutura de projetos Django.
---

## 3. Demonstração

*Inclua capturas de tela, GIF ou link para vídeo. Coloque as imagens em `images/`.*

![Tela principal](images/[screenshot-principal].png)

| Tela | Descrição |
| --- | --- |
| [Login] | [Acesso ao sistema com e-mail e senha] |
| [Painel] | [Visão geral das reservas do dia] |

**Vídeo / protótipo:** [URL do YouTube, Loom ou Figma]

---

## 4. Tecnologias utilizadas

As tecnologias previstas inicialmente são:

| Camada | Tecnologia | Versão |
|---|---|---|
| Linguagem | Python | 3.12+ |
| Frontend | Django Templates, HTML, CSS e Bootstrap | Bootstrap 5.3 |
| Backend | Django | 6.1 |
| API REST | Django REST Framework | 3.18 |
| Autenticação da API | djangorestframework-simplejwt (JWT) | 5.5 |
| Documentação da API | drf-spectacular (Swagger / Redoc) | 0.30 |
| Banco de dados | SQLite | — |
| API externa | TMDB API (consumida com `requests`) | v3 |
| Controle de versão | Git e GitHub | — |
| Testes | `unittest` do Django (`manage.py test`) | — |



---

## 5. Arquitetura

*Explique como o sistema está organizado: camadas, principais componentes e o fluxo entre eles. Inclua um diagrama no PDF de arquitetura ou de classes em `docs/` e descreva-o em texto.*

[Ex.: a solução segue uma arquitetura em camadas (apresentação, aplicação, domínio e persistência). O frontend consome uma API REST. O backend aplica as regras de negócio e persiste os dados no banco.]

```text
[Usuário] → [Interface / Frontend] → [API / Backend] → [Banco de dados]
```

**Decisões relevantes:**

- [Ex.: uso de API REST para separar cliente e servidor.]
- [Ex.: persistência relacional porque os dados possuem relacionamentos bem definidos.]

### Apps do projeto Django

| App | Responsabilidade |
| --- | --- |
| `contas` | Página inicial, cadastro, login e logout de usuários |
| `biblioteca` | Models (Gênero, Título, Item da biblioteca, Avaliação), CRUD e busca na biblioteca |
| `tmdb` | Integração com a API externa TMDB (busca e importação de títulos) |
| `avaliacoes` | Registro de nota e comentário dos títulos |
| `relatorios` | Dashboard, relatório com filtros, impressão e exportação CSV |
| `api` | API REST própria (DRF, JWT e Swagger) |

### Endpoints principais

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/api/v1/titulos/` | Lista o catálogo (filtros `busca`, `tipo`, `genero`, `ano`) |
| `GET` | `/api/v1/generos/` | Lista os gêneros |
| `GET` / `POST` | `/api/v1/biblioteca/` | Lista ou adiciona itens da biblioteca (JWT) |
| `GET` / `PUT` / `PATCH` / `DELETE` | `/api/v1/biblioteca/{id}/` | Consulta, altera ou remove um item (JWT) |
| `POST` | `/api/v1/biblioteca/{id}/avaliar/` | Avalia um item (JWT) |
| `GET` | `/api/v1/biblioteca/relatorio/` | Indicadores da biblioteca (JWT) |
| `POST` | `/api/token/` | Obtém o token JWT |

Documentação completa da API: [`docs/api/README.md`](docs/api/README.md) e Swagger em `/api/docs/swagger/`.

---

## 6. Organização dos diretórios

*Mantenha a árvore alinhada à estrutura real do repositório. Ajuste pastas conforme o tipo de projeto.*

```text
.
├── README.md                 # Documentação principal do projeto
├── .env.example              # Modelo de variáveis de ambiente (sem segredos)
├── docs/                     # Modelagem e demais artefatos técnicos (PDF)
│   ├── README.pdf            # Índice da pasta docs/
│   └── modelagem/
│       ├── casos-de-uso/
│       │   └── especificacoes-casos-de-uso.pdf
│       ├── classes/
│       │   └── diagrama-de-classes.pdf
│       └── banco-de-dados/
│           ├── diagrama-er.pdf
│           └── modelo-logico.pdf
├── images/                   # Figuras da documentação geral (ex.: política de IA)
├── src/                      # Código-fonte da aplicação
│   ├── frontend/             # Interface com o usuário (quando houver)
│   └── backend/              # Regras de negócio, API e acesso a dados (quando houver)
├── tests/                    # Testes automatizados
└── scripts/                  # Scripts auxiliares de setup, build ou deploy
```

| Diretório / arquivo | Função |
| --- | --- |
| `README.md` | Apresentação do projeto, objetivos, tecnologias e instruções de uso |
| `.env.example` | Lista das variáveis necessárias, sem credenciais reais |
| `docs/` | Artefatos de análise e modelagem em PDF |
| `docs/modelagem/` | Casos de uso, classes e modelo de dados (diagramas embutidos nos PDFs) |
| `images/` | Figuras da documentação geral do repositório (não usar para diagramas de modelagem) |
| `src/` | Código-fonte organizado por camada ou módulo |
| `tests/` | Casos de teste e evidências de verificação |
| `scripts/` | Automação de ambiente e execução |

---

## 7. Participantes

| Nome | Matrícula | Função no projeto |
|---|---|---|
| Arthur Barroso Neiva | 22510032 | FrontEnd e BackEnd |
| David Silveira Maciel | A informar | Documentação e Testes |
| Guilherme Meyer Soares | 22504716 | BackEnd e FrontEnd |
| João Vitor Belchior Estanislau | A informar | Banco de Dados e BackEnd |


**Professor(a) responsável:** Felippe Pires Ferreira

---

## 8. Como executar

*Preencha com os comandos reais do projeto para que outra pessoa consiga reproduzir o ambiente.*

### Pré-requisitos

- Git
- Python 3.12+

### Instalação e execução

```bash
# 1. Clonar o repositório
git clone https://github.com/ArthurNeiva017/Projeto-Desenvolvimento-Web.git
cd Projeto-Desenvolvimento-Web/cinetrack

# 2. Criar e ativar o ambiente virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
copy .env.example .env       # Windows (Linux/macOS: cp .env.example .env)
# edite o .env: SECRET_KEY e TMDB_API_KEY

# 5. Criar o banco e um administrador
python manage.py migrate
python manage.py createsuperuser

# 6. Executar a aplicação
python manage.py runserver
```

**Acesso local:** http://127.0.0.1:8000 (Swagger: http://127.0.0.1:8000/api/docs/swagger/)

---

## 9. Configuração

*Liste as variáveis de ambiente usadas pelo sistema. Nunca publique senhas, tokens ou chaves neste arquivo.*

| Variável | Obrigatória | Descrição | Exemplo |
| --- | --- | --- | --- |
| `SECRET_KEY` | Sim | Chave de sessão e de assinatura do JWT | `[gerar localmente]` |
| `TMDB_API_KEY` | Sim | Chave da API do TMDB | `[obter em themoviedb.org]` |

Credenciais reais devem ficar apenas no arquivo `.env` (não versionado).

---

## 10. Testes

*Descreva como executar os testes e o que eles cobrem.*

```bash
cd cinetrack
python manage.py test
```

| Tipo | Ferramenta | O que verifica |
| --- | --- | --- |
| Views e regras de negócio | `django.test.TestCase` | Cadastro, login, CRUD, busca, avaliação, relatório e CSV |
| Integração externa | `unittest.mock` | TMDB: sucesso, timeout, falha de conexão, limite (429) e resposta inválida |
| API REST | `rest_framework.test.APITestCase` | JWT, CRUD, filtros, paginação, códigos HTTP e isolamento entre usuários |
| Segurança | Bandit, pip-audit e OWASP ZAP | Ver [`docs/seguranca/`](docs/seguranca/README.md) |

---

## 11. Uso de inteligência artificial

Este repositório segue a política de uso de IA da disciplina (semáforo pedagógico):

![Política de uso de IA — semáforo](images/semaforo.png)

| Situação | Significado |
| --- | --- |
| **Vermelho — uso proibido** | Atividades de autonomia intelectual (ex.: provas presenciais sem consulta). |
| **Amarelo — uso limitado** | IA pode ser ferramenta auxiliar, desde que haja declaração de uso. |
| **Verde — uso permitido** | Uso livre ao longo da atividade acadêmica. |

### Declaração de uso

*Preencha de forma honesta. Se não houve uso de IA, declare explicitamente.*

- **Houve uso de IA neste projeto?** [Sim / Não]
- **Ferramentas utilizadas:** [Ex.: ChatGPT, GitHub Copilot, Gemini — ou “nenhuma”]
- **Finalidade:** [Ex.: revisão de texto, geração de esboço de testes, esclarecimento de dúvidas de sintaxe]
- **O que NÃO foi delegado à IA:** [Ex.: definição do problema, modelagem, implementação das regras de negócio, testes finais]

---

## 12. Contribuição e fluxo de trabalho

*Padronize o trabalho em equipe. Ajuste as regras ao combinado da disciplina.*

### Branches

- `main` — versão estável para avaliação
- `develop` — integração do grupo *(opcional)*
- `feat/[nome]` — nova funcionalidade
- `fix/[nome]` — correção de defeito
- `docs/[nome]` — alterações só de documentação

### Commits

Use mensagens curtas e no imperativo, por exemplo:

- `feat: adiciona cadastro de reservas`
- `fix: corrige validação de data`
- `docs: atualiza instruções de execução`

### Passos sugeridos

1. Criar uma branch a partir de `main`.
2. Implementar e testar localmente.
3. Abrir um *pull request* / *merge request* para revisão do grupo.
4. Só então integrar à branch principal.

**Issues e quadro de tarefas:** [link do GitHub Projects, Trello ou similar]

---

## 13. Histórico de versões

*Registre entregas relevantes (sprints, checkpoints ou versões avaliadas).*

| Versão | Data | Descrição |
| --- | --- | --- |
| `0.1.0` | [AAAA-MM-DD] | [Ex.: primeira versão executável / MVP] |
| `0.0.1` | [AAAA-MM-DD] | [Ex.: estrutura inicial do repositório] |

---

## 14. Limitações e próximos passos

### Problemas conhecidos

- [Ex.: a recuperação de senha ainda não envia e-mail]
- [Ex.: o layout quebra em telas menores que 360 px]

### Roadmap

- [ ] [Ex.: autenticação com dois fatores]
- [ ] [Ex.: exportação de relatórios em CSV]
- [ ] [Ex.: implantação em ambiente de homologação]

---

## 15. Licença, referências e contato

**Licença:** [Ex.: uso exclusivamente acadêmico / MIT / outro]

Este material destina-se a fins educacionais. Verifique com a disciplina se o código pode ser reutilizado fora do curso.


### Referências

- [Autor. Título. Ano. URL ou dados bibliográficos.]
- [Documentação oficial da tecnologia X.]

### Contato

Dúvidas sobre o projeto: [e-mail institucional do grupo ou issue no repositório]

**Agradecimentos:** [Ex.: professor(a), monitoria, materiais da disciplina]
