# Definição de demanda: Tetris Game (React/TS + Node.js)

## 1. Objetivo

Implementar um jogo 2D funcional utilizando React e TypeScript no frontend, com uma estrutura preparada para integração com Node.js.

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

Regras de Importação: - Os arquivos dentro de tests/domain/ devem utilizar caminhos relativos para acessar src/. Ex: import { Board } from '../../src/domain/entities/Board'.

    - Os imports devem ser precisos conforme a profundidade do arquivo na árvore acima.

## 4. Regras de Negócio

    - Mecânica de Queda: Blocos descem do topo e param ao colidir com o fundo ou outros blocos.
    - Formatos (Tetrominos): Inicialmente 4 tipos: O (quadrado), L, I e Z. Cada bloco possui exatamente 4 células.
    - Rotação: O bloco rotaciona em torno de seu eixo central, validando colisão com bordas e blocos fixos antes de confirmar o movimento.
    - Tabuleiro: Dimensões fixas de 8 células de largura por 24 de altura.
    - Controle de Velocidade: - Velocidade inicial: 1 célula/segundo.
        - Aceleração manual: até 10x a velocidade atual.
        - Progressão: A cada 100 pontos, a velocidade base aumenta em 10%.

    - Pontuação e Eliminação:
        - Linhas completas devem ser removidas.
        - Se múltiplas linhas completarem simultaneamente, todas são eliminadas.
        - Cada linha eliminada concede 100 pontos.
    - Game Over: Ocorre quando um novo bloco, ao spawnar ou colidir no topo, não cabe mais nos limites da tela.

## Regras de negócio

    - O jogo consite em um bloco que desce do topo da tela e para ao colidir com o fundo da tela ou com outro bloco.
    - O bloco inicialmente tem 4 formatos: O (quadrado), L e I e Z.
    - Cada bloco é composto por 4 celulas em formato de retangulo perfeito.
    - O bloco pode ser rotacionado em torno do proprio eixo central.
    - A rotação só pode ser feita se o bloco na nova posição rotacionada não colidir com as estremidades da tela ou com celulas já preenchidas no fundo.
    - A tela tem dimensões de 8 celulas de largura por 24 de altura.
    - O bloco pode ser acelerado para chegar ao fundo mais rápido.
    - A aceleração vai até 10 vezes a velocidade de movimento atual do bloco.
    - O bloco tem velocidade de movimento inicial de uma celula por segundo.
    - Quando todas as celulas de uma linha estiverem preenchidas com partes dos blocos, essa linha é eliminada e as celulas a cima descem para se juntar às celulas abaixo ou ao fundo da tela.
    - Se mais de uma linha estiver completa ao mesmo tempo, todas devem ser eliminadas.
    - A cada linha eliminada o jogador soma 100 pontos.
    - A cada 100 pontos acumulados pelo jogar a velocidade do bloco que está descendo aumenta em 10%.
    - O jogo acaba quando um bloco, após colidir, não couber na tela.
