# Definição de demanda

## Objetivo

Implementar um jogo em 2D em React/TypeScript.

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
