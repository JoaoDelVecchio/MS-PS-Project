# Rascunho Inicial de testes unitários

Não estão necessariamente na ordem que foram implementados

1. Testa uma sequencia complexa de ordem do enunciado

A seguinte sequencia de match deve ser aceita:
   
>>> limit buy 10 100

>>> limit sell 20 100

>>> limit sell 20 200

>>> market buy 150

Trade, price: 20, qty: 150

>>> market buy 200

Trade, price: 20, qty: 150

>>> market sell 200

Trade, price: 10, qty: 100

2. Testa se é capaz de adicionar um limit buy order ao book

Quando adicionar um limit buy 10 100; entao ao printar o book devemos ter:
Ordens de Compra
100 @ 10
Ordens de Venda

3. Testa se é capaz de adicionar um limit sell order ao book

 Quando adicionar um limit sell 20 100, entao printar o book deve gerar: 
 Ordens de Compra
 Ordens de Venda
 100 @ 20

4. Testa se é capaz de adicionar um limit buy e um limit sell que nao dao match diretamente

Quando receber como input
limit buy 10 100
limit sell 20 100

Entao ao printar o book deve gerar:
Ordens de Compra
100 @ 10
Ordens de Venda
100 @ 20

5. Testa se é capaz de adicionar um limit buy e um limit sell que dao match diretamente, e nao sobra volume de nenhum

>>> limit buy 10 100

>>> limit sell 10 100

Trade, price: 10, qty: 100

1. Testa se, ao dar match em duas ordens limites que possuem o mesmo volume, entao o book printado devera retornar vazio

Quando o input for

>>> limit buy 10 100

>>> limit sell 10 100

entao ao printar o book devemos ter
Ordens de Compra
Ordens de Venda

7. Testa se consegue realizar uma ordem a mercado de compra quando existe uma limit de venda com liquidez maior que a ordem de compra

>>> limit sell 20 100
>>> market buy 40
Trade, price: 20, qty: 40

Ao printar o book:
Ordens de Compra
Ordens de Venda
60 @ 20

8. Testa se consegue realizar uma ordem a mercado de compra quando existe uma limite de venda com liquidez menor que a ordem de compra, mas existe outra ordem de venda posterior com liquidez suficiente

>>> limit sell 20 30
>>> limit sell 25 100
>>> market buy 50
Trade, price: 20, qty: 30
Trade, price: 25, qty: 20

Ao printar o book:
Ordens de Compra
Ordens de Venda
80 @ 25

9.  Testa se consegue realizar uma ordem a mercado de compra quando existe uma limite de venda com liquidez menor que a ordem de compra, existindo outra ordem de venda posterior sem liquidez suficiente, mas com uma terceira com liquidez suficiente

>>> limit sell 20 20
>>> limit sell 25 20
>>> limit sell 30 100
>>> market buy 60
Trade, price: 20, qty: 20
Trade, price: 25, qty: 20
Trade, price: 30, qty: 20

Ao printar o book:
Ordens de Compra
Ordens de Venda
80 @ 30

10. Testa se consegue realizar uma ordem a mercado de compra quando existe uma limite de venda com liquidez menor que a ordem de compra, existindo outra ordem de venda posterior sem liquidez suficiente, sem uma terceira

>>> limit sell 20 20
>>> limit sell 25 20
>>> market buy 60
Trade, price: 20, qty: 20
Trade, price: 25, qty: 20

Ao printar o book:
Ordens de Compra
Ordens de Venda

11. Testa se consegue realizar uma ordem a mercado de compra quando existe uma limit de venda com liquidez menor, e nao ha outra ordem

>>> limit sell 20 50
>>> market buy 100
Trade, price: 20, qty: 50

Ao printar o book:
Ordens de Compra
Ordens de Venda
    
12. Testa se consegue realizar uma ordem a mercado de venda quando existe uma limit de compra com liquidez maior que a ordem de compra

>>> limit buy 10 100
>>> market sell 40
Trade, price: 10, qty: 40

Ao printar o book:
Ordens de Compra
60 @ 10
Ordens de Venda

13. Testa se consegue realizar uma ordem a mercado de venda quando existe uma limite de compra com liquidez menor que a ordem de compra, mas existe outra ordem de compra posterior com liquidez suficiente

>>> limit buy 15 30
>>> limit buy 10 100
>>> market sell 50
Trade, price: 15, qty: 30
Trade, price: 10, qty: 20

Ao printar o book:
Ordens de Compra
80 @ 10
Ordens de Venda

