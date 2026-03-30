# Enunciado

Uma ordem, no mercado financeiro, significa uma manifestação de interesse de compra ou venda de um determinado ativo. Para fins de simplicidade, iremos trabalhar com dois tipos de ordem: uma ordem à mercado (ou Market Order) e ordem limite (ou Limit Order).

Uma Matching Engine (ou Order Matching System) é um sistema desenvolvido para cruzar ordens em uma exchange de forma rápida e justa. O seu objetivo é estruturar uma matching engine simples, de acordo com algumas premissas:

 

1- A engine trabalhará com apenas 1 ativo

2- As ordens possíveis são limit (uma ordem passiva colocada a um preço fixo)  e market (uma ordem que deve ser preenchida no melhor preço disponível imediatamente)

3- Não é necessário ter armazenamento perene das ordens e trades, todas as informações podem ser mantidas em memória volátil

4- Não é necessário pensar em escalabilidade de hardware e ferramentas de nuvem e elasticidade (como Kubernetes)

 

O objetivo é desenhar um projeto de software utilizando formas eficientes de estruturação de dados, algoritmos e engenharia de software. Os algoritmos devem ter, se possível, ordem N. O software pode ser escrito em forma estrutural ou orientada à objetos.

Deve ser possível inserir ordens com as informações:

                - Tipo (limit/market)

                - Side (buy/sell)

                - Price (quando order for limit)

                - Qty

Limit orders com preços que gerariam trades podem ser ignoradas ou preenchidas, porém o comportamento escolhido deve ser justificado.

Quando um trade for realizado, deve-se mostrar na saída:

"Trade, price: <preço do trade>, qty: <número de shares>"

Exemplos de entrada e saída:

 

>>> limit buy 10 100

>>> limit sell 20 100

>>> limit sell 20 200

>>> market buy 150

Trade, price: 20, qty: 150

>>> market buy 200

Trade, price: 20, qty: 150

>>> market sell 200

Trade, price: 10, qty: 100

 

Demais items a serem implementados:

1. Implementar uma função/método para visualização do livro;

2. Soluções que respeitem a ordem de chegada das ordens. No exemplo anterior, isso significa que a primeira ordem de venda com quantidade 100 deve ser preenchida antes da segunda, com quantidade 200;

3. Implementação de cancelamento. Uma ordem ao ser cancelada, deve ser retirada do match engine.  Exemplo:

                >>> limit buy 10 100

                Order created: buy 100 @ 10 identificador_1

                >>> cancel order identificador_1

                Order cancelled

Bônus:

1. Cobertura com testes unitários.

2. Implementação de alteração de ordem. Uma ordem alterada tem seu preço, quantidade ou ambos modificados. Caso tenha implementado o primeiro item de bönus, lembre-se que a ordem com alteração de preço deve ser recolocada para a faixa de preço adequado. Em um livro hipotético:

               

Ordens de Compra

Ordens de Venda

200 @ 10

100 @ 10.5

100 @ 9.99

 

 

Ao alterar a primeira ordem de compra (200 quantidades ao preço R$ 10,00) para um preço de 9.98, devemos ter a seguinte configuração do livro:

 

Ordens de Compra

Ordens de Venda

100 @ 9.99

100 @ 10.5

200 @ 9.98

 

 

Ou seja, perdeu prioridade na fila.

3. Uma ordem pegged é um tipo de ordem que segue um determinado preço de referência. Bid é o melhor preço de compra disponível no livro de ofertas. Offer é o melhor preço de venda. Por exemplo, uma ordem peg to the bid irá acompanhar o preço do bid, ou seja, tem sempre o preço atualizado pelo match engine para acompanhar o melhor preço de compra conforme exemplo abaixo:

>> print book

Ordens de Compra

Ordens de Venda

200 @ 10

100 @ 10.5

100 @ 9.99

 

>> peg bid buy 150

Ordens de Compra

Ordens de Venda

200 @ 10

100 @ 10.5

150 @ 10

 

100 @ 9.99

 

>> limit bid buy 10.1 300

Ordens de Compra

Ordens de Venda

150 @ 10.1

100 @ 10.5

300 @ 10.1

200 @ 10

 

100 @ 9.99

 

O mesmo funciona para o peg to de offer.

##############################################

 Linguagens preferíveis: Java, Python ou C++