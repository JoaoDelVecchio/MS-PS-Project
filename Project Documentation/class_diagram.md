# Diagrama de Classes e Arquitetura do Sistema

Este documento descreve todas as entidades, estruturas de dados e controladores que compõem o *Matching Engine* e o *Limit Order Book (LOB)*, detalhando seus atributos e métodos.

**Legenda de Visibilidade (Convenção Python):**

* `+` : Público (Public)
* `-` : Privado (Private / Internal)

## 1. Domínio de Entidades (`Core/entities.py`)

As entidades representam os objetos de negócio fundamentais do sistema. Elas guardam estado, mas não possuem lógica complexa de mercado.

### `Order` (Classe Base)

A abstração principal que representa qualquer pedido de compra ou venda. Ela já possui os ponteiros embutidos (`prev` e `next`) para atuar como nó em uma Lista Duplamente Encadeada.
**Atributos:**

* `+ order_id: str` (Identificador único da ordem)
* `+ seq_id: int` (Prioridade temporal da ordem na fila)
* `+ side: str` ('buy' ou 'sell')
* `+ price: float` (Preço alvo da ordem)
* `+ qty: int` (Quantidade atual/restante)
* `+ prev: Order` (Ponteiro para a ordem anterior na fila)
* `+ next: Order` (Ponteiro para a próxima ordem na fila)

**Métodos:**

* `+ reduce_qty(amount: int)` (Deduz a quantidade executada do total da ordem)

### `LimitOrder` (Herda de `Order`)

Representa uma ordem passiva/agressiva com limite de preço fixo.
*(Não possui atributos/métodos adicionais, herda tudo de `Order`)*

### `PeggedOrder` (Herda de `Order`)

Representa uma ordem ancorada dinamicamente ao mercado.
**Atributos Adicionais:**

* `+ peg_type: str` ('bid' ou 'offer', definindo a qual lado do livro ela se atrela)


## 2. Domínio de Dados (`Core/limit_order_book.py`)

Responsável por armazenar o estado do mercado e organizar as ordens com a máxima eficiência temporal ($\mathcal{O}(1)$ para maioria das operações).

### `OrderDoubleLinkedList`

Fila encadeada que gerencia a prioridade temporal das ordens dentro de um mesmo nível de preço.
**Atributos:**

* `+ head: Order` (Primeira ordem da fila - maior prioridade)
* `+ tail: Order` (Última ordem da fila - menor prioridade)

**Métodos:**

* `+ insert_sorted(order: Order)` (Insere a ordem respeitando o `seq_id`. Usado para realocar Pegged Orders)
* `+ append(order: Order)` (Adiciona a ordem no final da fila em $\mathcal{O}(1)$)
* `+ remove(order: Order)` (Remove a ordem do meio da fila atualizando os ponteiros em $\mathcal{O}(1)$)

### `LimitOrderBook`

O coração dos dados. Mantém o mapeamento de IDs e organiza os níveis de preço.
**Atributos:**

* `+ orders_map: dict` (Mapeia `order_id` -> Objeto `Order` em $\mathcal{O}(1)$)
* `+ bids_dict: dict` / `+ asks_dict: dict` (Mapeia Preço -> `OrderDoubleLinkedList`)
* `+ bids_prices: list` / `+ asks_prices: list` (Arrays ordenados com os níveis de preço ativos)
* `+ pegged_bids: dict` / `+ pegged_asks: dict` (Rastreamento rápido das Pegged Orders ativas)
* `+ time_counter: int` (Relógio global do sistema para gerar o `seq_id`)

**Métodos:**

* `- _insert_into_price_list(order: Order)` (Método privado que lida com o `bisect` e a Linked List)
* `+ add_limit_order(order_id, side, price, qty)`
* `+ add_pegged_order(order_id, side, peg_type, price, qty)`
* `+ remove_order(order_id: str)`
* `+ update_pegged_orders(peg_type: str, new_price: float)`
* `+ get_order(order_id: str)`
* `+ get_all_positions()`
* `+ get_best_bid() / get_best_ask()`
* `+ get_best_limit_bid_price() / get_best_limit_ask_price()`

---

## 3. Domínio de Regras e Controle (`Core/matching_engine.py` e `Controllers/command_parser.py`)

### `MatchingEngine`

Processa as regras de mercado, os cruzamentos de *spread* e as agressões.
**Atributos:**

* `+ lob: LimitOrderBook` (Referência para o livro de ofertas atual)

**Métodos:**

* `+ process_limit_order(...)`
* `+ process_market_order(...)`
* `+ process_pegged_order(...)`
* `+ process_modify_order(...)`
* `+ process_cancel_order(...)`

### `CommandParser`

A porta de entrada. Recebe *strings* do terminal e traduz em chamadas de método no motor.
**Atributos:**

* `+ engine: MatchingEngine`

**Métodos:**

* `+ process(command: str)` (Lê a string de entrada, valida os tipos de dados e despacha para o método correto do `MatchingEngine`)


## 4. Visualização (`Views/book_printer.py`)

### `BookPrinter`

Desacopla a lógica de impressão da lógica de dados.
**Métodos:**

* `+ print_book(lob: LimitOrderBook)` (Extrai as posições via `get_all_positions()` e formata no terminal)

---

## 5. Diagrama UML (Mermaid)

```mermaid
classDiagram
    %% Relações e Heranças
    Order <|-- LimitOrder
    Order <|-- PeggedOrder
    OrderDoubleLinkedList o-- Order : contém nós
    LimitOrderBook *-- OrderDoubleLinkedList : gerencia filas
    LimitOrderBook *-- Order : mapeia IDs
    MatchingEngine --> LimitOrderBook : altera estado
    CommandParser --> MatchingEngine : envia comandos
    BookPrinter --> LimitOrderBook : lê estado

    %% Definição das Classes
    class Order {
        +String order_id
        +int seq_id
        +String side
        +float price
        +int qty
        +Order prev
        +Order next
        +reduce_qty(amount)
    }

    class LimitOrder {
    }

    class PeggedOrder {
        +String peg_type
    }

    class OrderDoubleLinkedList {
        +Order head
        +Order tail
        +insert_sorted(order)
        +append(order)
        +remove(order)
    }

    class LimitOrderBook {
        +dict orders_map
        +dict bids_dict
        +dict asks_dict
        +list bids_prices
        +list asks_prices
        +dict pegged_bids
        +dict pegged_asks
        +int time_counter
        -_insert_into_price_list(order)
        +add_limit_order(...)
        +add_pegged_order(...)
        +remove_order(order_id)
        +update_pegged_orders(...)
        +get_best_bid()
        +get_all_positions()
    }

    class MatchingEngine {
        +LimitOrderBook lob
        +process_limit_order(...)
        +process_market_order(...)
        +process_pegged_order(...)
        +process_cancel_order(...)
        +process_modify_order(...)
    }

    class CommandParser {
        +MatchingEngine engine
        +process(command)
    }

    class BookPrinter {
        +print_book(lob)
    }