14. Testa se consegue realizar uma ordem a mercado de venda quando existe uma limite de compra com liquidez menor que a ordem de compra, existindo outra ordem de compra posterior sem liquidez suficiente, mas com uma terceira com liquidez suficiente

>>> limit buy 20 20
>>> limit buy 15 20
>>> limit buy 10 100
>>> market sell 60
Trade, price: 20, qty: 20
Trade, price: 15, qty: 20
Trade, price: 10, qty: 20

Ao printar o book:
Ordens de Compra
80 @ 10
Ordens de Venda

15. Testa se consegue realizar uma ordem a mercado de venda quando existe uma limite de compra com liquidez menor que a ordem de compra, existindo outra ordem de compra posterior sem liquidez suficiente, sem uma terceira

>>> limit buy 20 20
>>> limit buy 15 20
>>> market sell 60
Trade, price: 20, qty: 20
Trade, price: 15, qty: 20

Ao printar o book:
Ordens de Compra
Ordens de Venda


16. Testa se é capaz de adicionar 2 posicoes de Limit Buy, mas com precos diferentes, em que eh respeitada a prioridade de preco na hora de printar o book

>>> limit buy 10 100
>>> limit buy 15 100

Ao printar o book:
Ordens de Compra
100 @ 15
100 @ 10
Ordens de Venda

17. Testa se é capaz de adicionar 2 posicoes de Limit sell, mas com precos diferentes, em que eh respeitada a prioridade de preco na hora de printar o book

>>> limit sell 25 100
>>> limit sell 20 100

Ao printar o book:
Ordens de Compra
Ordens de Venda
100 @ 20
100 @ 25

18. Testa se é capaz de adicionar 2 posicoes de Limit Buy, mas com precos diferentes, em que eh respeitada a prioridade de tempo na hora de printar o book

>>> limit buy 10 100 (identificador_A)
>>> limit buy 10 50 (identificador_B)

Ao printar o book:
Ordens de Compra
100 @ 10
50  @ 10
Ordens de Venda

19. Testa se é capaz de adicionar 2 posicoes de Limit sell, com precos iguais, em que eh respeitada a prioridade de tempo na hora de printar o book

>>> limit sell 20 100
>>> limit sell 20 50

>> print book
Ordens de Compra
Ordens de Venda
100 @ 20
50 @ 20


20. Testa se, ao adicioanar 3 limit orders de buy, o market order que sera lancado, com liquidez menor, respeitara prioridade de preco

>>> limit buy 10 100
>>> limit buy 15 100
>>> limit buy 5 100
>>> market sell 50
Trade, price: 15, qty: 50

21. Testa se, ao adicioanr 3 limit orders de sell, o market order que sera lancado, com liquidez menor, respeitara a prioridade de preco

>>> limit sell 25 100
>>> limit sell 20 100
>>> limit sell 30 100
>>> market buy 50
Trade, price: 20, qty: 50


22. Testa se, ao adicioanar 3 limit orders de buy, o market order que sera lancado, com liquidez menor, respeitara prioridade de tempo

>>> limit buy 10 50
>>> limit buy 10 50
>>> limit buy 10 50
>>> market sell 80
Trade, price: 10, qty: 50
Trade, price: 10, qty: 30

23. Testa se, ao adicioanr 3 limit orders de sell, o market order que sera lancado, com liquidez menor, respeitara a prioridade de tempo

>>> limit sell 20 50
>>> limit sell 20 50
>>> limit sell 20 50
>>> market buy 80
Trade, price: 20, qty: 50
Trade, price: 20, qty: 30

24. Testa se, ao ter apenas um limit order de buy, e colocar um market order que nao consome toda liquidez, entao ao printar o book a quantidade estara alterada

>>> limit buy 10 100
>>> market sell 30
Trade, price: 10, qty: 30

>> print book
Ordens de Compra
70 @ 10
Ordens de Venda

25. Testa se, ao ter apenas um limit order de sell, e colocar um market order que nao consome toda liquidez, entao ao printar o book a quantidade estara alterada

>>> limit sell 20 100
>>> market buy 30
Trade, price: 20, qty: 30

>> print book
Ordens de Compra
Ordens de Venda
70 @ 20

26. Testa se é possível cancelar uma ordem corretamente

>>> limit buy 10 100

Order created: buy 100 @ 10 identificador_1

>>> cancel order identificador_1

Order cancelled

27. Testa o funcionamento de uma pegg order dado o enunciado:
Quando o book for:

>> print book

Ordens de Compra:
200 @ 10
100 @ 9.99
Ordens de Venda:
100 @ 10.5

>> peg bid buy 150

