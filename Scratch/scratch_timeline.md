# Timeline

Minha ordem para fazer o projeto será a seguinte:

1. Definir os requisitos pedidos pelo enunciado
2. Escrever os testes unitarios (em formato de palavra inicialmente) que satisfazem esses requisitos
3. Escolher e modelar as interfaces, metodos, entidades, etc
4. Pensar na estrutura de dados que vou usar para resolver os problemas
5. Começar o ciclo TDD de: Escreve um teste -> escreve o codigo que faz esse teste passar -> refatora -> repetir...
6. Documentar somente o necessario do que foi feito
7. Pensar em como seria possivel expandir o projeto =)

OBS: Sempre adicionar um teste quando der algum bug, cobrindo este bug

## 1 - Requisitos

* Quando receber uma ordem do tipo Pegged, Limit ou Market, deve ser capaz de processá-la segundo as regras de mercado correspondentes.
* Deve ser capaz de realizar operações de cancelamento e modificação de ordens ativas.
* Deve seguir uma regra de execução baseada primeiramente no preço e, em seguida, na ordem de chegada 
* Quando uma ordem sofrer alteração de preço, deve ser capaz de colocá-la na faixa adequada, rebaixando sua prioridade de chegada na fila.
* Deve ser capaz de tratar e processar corretamente o matching de casos complexos e sequências de pedidos.
* Quando um trade for realizado, deve ser capaz de emitir e exibir os detalhes da execução imediatamente na saída do sistema.
* Deve ser capaz de exibir o estado atual do Limit Order Book para visualização.
* Deve ser capaz de suportar erros de entrada typo ou ignorar comandos não existentes.
* Deve realizar trade de ordens limits sempre que cruzarem o spread.
* Os algoritmos devem ser, quando possível, no máximo O(N)

## 2 - Ideia inicial de interfaces e entidades

## 3 - Escolher e modelar a arquitetura de classes, etc.

Order
* Responsabilidade: Manter o estado basico de uma ordem qualquer
* Atributos
  * id (string)
  * side (Side)
  * quantity (inteiro)
  * timestamp (Date/time)
* Metodo
  * reduce_quantity()

Limit Order (herda Order)
* Responsabilidade: Modelar ordem limite com suas caracteristicas proprias
* Atributos
  * price (float)
* Metodo
  * change_price()

Pegged Order (herda order)
* Responsabilidade: Modelar uma pegged order
* Atributos
  * current_price
* Metodo
  * Update_price
  
Order Book
* Responsabilidade: armazenar as ordens
* Atributos
  * Bids
  * Asks
* Metodos
  * add_order
  * remove_order
  * get_best_bid
  * get_best_ask
  * get_order_by_id
  * get_all_orders

Matching Engine
* Responsabilidade: regras de negocio com base no input
* Atributos
  * Book
* Metodos
  * process_limit_order
  * process_market_order
  * process_pegged_order
  * cancel_order
  * modify_order
  * update_pegged_orders
  
Parser
* Responsabilidade: Le o input bruto, processa a informacao, e manda para o Matching engine, caso nao seja erro

## 4 - Estrutura de dados

Me foi pedido para realizar tudo em ordem(N), quando possível

Eu tenho no geral, algumas tarefas.

Insert bid/ask
cancel order
modify order
get order by id
...

Para essas tarefas, pensei em duas formas de estruturar meus dados

Forma 1) Bid e Ask sao filas de prioridade heap, insere em O(Log(N)), extrai em O(log(N)),
busca em O(N)


Forma 2) Mais complicado, temos varias estruturas de dados para cada coisa que pretendemos fazer
    1 Hash Map para as ordens (chave ID, valor um ponteiro, ou referencia para o objeto na memoria) (encontro a ordem em O(1) pelo ID para cancel e modify)
    1 Lista duplamente encadeada para cada Nivel de Preço  (pois ao cancelar ou modify, ao achar a ordem pelo hash map, podemos apenas eliminar ela dessa lista, em O(1))
    1 Arvore Binaria de Busca para os precos (chave = preco, valor = ponteiro para  a cabeca da lista duplamente encadeada)