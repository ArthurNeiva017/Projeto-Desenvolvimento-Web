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
| Linguagem | Python | A definir |
| Frontend | HTML, CSS e JavaScript | — |
| Backend | Django | A definir |
| API REST | Django REST Framework | A definir |
| Banco de dados | SQLite / banco relacional compatível com produção | A definir |
| API externa | TMDB API | — |
| Controle de versão | Git e GitHub | — |
| Testes de API | Postman | — |



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

### Endpoints principais (quando houver API)

| Método | Rota | Descrição |
| --- | --- | --- |
| `POST` | `/api/[recurso]` | [Ex.: criar um registro] |
| `GET` | `/api/[recurso]` | [Ex.: listar registros] |
| `GET` | `/api/[recurso]/{id}` | [Ex.: obter um registro] |
| `PUT` | `/api/[recurso]/{id}` | [Ex.: atualizar um registro] |
| `DELETE` | `/api/[recurso]/{id}` | [Ex.: remover um registro] |

Documentação completa da API: [link para Swagger, Postman ou `docs/api.md`]

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
| Arthur Barroso Neiva | A informar | FrontEnd |
| David Silveira Maciel | A informar | Documentação e Testes |
| Guilherme Meyer Soares | A informar | BackEnd e FrontEnd |
| João Vitor Belchior Estanislau | A informar | Banco de Dados e BackEnd |


**Professor(a) responsável:** Felippe Pires Ferreira

---

## 8. Como executar

*Preencha com os comandos reais do projeto para que outra pessoa consiga reproduzir o ambiente.*

### Pré-requisitos

- [Ex.: Git]
- [Ex.: Python 3.12+]
- [Ex.: Node.js 20+]
- [Ex.: Docker]

### Instalação e execução

```bash
# 1. Clonar o repositório
git clone [URL_DO_REPOSITORIO]
cd [NOME_DA_PASTA]

# 2. Instalar dependências
[comando de instalação]

# 3. Configurar variáveis de ambiente
cp .env.example .env
# edite o arquivo .env com as credenciais locais

# 4. Executar a aplicação
[comando de execução]
```

**Acesso local:** [Ex.: http://localhost:3000]

### Implantação (quando houver)

- **Ambiente:** [Ex.: Render, Railway, Vercel, servidor da instituição]
- **URL de produção:** [https://...]
- **Observações:** [Ex.: é necessário configurar as variáveis de ambiente no painel do provedor]

---

## 9. Configuração

*Liste as variáveis de ambiente usadas pelo sistema. Nunca publique senhas, tokens ou chaves neste arquivo.*

| Variável | Obrigatória | Descrição | Exemplo |
| --- | --- | --- | --- |
| `PORT` | Sim | Porta da aplicação | `3000` |
| `DATABASE_URL` | Sim | Conexão com o banco | `postgresql://user:senha@localhost:5432/app` |
| `SECRET_KEY` | Sim | Chave de sessão / JWT | `[gerar localmente]` |

Credenciais reais devem ficar apenas no arquivo `.env` (não versionado).

---

## 10. Testes

*Descreva como executar os testes e o que eles cobrem.*

```bash
[comando para executar os testes]
```

| Tipo | Ferramenta | O que verifica |
| --- | --- | --- |
| Unitários | [Ex.: pytest / JUnit / Jest] | [Ex.: regras de negócio isoladas] |
| Integração | [Ex.: ...] | [Ex.: API e banco de dados] |
| Manuais | [Ex.: checklist em `docs/`] | [Ex.: fluxos principais da interface] |

**Cobertura atual:** [Ex.: 70% / não medida]

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

### Documentação complementar

- Índice da pasta `docs/`: [`docs/README.pdf`](docs/README.pdf)
- Casos de uso (diagrama + especificações): [`docs/modelagem/casos-de-uso/especificacoes-casos-de-uso.pdf`](docs/modelagem/casos-de-uso/especificacoes-casos-de-uso.pdf)
- Diagrama de classes: [`docs/modelagem/classes/diagrama-de-classes.pdf`](docs/modelagem/classes/diagrama-de-classes.pdf)
- Modelo conceitual (ER): [`docs/modelagem/banco-de-dados/diagrama-er.pdf`](docs/modelagem/banco-de-dados/diagrama-er.pdf)
- Modelo lógico: [`docs/modelagem/banco-de-dados/modelo-logico.pdf`](docs/modelagem/banco-de-dados/modelo-logico.pdf)
- Apresentação: [`docs/apresentacao.pdf`](docs/)

### Referências

- [Autor. Título. Ano. URL ou dados bibliográficos.]
- [Documentação oficial da tecnologia X.]

### Contato

Dúvidas sobre o projeto: [e-mail institucional do grupo ou issue no repositório]

**Agradecimentos:** [Ex.: professor(a), monitoria, materiais da disciplina]