O book sera assim:
Ordens de Compra
200 @ 10
150 @ 10
100 @ 9.99
Ordens de Venda
100 @ 10.5

>> limit bid buy 10.1 300

Entao o book sera assim:
Ordens de Compra:
150 @ 10.1
300 @ 10.1
200 @ 10
100 @ 9.99

Ordens de venda:
100 @ 10.5

28. Testa o mesmo comportamento anterior mas para peg to offer

29. Testa se eh capaz de alterar uma posição, perdendo prioridade caso necessario:


Ordens de Compra
200 @ 10
100 @ 9.99
Ordens de Venda
100 @ 10.5


Ao alterar a primeira ordem de compra (200 quantidades ao preço R$ 10,00) para um preço de 9.98, devemos ter a seguinte configuração do livro:

Ordens de Compra
100 @ 9.99
200 @ 9.98

Ordens de Venda
100 @ 10.5

Ou seja, perdeu prioridade na fila.

30. Testa a submissão de uma Limit Buy que atravessa o spread (Marketable Limit Order)

>>> limit sell 20 100
>>> limit buy 25 50
Trade, price: 20, qty: 50

>> print book
Ordens de Compra
Ordens de Venda
50 @ 20

31. Testa a submissão de uma Limit Sell que atravessa o spread
    
>>> limit buy 10 100
>>> limit sell 5 50
Trade, price: 10, qty: 50

>> print book
Ordens de Compra
50 @ 10
Ordens de Venda


32. Testa o comportamento perante entradas inválidas (Typos e valores incorretos)

>>> lmit buy 10 100
Error
>>> limit buy -10 100
Error
>>> market sell 0
Error

33. Testa a alteração de quantidade PARA BAIXO mantendo a prioridade de tempo

>>> limit buy 10 100
Order created: buy 100 @ 10 id_1
>>> limit buy 10 50
Order created: buy 50 @ 10 id_2
>>> modify id_1 qty 50
Order modified
>>> market sell 60
Trade, price: 10, qty: 50
Trade, price: 10, qty: 10

34. Testa alteração de preço que gera trade imediato    

>>> limit buy 10 100
Order created: buy 100 @ 10 id_1
>>> limit sell 20 100
Order created: sell 100 @ 20 id_2
>>> modify id_1 price 20
Trade, price: 20, qty: 100

35. Testa o funcionamento de uma peg to offer, acompanhando o melhor preço de venda

>>> limit sell 20 100
>>> peg offer sell 50

>> print book
Ordens de Compra
Ordens de Venda
100 @ 20
50 @ 20

36. Testa a atualização da peg to offer quando uma ordem de venda com preço melhor (menor) é inserida

>>> limit sell 20 100
>>> peg offer sell 50
>>> limit sell 15 100

>> print book
Ordens de Compra
Ordens de Venda
50 @ 15
100 @ 15
100 @ 20

37. Testa a atualização da peg to offer quando o melhor preço de venda é totalmente consumido

>>> limit sell 15 100
>>> limit sell 20 100
>>> peg offer sell 50
>>> market buy 100
Trade, price: 15, qty: 100

>> print book
Ordens de Compra
Ordens de Venda
100 @ 20
50 @ 20

38. Testa a execução de uma peg to offer quando uma ordem de compra a mercado consome a liquidez

>>> limit sell 20 100
>>> peg offer sell 50
>>> market buy 150
Trade, price: 20, qty: 100
Trade, price: 20, qty: 50

>> print book
Ordens de Compra
Ordens de Venda

39. Testa o cancelamento de uma ordem limit de compra e a visualização do book

>>> limit buy 10 100
Order created: buy 100 @ 10 id_1
>>> limit buy 15 100
Order created: buy 100 @ 15 id_2
>>> cancel order id_1
Order cancelled

>> print book
Ordens de Compra
100 @ 15
Ordens de Venda

40. Testa o cancelamento de uma ordem limit de venda e a visualização do book

>>> limit sell 20 100
Order created: sell 100 @ 20 id_1
>>> limit sell 25 100
Order created: sell 100 @ 25 id_2
>>> cancel order id_2
Order cancelled

>> print book
Ordens de Compra
Ordens de Venda
100 @ 20

41. Testa o cancelamento de uma ordem pegged (bid)
    
>>> limit buy 10 100
Order created: buy 100 @ 10 id_1
>>> peg bid buy 50
Order created: peg bid 50 id_2
>>> cancel order id_2
Order cancelled

>> print book
Ordens de Compra
100 @ 10
Ordens de Venda

