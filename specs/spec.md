# Definição de demanda: Tetris Game (React/TS + Node.js)

## 1. Objetivo

Implementar um jogo 2D funcional utilizando React com vite e TypeScript no frontend, com uma estrutura preparada para integração com Node.js.

## 2. Arquitetura e Padrões

O desenvolvimento deve seguir rigorosamente:
    - Clean Architecture: Independência de frameworks; a lógica de negócio não deve conhecer o React.
    - Domain-Driven Design (DDD): Foco no domínio, utilizando Entidades, Value Objects e Casos de Uso.
    - TDD (Test-Driven Development): Testes unitários devem validar a lógica de colisão e pontuação antes da UI.

## 3. Estrutura de Pastas (Diretrizes de Implementação)

Toda a implementação deve respeitar a seguinte árvore de diretórios:

/
├── src/
│   ├── domain/                # Camada de Domínio (Pureza total)
│   │   ├── entities/          # Peças, Tabuleiro, Motor de Jogo
│   │   └── value-objects/     # Pontuação, Coordenadas (Point)
│   ├── application/           # Camada de Aplicação (Use Cases)
│   │   └── usecases/          # Movimentar, Rotacionar, Limpar Linhas
│   ├── infra/                 # Camada de Infraestrutura (React/UI)
│   │   ├── components/        # Componentes visuais do React
│   │   └── hooks/             # Hooks para ligar a UI ao Domínio
│   └── shared/                # Constantes, Utils e Tipos Globais
└── tests/                     # Testes (Espelha a estrutura de src/)
    ├── domain/                # Testes de Entidades
    └── application/           # Testes de Casos de Uso

Regras de Importação:
    - Sempre utilize o alias @/ para se referir à pasta src/, garantindo que os imports funcionem em qualquer nível de profundidade.
    - Não faça imports com @/src, @/ iquivale a @/src.
    - Os imports devem ser precisos conforme a profundidade do arquivo na árvore acima.

## 4. Configurações

    - Implemente a lógica de UI dentro da pasta infra.
    - Crio o arquivo index.tsx como ponto de partida do componentes .tsx.
    - Se usar arquivos .css configure o typescript para reconhecer esse tipo de extensão criando um arquivo de tipos.
    - Crie o arquivo package.json com as configurações de execução e gerenciamento de dependencias:
        - Adicione a dependencia ts-node no package.json.
        - Adicione a dependencia jest-environment-jsdom no package.json.
    - Crie o arquivo de configurações do TypeScript:
        - Configure no arquivo tsconfig o alias @/ para se refererir a pasta src.
        - Adicione a opção ignoreDeprecations": "6.0" no arquivo de configurações do typescript.
    - Crie apenas o arquivo de configurações jest.config.ts para execução dos testes unitários pelo jest.

## 5. Regras de Negócio

    - Mecânica de Queda: Um bloco de cada vez desce do topo e para ao colidir com o fundo ou com celulás já preenchidas.
    - Os blocos têm formatos (Tetrominos): Inicialmente 4 tipos: O (quadrado), L, I e Z. Cada bloco possui exatamente 4 células.
    - Uma célula é um retangulo perfeito.
    - Rotação: O bloco rotaciona em torno de seu eixo central, validando colisão com bordas e blocos fixos antes de confirmar o movimento.
    - Tabuleiro: Dimensões fixas de 8 células de largura por 24 de altura.
    - Controle de Velocidade: 
        - Velocidade inicial: 1 célula/segundo.
        - Aceleração manual: até 10x a velocidade atual.
        - Progressão: A cada 100 pontos, a velocidade base aumenta em 10%.

    - Pontuação e Eliminação:
        - Linhas completas devem ser removidas.
        - Se múltiplas linhas completarem simultaneamente, todas são eliminadas.
        - Células preenchidas acima de linhas removidas caem até colidir com o fundo ou outras células preenchidas.
        - Cada linha eliminada concede 100 pontos.
    - Game Over: Ocorre quando um novo bloco, ao spawnar ou colidir no topo, não cabe mais nos limites da tela.
