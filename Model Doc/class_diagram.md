# Diagrama de Classes

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
        +get_best_ask()
        +get_best_limit_bid_price()
        +get_best_limit_ask_price()
        +get_best_resting_bid()
        +get_best_resting_ask()
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
        -_parse_print_book()
        -_parse_limit()
        -_parse_market()
        -_parse_peg()
        -_parse_cancel()
        -_parse_modify()
    }

    class BookPrinter {
        +print_book(lob)
    }
    