42. Testa o cancelamento de uma ordem que já foi parcialmente executada

>>> limit buy 10 100
Order created: buy 100 @ 10 id_1
>>> market sell 40
Trade, price: 10, qty: 40
>>> cancel order id_1
Order cancelled

>> print book
Ordens de Compra
Ordens de Venda

43. Testa o comportamento ao tentar cancelar uma ordem inexistente ou já totalmente executada

>>> limit buy 10 100
Order created: buy 100 @ 10 id_1
>>> market sell 100
Trade, price: 10, qty: 100
>>> cancel order id_1
Error

44. Testa a alteração de preço de uma limit buy para baixo (piora o preço) e a reordenação no book

>>> limit buy 15 100
Order created: buy 100 @ 15 id_1
>>> limit buy 10 100
Order created: buy 100 @ 10 id_2
>>> modify id_1 price 5
Order modified

>> print book
Ordens de Compra
100 @ 10
100 @ 5
Ordens de Venda

45. Testa a alteração de preço de uma limit buy para igualar a outra, verificando a perda de prioridade temporal
    
>>> limit buy 10 100
Order created: buy 100 @ 10 id_1
>>> limit buy 15 100
Order created: buy 100 @ 15 id_2
>>> modify id_1 price 15
Order modified
>>> market sell 100
Trade, price: 15, qty: 100

>> print book
Ordens de Compra
100 @ 15
Ordens de Venda

46. Testa a alteração de quantidade de uma limit sell para CIMA, verificando a perda de prioridade temporal

>>> limit sell 20 100
Order created: sell 100 @ 20 id_1
>>> limit sell 20 100
Order created: sell 100 @ 20 id_2
>>> modify id_1 qty 150
Order modified
>>> market buy 100
Trade, price: 20, qty: 100

>> print book
Ordens de Compra
Ordens de Venda
150 @ 20

47. Testa a alteração de quantidade de uma limit sell para BAIXO, verificando a manutenção da prioridade temporal

>>> limit sell 20 100
Order created: sell 100 @ 20 id_1
>>> limit sell 20 100
Order created: sell 100 @ 20 id_2
>>> modify id_1 qty 50
Order modified
>>> market buy 50
Trade, price: 20, qty: 50

>> print book
Ordens de Compra
Ordens de Venda
100 @ 20

48. Testa a alteração de preço de uma limit buy atravessando o spread, gerando execução imediata

>>> limit buy 10 100
Order created: buy 100 @ 10 id_1
>>> limit sell 20 100
Order created: sell 100 @ 20 id_2
>>> modify id_1 price 20
Trade, price: 20, qty: 100

49. Testa uma limit buy agressiva que atravessa o spread, executando parcialmente e indo para o book

>>> limit sell 20 100
>>> limit buy 25 150
Trade, price: 20, qty: 100

>> print book
Ordens de Compra
50 @ 25
Ordens de Venda

50. Testa uma limit sell agressiva que atravessa o spread, executando parcialmente e indo para o book

>>> limit buy 10 100
>>> limit sell 5 150
Trade, price: 10, qty: 100

>> print book
Ordens de Compra
Ordens de Venda
50 @ 5

51. Testa uma limit buy agressiva que atravessa o spread e consome múltiplos níveis de preço

>>> limit buy 10 100
>>> limit sell 5 150
Trade, price: 10, qty: 100

>> print book
Ordens de Compra
Ordens de Venda
50 @ 5

52. Testa uma limit sell agressiva que atravessa o spread e consome múltiplos níveis de preço, parando no limite

>>> limit buy 15 50
>>> limit buy 10 50
>>> limit sell 12 80
Trade, price: 15, qty: 50

>> print book
Ordens de Compra
50 @ 10
Ordens de Venda
30 @ 12

53. Testa o comportamento da peg offer acompanhando o melhor ask quando este é modificado (melhora de preço)

>>> limit sell 20 100
Order created: sell 100 @ 20 id_1
>>> peg offer sell 50
Order created: peg offer 50 id_2
>>> modify id_1 price 18
Order modified

>> print book
Ordens de Compra
Ordens de Venda
50 @ 18
100 @ 18

54. Testa uma limit buy igualando exatamente o melhor ask para uma execução parcial simples

>>> limit sell 20 100
>>> limit buy 20 40
Trade, price: 20, qty: 40

>> print book
Ordens de Compra
Ordens de Venda
60 @ 20

55. Testa a alteração de quantidade de uma peg bid, verificando se ela perde a prioridade entre outras ordens peg

>>> limit buy 10 100
Order created: buy 100 @ 10 id_1
>>> peg bid buy 50
Order created: peg bid 50 id_2
>>> peg bid buy 50
Order created: peg bid 50 id_3
>>> modify id_2 qty 100
Order modified
>>> market sell 150
Trade, price: 10, qty: 100
Trade, price: 10, qty: 50

56. Testa a atualização da peg bid quando a ordem limit de compra de referência (melhor bid) é CANCELADA

>>> limit buy 10 100
Order created: buy 100 @ 10 id_1
>>> limit buy 9 100
Order created: buy 100 @ 9 id_2
>>> peg bid buy 50
Order created: peg bid 50 id_3
>>> cancel order id_1
Order cancelled

>> print book
Ordens de Compra
100 @ 9
50 @ 9
Ordens de Venda

57. Testa a atualização da peg offer quando a ordem limit de venda de referência (melhor offer) é CANCELADA

>>> limit sell 20 100
Order created: sell 100 @ 20 id_1
>>> limit sell 21 100
Order created: sell 100 @ 21 id_2
>>> peg offer sell 50
Order created: peg offer 50 id_3
>>> cancel order id_1
Order cancelled

>> print book
Ordens de Compra
Ordens de Venda
100 @ 21
50 @ 21

58. Testa a atualização da peg bid quando a ordem limit de compra de referência é ALTERADA PARA PIOR (menor preço)

>>> limit buy 10 100
Order created: buy 100 @ 10 id_1
>>> limit buy 9 100
Order created: buy 100 @ 9 id_2
>>> peg bid buy 50
Order created: peg bid 50 id_3
>>> modify id_1 price 8
Order modified

>> print book
Ordens de Compra
100 @ 9
50 @ 9
100 @ 8
Ordens de Venda

59. Testa a atualização da peg offer quando a ordem limit de venda de referência é ALTERADA PARA PIOR (maior preço)

>>> limit sell 20 100
Order created: sell 100 @ 20 id_1
>>> limit sell 21 100
Order created: sell 100 @ 21 id_2
>>> peg offer sell 50
Order created: peg offer 50 id_3
>>> modify id_1 price 22
Order modified

>> print book
Ordens de Compra
Ordens de Venda
100 @ 21
50 @ 21
100 @ 22

60. Testa a atualização da peg bid quando a ordem limit de compra de referência é ALTERADA PARA MELHOR (maior preço)

>>> limit buy 10 100
Order created: buy 100 @ 10 id_1
>>> limit buy 9 100
Order created: buy 100 @ 9 id_2
>>> peg bid buy 50
Order created: peg bid 50 id_3
>>> modify id_1 price 11
Order modified

>> print book
Ordens de Compra
50 @ 11
100 @ 11
100 @ 9
Ordens de Venda

61. Testa o comportamento da pegged order quando a ÚNICA ordem de referência no book é cancelada
(Nota arquitetural: Como o enunciado não especifica o que ocorre se o livro esvaziar de um lado, o comportamento padrão de mercado é que a ordem pegged mantenha o último preço de referência válido até que uma nova limit surja, ou seja suspensa. Este teste assume que ela mantém o último preço).

>>> limit buy 10 100
Order created: buy 100 @ 10 id_1
>>> peg bid buy 50
Order created: peg bid 50 id_2
>>> cancel order id_1
Order cancelled

>> print book
Ordens de Compra
50 @ 10
Ordens de Venda

62. Testa a tentativa de alterar o PREÇO de uma ordem Pegged (deve gerar erro, pois o preço é dinâmico)
    
>>> limit buy 10 100
Order created: buy 100 @ 10 id_1
>>> peg bid buy 50
Order created: peg bid 50 id_2
>>> modify id_2 price 15
Error

63. Testa a alteração de quantidade de uma ordem para ZERO
Deve rejeitar

64. Testa a execução de uma Market Order que consome simultaneamente uma Limit Order e uma Pegged Order no mesmo nível de preço

>>> limit buy 10 100
>>> peg bid buy 50
>>> market sell 150
Trade, price: 10, qty: 100
Trade, price: 10, qty: 50

>> print book
Ordens de Compra
Ordens de Venda

65. Testa uma Limit Order Agressiva que varre o book (Sweep), consumindo múltiplos níveis e incluindo ordens Pegged no caminho

>>> limit sell 20 100
>>> limit sell 21 100
>>> peg offer sell 50
>>> limit buy 25 200
Trade, price: 20, qty: 100
Trade, price: 20, qty: 50
Trade, price: 21, qty: 50

>> print book
Ordens de Compra
Ordens de Venda
50 @ 21